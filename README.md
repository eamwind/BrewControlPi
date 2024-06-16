# BrewControlPi
## Introduction
I have an Avantco IC3500 induction heater, a Raspberry Pi 3b with a 3.5 inch touchscreen, and a set of DS1820 Temperature Sensors. I used to use [CraftBeerPi](http://web.craftbeerpi.com/ttps://www.google.com) with that setup, which is a good resource and worked well with the heating element approach. However, I downsized my brewing setup and went to induction because it's cool technology. 
After reading through [these plans](https://www.homebrewtalk.com/threads/will-this-cheap-3500-watt-induction-burner-work.301722/page-23#post-7907790) I decided to give it a shot. I already had the Raspberry Pi sitting around with the screen so I gave it a shot. I picked up an optocoupler board to control the (+) and (-) buttons on the induction heater.
I'm an amateur at everything that is happening but I wanted to provide my code and document my work here!

## "Modding" the induction heater
Install a set of wires on the (+) and (-) buttons. This is also done [here.](https://www.homebrewtalk.com/threads/will-this-cheap-3500-watt-induction-burner-work.301722/page-23#post-7907790)

![BottomScrews](https://github.com/eamwind/BrewControlPi/assets/172992640/a5c21314-e17a-40d9-aae4-1db99e831fe4)

Remove the screws here. There's a cable connecting the interface board with the rest of the machine, so you can carefully lift off the bottom and place it on the side or you can disconnect the cable.

![PXL_20240616_170152239](https://github.com/eamwind/BrewControlPi/assets/172992640/5c2ee3c2-1afa-4798-8add-4135bf9f21aa)

Now you can solder three wires, one for each button and one for the neutral.  It's a really good idea to be careful here and don't short the board. Check circuit continuity and the function of the buttons with a multimeter.

## Hardware wiring
Wiring the Raspberry Pi requires some creative work assuming you're also using the 3.5" LCD screen. You need the 5v, 3.3v, ground, and 3 data pins. I used pins 36, 38, and 40, or GPIO 16,20, and 21. I'll be using their GPIO numbers. GPIO 16 is for the (+) button, GPIO 20 is for the (-) button, and GPIO 21 is for the DS1820 temperature sensor.
I recommend going through [someone else's wiring tutorial](https://www.circuitbasics.com/raspberry-pi-ds18b20-temperature-sensor-tutorial/) for the temperature sensor. There are good ones on the internet, and you can test your sensors first. 
I connected 3.3V, ground and GPIO 21 to the correct wires on the temperature sensors.
As for controlling the buttons, I used a board with two optocouplers on it for simplicity. The couplers are JQC-3FF-S-Z. Importantly they are 5v controllable. 

![Screenshot 2024-06-16 124010](https://github.com/eamwind/BrewControlPi/assets/172992640/798b10cf-4df5-4696-91bd-3ed12bb21ac0)

Wiring this up, 3.3V to VCC, ground to ground, GPIO 16 and 20 to IN1 and IN2, and 5V to JD-VCC. You need to remove the jumper on JD-VCC. There are some really good wiring diagrams and instructions on using these optocouplers online that I recommend getting into. 

## Software
I started with unmodified Rasbpian flashed to an SD card, and then started in on it. 
I am 100% missing some parts but I don't want to go through it again to remember. First, [I set up the DS1820 sensors via software](https://www.circuitbasics.com/raspberry-pi-ds18b20-temperature-sensor-tutorial/). Then I installed python 3, lighttpd with fastcgi-mod, and php 7.4. Installing from the command line on the raspberry pi 

'''bash
sudo apt install python3 idle3 php7.4 php7.4-fpm lighttpd
lighttpd-enable-mod fastcgi
'''

I may be missing some required stuff here.
Probably best to reboot at this point, but you can also do

'''bash
sudo lighttpd force-reload
'''


