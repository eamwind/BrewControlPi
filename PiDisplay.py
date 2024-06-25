import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os
import glob
import time
from RPi import GPIO
from simple_pid import PID
from random import randrange

# Sets the appearance of the window
# Supported modes : Light, Dark, System
# "System" sets the appearance mode to 
# the appearance mode of the system
ctk.set_appearance_mode("Dark") 

# Sets the color of the widgets in the window
# Supported themes : green, dark-blue, blue 
ctk.set_default_color_theme("blue") 

# Set a bunch of variables that might be useful to change
appWidth, appHeight = 480, 320 #window dimensions should be screen dimensions, in pixels
wattage = 3 # which step, in the wattages list, the wattage is set to initially
wattages = [500,700,1000,1200,1400,1600,1800,2000,2300,2600,3000,3200,3500] #list of all wattages to cycle through
tempslist = list(range(140,480,20)) # list of all temperatures to cycle through -- we now use this one
usedlist = wattages
is_on = False # When the application opens, we want it off
celsius = False # Set to true to switch to celsius
phpfile = '/var/www/html/temps.txt' # location of the file which is shared with the webserver
temphistory = 'temphistory.txt' #location of the file that will record the temperature history
increasepin = 16 #pin that runs to the optocoupler which controls the increase button
decreasepin = 20 #pin that runs to the optocoupler which controls the decrease button
sleeptime = 0.15 #how long to sleep when "pressing" the button
setpoint = 150. #the initial setpoint
global heater
tempproben = 0 #which probe number you have set, just in case you have multiple probes connected to the one pin
pid_values = [2,0,0.01] #proportional, integral and derivative values for PID tuning, look up a guide on PID tuning and change these

#Grab images
img_on = ctk.CTkImage(Image.open("on.png"), size=(75, 30))
img_off = ctk.CTkImage(Image.open("off.png"), size=(75, 30))

# Important for using my display
if os.environ.get('DISPLAY','') == '':
    os.environ.__setitem__('DISPLAY', ':0.0')

    
# simplifies interacting with heater
class Heater:
    def __init__(self, celsius, increasepin, decreasepin, curwatt, probe, PIDv, setpoint):
        #Setup basic values
        self.unitc = celsius
        self.incpin = increasepin
        self.decpin = decreasepin
        self.watt = curwatt
        self.P = PIDv[0]
        self.I = PIDv[1]
        self.D = PIDv[2]
        self.setpoint=setpoint

        #Setup temperature probe
        self.probe = probe
        devices = glob.glob("/sys/bus/w1/devices/" + "28*")
        self.probef = devices[self.probe] + "/w1_slave"
        self.temp = self.read_temp()
        
        #Setup GPIO pins for controlling the buttons
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(increasepin, GPIO.OUT)
        GPIO.output(increasepin,GPIO.HIGH)
        GPIO.setup(decreasepin, GPIO.OUT)
        GPIO.output(decreasepin,GPIO.HIGH)


    def read_temp_raw(self,device_file):
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp(self, decimals = 1):
        lines = self.read_temp_raw(self.probef)
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw(self.probef)
        equals_pos = lines[1].find("t=")
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            tempc = round(float(temp_string) / 1000.0, decimals)
            tempf = round(9/5000.0*float(temp_string) + 32, decimals)
        if self.unitc == True:
            self.temp=tempc
        else:
            self.temp=tempf
        return(self.temp)

    def step_wattage(self,up):
        if up == True:
            pin = increasepin
        else:
            pin = decreasepin
        GPIO.output(pin,GPIO.LOW)
        time.sleep(sleeptime)
        GPIO.output(pin,GPIO.HIGH)

    def set_wattage(self, newwattage):
        move = round(newwattage - self.watt)
        if move == 0:
            return
        moveup = False
        if move > 0:
            moveup = True
        for i in range(abs(move)):
            self.step_wattage(moveup)
            time.sleep(sleeptime)
        self.watt = newwattage

    def update(self,):
        self.temp = self.read_temp()
        pid = PID(self.P, self.I, self.D, setpoint=self.setpoint)
        pid.output_limits = (0, (len(usedlist)-1))
        power = round(pid(self.temp))
        heater.set_wattage(power)

        

