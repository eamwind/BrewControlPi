import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os
import glob
import time
from RPi import GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.output(16,GPIO.HIGH)
GPIO.output(20,GPIO.HIGH)

if os.environ.get('DISPLAY','') == '':
    #print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')

devices = glob.glob("/sys/bus/w1/devices/" + "28*")
def read_temp(proben, decimals = 1):
    probe = devices[proben] + "/w1_slave"
    with open(probe, "r") as f:
        lines = f.readlines()
    while lines[0].strip()[-3:] != "YES":
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find("t=")
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        tempc = round(float(temp_string) / 1000.0, decimals)
        tempf = round(9/5000.0*float(temp_string) + 32, decimals)
    return(tempc, tempf)

def increase_wattage():
    GPIO.output(16,GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(16,GPIO.HIGH)

def decrease_wattage():
    GPIO.output(20,GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(20,GPIO.HIGH)
'''
def read_temp(proben, decimals = 1):
    return(100.0,212.0)

def increase_wattage():
    time.sleep(0.5)

def decrease_wattage():
    time.sleep(0.5)
'''

# Sets the appearance of the window
# Supported modes : Light, Dark, System
# "System" sets the appearance mode to 
# the appearance mode of the system
ctk.set_appearance_mode("Dark") 

# Sets the color of the widgets in the window
# Supported themes : green, dark-blue, blue 
ctk.set_default_color_theme("blue") 

# Dimensions of the window
appWidth, appHeight = 480, 320
wattage = 3
wattages = [500,700,1000,1200,1400,1600,1800,2000,2300,2600,3000,3200,3500]
temp_range = 5
is_on = False
img_on = 'o'
img_off = 'f'
hogval = 0
celsius = False
phpfile = '/var/www/html/temps.txt'
temphistory = '/home/pi/temphistory.txt'

# Custom widget for the numpad input
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


# App Class
class App(ctk.CTk):
    def getCurTemp(self, unitc):
        #global temp
        temp = read_temp(0,)
        if unitc == True:
            return(temp[0])
        else:
            return(temp[1])

    def change_wattage(self,v):
        global wattage
        global wattages
        if v == -1 and wattage > 0:
            wattage +=v
            decrease_wattage()
        if v == 1 and wattage < (len(wattages)-1):
            wattage +=v
            increase_wattage()

    def nupdate(self):
        global temp_range
        global wattages
        global hogval
        global celsius
        global phpfile
        global temphistory

        # Update temperature
        set_temp = self.setTempVal.get()
        current_temp = self.getCurTemp(celsius)
        if celsius == True:
            self.curTempVal.configure(text=str(current_temp)+"°C" )
        else:
            self.curTempVal.configure(text=str(current_temp)+"°F" )

        # Write current temperatures to history file
        histvalues = '\n'+str(time.gmtime()) + ', ' + str(set_temp) +', '+str(current_temp)
        out = open(temphistory, "a")
        out.write(histvalues)
        out.close()

        #Check php file for web updates
        inp = open(phpfile, 'r')
        phpcur, phpset, recentset = inp.read().splitlines()
        phpcur = float(phpcur)
        phpset = float(phpset)
        if recentset == 'web':
            set_temp = phpset
            self.setTempVal.set(set_temp)
        inp.close()
        inp = open(phpfile, 'w')
        inp.write((str(current_temp)+'\n'+str(set_temp)+'\n'+'local'))
        inp.close()


        # Check if it needs to change output
        if is_on == True:
            if current_temp < set_temp - (temp_range/2):
                hogval+=1
                if hogval > 1:
                    self.change_wattage(1)
                    hogval = 0
            elif current_temp > set_temp + (temp_range/2):
                hogval-=1
                if hogval < -1:
                    self.change_wattage(-1)
                    hogval = 0
            self.curWattVal.configure(text = str(wattages[wattage]))
        #else:
        #   self.curWattVal.configure(text = '0')

        self.after(1000, self.nupdate)
        
    # The layout of the window will be written
    # in the init function itself
    def __init__(self, *args, **kwargs):
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
        self.curWattVal = ctk.CTkLabel(self, text=str(wattages[wattage]), font = ('Arial', 48))
        self.curWattVal.grid(row=0, column=2, padx=20, pady=10, sticky="ew")

        # Exit button
        self.exitButton = ctk.CTkButton(self, text= 'EXIT', fg_color="Grey", width = 100, 
                                        height=70, font = ('Arial', 36), command = self.destroy)
        self.exitButton.grid(row=2, column=2,padx=20,pady=10)

        self.nupdate()

# Setting up for automation switch
# Define our switch function
def switch():
    global is_on
    global img_on
    global img_off
    global app

    # Determine is on or off
    if is_on:
        app.on_button.configure(image = img_off, fg_color="Red")
        is_on = False
    else:
        app.on_button.configure(image = img_on, fg_color="Green")
        is_on = True

if __name__ == "__main__":
    #Overwrite temphistory and temps file
    nf = open(temphistory,'w')
    nf.close()
    nfi = open(phpfile, 'w')
    nfi.write('70.0\n70.0\nlocal')
    nfi.close()

    #Initialize app
    app = App()

    #Grab images
    img_on = ctk.CTkImage(Image.open("on.png"), size=(75, 30))
    img_off = ctk.CTkImage(Image.open("off.png"), size=(75, 30))

    # On/Off Button
    app.on_button = ctk.CTkButton(app, text= '', image = img_off, command = switch, width = 100, height = 70, fg_color="Red", hover = False)
    app.on_button.grid(row=1, column=2, padx=20, pady=10, sticky="ew")

    # Runs the app
    app.wm_attributes('-fullscreen', True)
    app.mainloop()

'''
def initializeit():
    global img_on
    global img_off
    global app
    
    app = App()

    #Grab images
    img_on = ctk.CTkImage(Image.open("on.png"), size=(75, 30))
    img_off = ctk.CTkImage(Image.open("off.png"), size=(75, 30))

    # On/Off Button
    app.on_button = ctk.CTkButton(app, text= '', image = img_off, command = switch, width = 100, height = 70, fg_color="Red", hover = False)
    app.on_button.grid(row=1, column=2, padx=20, pady=10, sticky="ew")

    # Runs the app
    app.wm_attributes('-fullscreen', True)
    app.mainloop()

if __name__ == "__main__":
    #time.sleep(15)
    while True:
        try:
            initializeit()
            break
        except Exception as e:
            time.sleep(1)
'''
