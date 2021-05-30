# Raspberry Pi internet radio with LCD display and Web-Interface

This radio is able to read a playlist file which contains links up to 99 
internet radiostations and play them in order. 

To controll the radio you are able to turn two different potentiometer to adjust 
the volume and channel. You also could use the web interface to change channels. 
  
**The potentiometer that is used to change channels should works as follows:**  
When the meter is in the middle nothing happens.  
  
When the meter is turned to the right, it will go to the next channel **ONCE**. If you want to go 2 channels further, the meter has to go to the middle before turning it to the right again.
  
When the meter is turned to the left, it will go to the previous channel **ONCE**. If you want to go 2 channels back, the meter has to go to the middle before turning it to the left again.

When you change channels, a stepper motor will indicate which channel is 
currently playing and the LCD display will show you: the station name, the 
volume, the IP address of the web interface (= IP address of the Pi) and a logo if available. (This part is hard coded for some Dutch radio stations)  
  
When the program is stoped (with CTRL + C) The stepper motor will return to its starting position before stopping the radio.
  
To start the radio simply use the command: __*sudo python3 ./src/main.py*__


## Components used:
- Raspberry Pi (4 in my case) 
- MCP 3008
- ULN2003APG
- 28BYJ-48 Stepper Motor
- Potentio Meter X2
- Nokia 5110 LCD Display
- Wires to connect the components
- AUX cable
- Power cable (for the raspberry pi)
- Breadboard
- Speaker (With AUX-IN)
                
  
   
   
## Wiring Scheme:  
  
![Wiring scheme](/img/Wireing_scheme.png)


## Explanation about the playlist files:  

In the playlist files you can paste the links to the internet radios you like to listen to.
I got my links from: [https://www.vrt.be/nl/aanbod/kijk-en-luister/radio-luisteren/streamingslinks-radio](https://www.vrt.be/nl/aanbod/kijk-en-luister/radio-luisteren/streamingslinks-radio/)  
**These are Dutch radio stations!**


## Explanation about the Web-interface:

When you want to use the Web-interface the command __*sudo ./src/ympd --webport 80*__ should be excecuted **In a second terminal!!**  
If the command is not excecuted in a different terminal, the program will NOT work.  
The Web-interface can be used to change channels, but not to change the volume.

## Pictures:

![Preview 1](/img/preview_1.jpg)  
![Preview 2](/img/preview_2.jpg)