# Custom widget for the numpad input and target temperature
class TempNumpad(ctk.CTkFrame):
    def __init__(self, *args, width: int = 70, height: int = 70, step_size=1, command: callable = None, **kwargs):
        super().__init__(*args, width=5, height=5, **kwargs)

        self.configure(fg_color=("gray78", "gray28"))  # set frame color
        self.command = command
        self.step_size = step_size

        self.entry = ctk.CTkEntry(self, width=width*3/7, height=height/7, border_width=0, font=('Arial', int(height/5)))
        self.entry.grid(row=0, column=1, columnspan=3, padx=3, pady=3, sticky="ew")
        
        self.subtract_button = ctk.CTkButton(self, text="-", width=width/7, height=height/4, command=self.subtract_button_callback)
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.add_button = ctk.CTkButton(self, text="+", width=width/7, height=height/4, command=self.add_button_callback)
        self.add_button.grid(row=0, column=4, padx=(0, 3), pady=3)

        self.one = ctk.CTkButton(self,text="1", width=width/7, height=height/7, command = lambda: (self.inputnum(1)))
        self.one.grid(row=1, column=0, padx=(3,0), pady=3)

        self.two = ctk.CTkButton(self,text="2", width=width/7, height=height/7,command = lambda: (self.inputnum(2)))
        self.two.grid(row=1, column=1, padx=3, pady=3)

        self.three = ctk.CTkButton(self,text="3", width=width/7, height=height/7,command = lambda: (self.inputnum(3)))
        self.three.grid(row=1, column=2, padx=3, pady=3)

        self.four = ctk.CTkButton(self,text="4", width=width/7, height=height/7,command = lambda: (self.inputnum(4)))
        self.four.grid(row=1, column=3, padx=3, pady=3)

        self.five = ctk.CTkButton(self,text="5", width=width/7, height=height/7,command = lambda: (self.inputnum(5)))
        self.five.grid(row=1, column=4, padx=3, pady=3)

        self.six = ctk.CTkButton(self,text="6", width=width/7, height=height/7,command = lambda: (self.inputnum(6)))
        self.six.grid(row=2, column=0, padx=3, pady=3)

        self.seven = ctk.CTkButton(self,text="7", width=width/7, height=height/7,command = lambda: (self.inputnum(7)))
        self.seven.grid(row=2, column=1, padx=3, pady=3)

        self.eight = ctk.CTkButton(self,text="8", width=width/7, height=height/7,command = lambda: (self.inputnum(8)))
        self.eight.grid(row=2, column=2, padx=3, pady=3)

        self.nine = ctk.CTkButton(self,text="9", width=width/7, height=height/7,command = lambda: (self.inputnum(9)))
        self.nine.grid(row=2, column=3, padx=3, pady=3)

        self.zero = ctk.CTkButton(self,text="0", width=width/7, height=height/7,command = lambda: (self.inputnum(0)))
        self.zero.grid(row=2, column=4, padx=3, pady=3)

        self.dot = ctk.CTkButton(self,text=".", width=width/7, height=height/7,command = lambda: (self.inputnum(".")))
        self.dot.grid(row=3, column=0, padx=3, pady=3)

        self.backspacebutton = ctk.CTkButton(self,text="<-", width=width*2/7, height=height/7,command = self.back_space)
        self.backspacebutton.grid(row=3, column=1, columnspan = 2, padx=3, pady=3)

        self.clearbutton = ctk.CTkButton(self,text="clear",width=width*2/7, height=height/7, command = lambda: (self.entry.delete(0,"end")))
        self.clearbutton.grid(row=3, column=3, columnspan = 2, padx=3, pady=3)

        self.entry.insert(150, "150")

    def inputnum(self,v):
        if self.command is not None:
            self.command()
        try:
            svalue = str(self.entry.get())+str(v)
            self.entry.delete(0, "end")
            self.entry.insert(0, svalue)
        except ValueError:
            return
        
    def back_space(self):
        if self.command is not None:
            self.command()
        try:
            value = str(self.entry.get())[:-1]
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            self.entry.delete(0, "end")
            self.entry.insert(0, 0.0)
        
    def add_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = float(self.entry.get()) + self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return

    def subtract_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = float(self.entry.get()) - self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return

    def get(self) -> float:
        try:
            return float(self.entry.get())
        except ValueError:
            return (float(150.))

    def set(self, value: float):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(float(value)))

