# BrewControlPi
## Introduction
I have an Avantco IC3500 induction heater, a Raspberry Pi 3b with a 3.5 inch touchscreen, and a set of DS1820 Temperature Sensors. I used to use [CraftBeerPi](http://web.craftbeerpi.com/ttps://www.google.com) with that setup, which is a good resource and worked well with the heating element approach. However, I downsized my brewing setup and went to induction because it's cool technology. 
After reading through [these plans](https://www.homebrewtalk.com/threads/will-this-cheap-3500-watt-induction-burner-work.301722/page-23#post-7907790) I decided to give it a shot. I already had the Raspberry Pi sitting around with the screen so I gave it a shot. 
I'm an amateur at everything that is happening but I wanted to provide my code and document my work here!

## "Modding" the induction plate
This part's easy! You want to install a set of wires on the (+) and (-) buttons. This is also done [here](https://www.homebrewtalk.com/threads/will-this-cheap-3500-watt-induction-burner-work.301722/page-23#post-7907790)

![BottomScrews](https://github.com/eamwind/BrewControlPi/assets/172992640/a5c21314-e17a-40d9-aae4-1db99e831fe4)
Remove the screws here. There's a cable connecting the interface board with the rest of the machine, so you can carefully lift off the bottom and place it on the side or you can disconnect the cable.

![PXL_20240616_170152239](https://github.com/eamwind/BrewControlPi/assets/172992640/5c2ee3c2-1afa-4798-8add-4135bf9f21aa)
Now you can solder three wires, one for each button and one for the neutral. It's a really good idea to be careful here and don't short the board. Check circuit continuity and the function of the buttons with a multimeter.


