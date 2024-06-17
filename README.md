# BrewControlPi
## Introduction
I have an Avantco IC3500 induction heater, a Raspberry Pi 3b with a 3.5 inch touchscreen, and a set of DS18B20 Temperature Sensors. I used to use [CraftBeerPi](http://web.craftbeerpi.com/ttps://www.google.com) with that setup, which is a good resource and worked well with the heating element approach. However, I downsized my brewing setup and went to induction because it's cool technology. 
After reading through [these plans](https://www.homebrewtalk.com/threads/will-this-cheap-3500-watt-induction-burner-work.301722/page-23#dspost-7907790) I decided to give it a shot. I already had the Raspberry Pi sitting around with the screen so I gave it a shot. I picked up an optocoupler board to control the (+) and (-) buttons on the induction heater.

This software provides a kiosk like experience on the 3.5 inch touchscreen with a readout for the current temperature and a keyboard onscreen to set the target temperature. This also provides a server where you can interact from local webpages to check and set temperature as well. 

![piscreen](https://github.com/eamwind/BrewControlPi/assets/172992640/25c28860-f623-4287-8b4b-72b90f89dbe8)

The kiosk screen!

![webcap](https://github.com/eamwind/BrewControlPi/assets/172992640/1ffdf709-a671-47ad-9104-0afb8d983718)

Interacting with the web page!

I'm an amateur at everything that is happening but I wanted to provide my code and document my work anyway.

## "Modding" the induction heater
Install a set of wires on the (+) and (-) buttons. This is also done [here.](https://www.homebrewtalk.com/threads/will-this-cheap-3500-watt-induction-burner-work.301722/page-23#post-7907790)

![BottomScrews](https://github.com/eamwind/BrewControlPi/assets/172992640/a5c21314-e17a-40d9-aae4-1db99e831fe4)

Remove the screws here. There's a cable connecting the interface board with the rest of the machine, so you can carefully lift off the bottom and place it on the side or you can disconnect the cable.

![PXL_20240616_170152239](https://github.com/eamwind/BrewControlPi/assets/172992640/5c2ee3c2-1afa-4798-8add-4135bf9f21aa)

Now you can solder three wires, one for each button and one for the neutral.  It's a really good idea to be careful here and don't short the board. Check circuit continuity and the function of the buttons with a multimeter.

## Hardware wiring
Wiring the Raspberry Pi requires some creative work assuming you're also using the 3.5" LCD screen. The screen uses pins 1-26 so you need to share the 5v and 3.3v pins (the first two). I accomplished this with homemade connectors lying flat between the pins and the fat connector. I also 3d printed (and hot glued) a connector for the remaining pins to hold everything together in the little project box.

![PXL_20240617_160620976](https://github.com/eamwind/BrewControlPi/assets/172992640/b2f95a76-7016-42ce-9f3e-3dee77693a55)

This image has the screen removed for clarity.

Honestly if you're buying stuff new, maybe go with a screen that connects through hdmi and usb. 
I recommend going through [someone else's wiring tutorial](https://www.circuitbasics.com/raspberry-pi-DS18B20-temperature-sensor-tutorial/) for the temperature sensor. There are good ones on the internet, and you can test your sensors first. For everything, you need the 5v, 3.3v, ground, and 3 data pins. I used pins 36, 38, and 40, or GPIO 16,20, and 21. I'll be using their GPIO numbers. GPIO 16 is for the (+) button, GPIO 20 is for the (-) button, and GPIO 21 is for the DS18B20 temperature sensor. If you want to use different pins, you can define the button pins in the python script and the temperature sensor pin in /boot/config.txt. I connected 3.3V, ground and GPIO 21 to the correct wires on the temperature sensors.
As for controlling the buttons, I used a board with two optocouplers on it for simplicity. The couplers are JQC-3FF-S-Z. Importantly they are 5v controllable. 

![Screenshot 2024-06-16 124010](https://github.com/eamwind/BrewControlPi/assets/172992640/798b10cf-4df5-4696-91bd-3ed12bb21ac0)

Wiring this up, 3.3V to VCC, ground to ground, GPIO 16 and 20 to IN1 and IN2, and 5V to JD-VCC. You need to remove the jumper on JD-VCC. There are some really good wiring diagrams and instructions on using these optocouplers online that I recommend getting into. 

I added a pair of barrel jacks so I can disconnect the induction plate from the raspberry pi. If you have these kinds of connectors lying around it seems like a good idea to do.

![PXL_20240617_161437483](https://github.com/eamwind/BrewControlPi/assets/172992640/529a91e2-dfd1-4541-9194-f6a926b22faa)


## Software
I started with unmodified Rasbpian flashed to an SD card, and then started in on it. 
I am 100% missing some parts but I don't want to go through it again to remember. First, [I set up the DS18B20 sensors via software](https://www.circuitbasics.com/raspberry-pi-DS18B20-temperature-sensor-tutorial/). Then I installed python 3, lighttpd with fastcgi-mod, and php 7.4. Installing from the command line on the raspberry pi 

```bash
sudo apt install python3 idle3 php7.4 php7.4-fpm lighttpd
lighttpd-enable-mod fastcgi
```

I may be missing some required stuff here...
Probably best to reboot at this point, but you can also do

```bash
sudo lighttpd force-reload
```

Now to set up the actual software!
To use the 3.5" display I bought from AliExpress, I used [this excellent resource.](https://github.com/lcdwiki/LCD-show-ubuntu) Your mileage may vary.
From python, you need customtkinter, tkinter, pillow and RPi. The only odd thing here is [customtkinter.](https://customtkinter.tomschimansky.com/)
The provided index.php should go into /var/www/html and you need to delete the index.html that is in there. 
For the python script and images, I keep it in my /home/pi/ folder, if you want to change these folders you need to change the associated variables in the python script/ php file.
You can always run the script manually off the pi or have it start with boot with systemd or crontab. What ended up working for me, I don't know why it was the only way, but I saved a bash file to the desktop called Startup.sh that just has the line to start the PiDisplay.py script.

```bash
#!/bin/bash
/usr/bin/python3 /home/pi/PiDisplay.py
```

And then having the script called from crontab on startup. So in the terminal

```bash
sudo crontab -e
```

and in the editor put the line 

```
@reboot /bin/bash /home/pi/Desktop/Startup.sh
```

## Use
I chose to only connect to the two buttons, meaning that this interface cannot turn the heater on and off and you have to manually turn the plate on and set it to heat via wattage beforehand. The lowest setting, at 500 watts, it low enough that it seems fine for me. You could run wires for all the buttons, but it didn't seem worth the risk to me. In that case you can easily implement that in the python code, adding more GPIO lanes. 
For the kiosk display: the big number on the top left is the current temperature, the target temperature is on the bottom left with the keypad for changing it. The number on the top right is the current wattage, it should correspond with whats shown on the screen of the induction heater. The on/off button determines whether the control is on/off, not the heat! This means that when you turn it off, the induction heater will just hold the current heat. To turn off the heater turn it down with the button. Finally the chunky exit button is self explanatory.


So this is my experience, remembering that I made this work for my hardware. Hopefully this helps someone else on their project though!