# Whole app class
class App(ctk.CTk):
    def switch_off(self):
        global is_on
        global img_on
        global img_off
        self.on_button.configure(image = img_off, fg_color="Red")
        is_on = False

    def switch_on(self):
        global is_on
        global img_on
        global img_off
        self.on_button.configure(image = img_on, fg_color="Green")
        is_on = True

    # The layout of the window will be written
    # in the init function itself
    def __init__(self, *args, **kwargs):
        global heater

        super().__init__(*args, **kwargs)

        # Sets the title of the window
        self.title("GUI Application") 
        self.geometry(f"{appWidth}x{appHeight}") 

        # Current Temperature Label
        #self.curTempLabel = ctk.CTkLabel(self, text="Current (C)")
        #self.curTempLabel.grid(row=0, column=0,	padx=1, pady=5, sticky="ew")

        # Current Temperature Field
        self.curTempVal = ctk.CTkLabel(self, text=str("60°C"), font = ('Arial',72))
        self.curTempVal.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        # Set Temperature Label
        #self.setTempLabel = ctk.CTkLabel(self, text="Target (C)")
        #self.setTempLabel.grid(row=1, column=0, padx=1, pady=5, sticky="ew")

        # Set Temperature Spinbox
        self.setTempVal = TempNumpad(self, width=380, height=260)
        self.setTempVal.grid(row=1, column=0, rowspan=2, padx=20, pady=10, sticky="ew")

        # Wattage Entry
        self.curWattVal = ctk.CTkLabel(self, text=str(usedlist[wattage]), font = ('Arial', 48))
        self.curWattVal.grid(row=0, column=2, padx=20, pady=10, sticky="ew")

        # Exit button
        self.exitButton = ctk.CTkButton(self, text= 'EXIT', fg_color="Grey", width = 100, 
                                        height=70, font = ('Arial', 36), command = self.destroy)
        self.exitButton.grid(row=2, column=2,padx=20,pady=10)

        # Setting up for on/off switch
        def switch():
            global is_on
            if is_on:
                self.switch_off()
            else:
                self.switch_on()

        # On/Off Button
        self.on_button = ctk.CTkButton(self, text= '', image = img_off, command = switch, width = 100, height = 70, fg_color="Red", hover = False)
        self.on_button.grid(row=1, column=2, padx=20, pady=10, sticky="ew")
        
        heater=Heater(celsius,increasepin,decreasepin,wattage,tempproben,pid_values,150)
        self.nupdate()

    def nupdate(self):
        global wattages
        global celsius
        global phpfile
        global temphistory
        global heater
        global is_on

        # Update temperature
        set_temp = self.setTempVal.get()
        heater.read_temp()
        current_temp = heater.temp
        if celsius == True:
            self.curTempVal.configure(text=str(current_temp)+"°C" )
        else:
            self.curTempVal.configure(text=str(current_temp)+"°F" )

        # Write current temperatures to history file
        histvalues = '\n'+str(time.asctime()) + ', ' + str(set_temp) +', '+str(current_temp)
        out = open(temphistory, "a")
        out.write(histvalues)
        out.close()

        #Check php file for web updates
        inp = open(phpfile, 'r')
        phpcur, phpset, recentset, unitc, phpon = inp.read().splitlines()
        try:
            phpset = float(phpset)
        except:
            pass
        else:
            if recentset == 'web':
                set_temp = phpset
                self.setTempVal.set(set_temp)
                if phpon == "True":
                    self.switch_on()
                else:
                    self.switch_off()
        inp.close()
        inp = open(phpfile, 'w')
        inp.write((str(current_temp)+'\n'+str(set_temp)+'\nlocal\n'+str(celsius)+'\n'+str(is_on)))
        inp.close()

        heater.setpoint = set_temp

        if is_on == True:
            heater.update()
            self.curWattVal.configure(text=str(usedlist[heater.watt]))

        self.after(1000, self.nupdate)

# Main
if __name__ == "__main__":
    #Overwrite temphistory and temps file
    nf = open(temphistory,'w')
    nf.write('Time, Target Temperature, Current Temperature')
    nf.close()
    nfi = open(phpfile, 'w')
    nfi.write('70.0\n70.0\nlocal\n'+str(celsius)+'\n'+str(is_on))
    nfi.close()

    #Initialize app
    app = App()
    app.wm_attributes('-fullscreen', True)
    app.mainloop()
