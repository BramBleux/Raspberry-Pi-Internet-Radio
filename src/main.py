# Start web client: sudo ./src/ympd --webport 80

###############################################################################
#				IMPORTING LIBRARIES	
###############################################################################
import time
import busio
import digitalio
import board
import adafruit_pcd8544
from adafruit_bus_device.spi_device import SPIDevice
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import os
import RPi.GPIO as GPIO
import time
from time import sleep
import subprocess

###############################################################################
#				INITIALISATION	
###############################################################################

# Setting pins for stepper motor in a list (Later used)
pins = [14,15,17,18]

# Setting up GPIO Pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(14, GPIO.OUT)     # pin 1 for motor
GPIO.setup(15, GPIO.OUT)     # pin 2 for motor
GPIO.setup(17, GPIO.OUT)     # pin 3 for motor
GPIO.setup(18, GPIO.OUT)     # pin 4 for motor

# Initialize SPI bus
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialize control pins for adc
cs0 = digitalio.DigitalInOut(board.CE0)  # chip select
adc = SPIDevice(spi, cs0, baudrate= 1000000)

# Initialize display
dc = digitalio.DigitalInOut(board.D23)  # data/command
cs1 = digitalio.DigitalInOut(board.CE1)  # chip select CE1 for display
reset = digitalio.DigitalInOut(board.D24)  # reset
display = adafruit_pcd8544.PCD8544(spi, dc, cs1, reset, baudrate=1000000)
display.bias = 4
display.contrast = 60
display.invert = True

#  Clear the display.  Always call show after changing pixels to make the display update visible!
display.fill(0)
display.show()

# Load default font.
font = ImageFont.load_default()

# Get drawing object to draw on image
image = Image.new('1', (display.width, display.height))
draw = ImageDraw.Draw(image)


###############################################################################
#				FUNCTIONS	
###############################################################################

# read SPI data 8 possible adc's (0 thru 7) 
def readadc(adcnum): 
	if ((adcnum > 7) or (adcnum < 0)): 
		return -1 
	with adc:
		r = bytearray(3)
		spi.write_readinto([1,(8+adcnum)<<4,0], r)
		time.sleep(0.000005)
		adcout = ((r[1]&3) << 8) + r[2] 
		return adcout 


# Making playlist from any file 
def making_playlsit():
	with open('./src/playlist/playlist_17.txt') as playlist:      # Fill in a file you want
		os.system("mpc clear")
		number_of_stations = 0
		station = playlist.readline().rstrip()
		while station:
			number_of_stations += 1
			os.system("mpc add " + str(station))
			station = playlist.readline().rstrip()

	os.system("mpc playlist")
	print(f"{'-' * 28}\n Playlist successfully made\n{'-' * 28}")
	return number_of_stations


# Returning the number of the station currently playing
def search_station():
    status = os.popen("mpc status")
    station_number = ""
    for i in status.readlines():
        for j in range(len(i)):
            if i[j] == "#":
                station_number += i[j + 1: j + 3]
                break
    
    # if number is lower than 10, the "/" is removed
    # if the number is higher than 10, the "/" will be the second digit of the number
    if (station_number[1] == "/"):
        station_number = station_number[0]
    
    return int(station_number)


def volume_adjustment():
    # Reading pot meter 
	ch0 = readadc(0) 

    # Calculating volume (in percent)
	volume_percent = abs(int(((ch0 / 1023) * 100) - 100)) 

    # Adjusting the volume
	os.system("mpc volume " + str(volume_percent)) 

	return volume_percent


# Rotating the stepper motor clockwise
def rotate_right(numberOfCycles):
    halfstep_seq = [
        [1,0,0,0],
        [1,1,0,0],
        [0,1,0,0],
        [0,1,1,0],
        [0,0,1,0],
        [0,0,1,1],
        [0,0,0,1],
        [1,0,0,1]
    ]

    for i in range(numberOfCycles):
        for halfstep in range(8):
            for pin in range(4):
                GPIO.output(pins[pin], halfstep_seq[halfstep][pin])
            time.sleep(0.004)
    


# Rotating the stepper motor counter-clockwise
def rotate_left(numberOfCycles):
    halfstep_seq = [
        [1,0,0,0],
        [1,1,0,0],
        [0,1,0,0],
        [0,1,1,0],
        [0,0,1,0],
        [0,0,1,1],
        [0,0,0,1],
        [1,0,0,1]
    ]

    for i in range(numberOfCycles):
        for halfstep in range(0, -8, -1):
            for pin in range(4):
                GPIO.output(pins[pin], halfstep_seq[halfstep][pin])
            time.sleep(0.004)

	


def LcdAdjust(volume):

    # Reading the name of the station currently playing
    f = os.popen("mpc current")
    station_full = " "
    for i in f.readlines():
        station_full += i
    
    parts = station_full.split("|")
    current_station = parts[0].rstrip()

    # Getting the IP address of the Pi
    IP = subprocess.check_output(["hostname", "-I"]).split()[0]

    # Print current station on first line of the LCD
    draw.text((1, 0), f"{current_station[1:]}", font=font)
    
    # Print the volume on the second line of the LCD
    draw.text((1, 8), f"Volume: {volume}%", font=font)

    # Print IP-address on the third line of the LCD
    draw.text((1,16), str(IP)[2:-1], font=font)

    # Pre-coded logo per station on the last two lines of the LCD
    if (current_station[1:8] == "Radio 1"):
        draw.text((1, 24), "|>  /\  /|", font=font)
        draw.text((1, 32), "|\ /--\ _|_", font=font)

    elif (current_station[1:] == "Radio 2 ANT"):
        draw.text((1, 24), "|) /\ |\ |___", font=font)
        draw.text((1, 32), "|\/--\| \| | ", font=font)

    elif (current_station[1:8] == "Radio 2"):
        draw.text((1, 24), "|>  /\  ||", font=font)
        draw.text((1, 32), "|\ /--\ ||", font=font) 

    elif (current_station[1:15] == "Studio Brussel") or (current_station[1:7] == "StuBru"):
        draw.text((1, 24), "|) |) | |", font=font)
        draw.text((1, 32), "|) |\ |_|", font=font)

    elif (current_station[1:6] == "Klara"):
        draw.text((1, 24), "|/ |    /\ ", font=font)
        draw.text((1, 32), "|\ |__ /--\ ", font=font)

    elif (current_station[1:4] == "MNM"):
        draw.text((1, 24), "|\/| |\ | |\/|", font=font)
        draw.text((1, 32), "|  | | \| |  |", font=font)
    

    # Displaying everything on the LCD screen
    display.image(image)
    display.show()
    draw.rectangle((0, 0, display.width, display.height), outline=255, fill=255)


###############################################################################
#				MAIN PROGRAM	
###############################################################################
try:
	# Making the playlist and putting the number of stations in a variable
    number_of_stations = making_playlsit()

	# Defining the amount of cycles the motor has to turn to go to the next station
    number_of_cycles = int(512 // number_of_stations)

	# starting the radio
    os.system("mpc play")

	# Setting up the volume
    volume_adjustment()

    # Initialising current station nr
    current_station_number = search_station()
    
    # Initialising switching variable
    switch = True

    # Reading the value of the potentiometer for the volume
    raw_volume = readadc(0)

    while True:
        # Adjusting the volume
        current_volume = volume_adjustment()
		
		# Station switch machanism
        ch1 = readadc(1)
		
        if (ch1 < 300) and switch:
            rotate_right(number_of_cycles)
            os.system("mpc next")
            switch = False

        elif ((ch1 > 800) and switch):
            rotate_left(number_of_cycles)
            os.system("mpc prev")
            switch = False


        # For motor when whebinterface changes station
        elif current_station_number != search_station():
            difference = search_station() - current_station_number

            if (difference > 0):
                rotate_right(number_of_cycles * difference)
            else:
                rotate_left(number_of_cycles * abs(difference))
                print(abs(difference))
            
	
        elif (400 <= ch1 <= 600):
            switch = True

        # Refreshing station number
        current_station_number = search_station()

        # Adjusting the LCD screen
        LcdAdjust(current_volume)

    GPIO.cleanup()


# When CTRL + C is pressed (Stopping the program)
except KeyboardInterrupt:
    # Resetting the motor to the start position
    if ((current_station_number - .5) > (number_of_stations / 2)):
        rotate_right(number_of_cycles * (number_of_stations - current_station_number + 1))
    else:
        rotate_left(number_of_cycles * (number_of_stations - (number_of_stations - current_station_number) - 1))

    # Clearing the LCD screen
    display.fill(0)
    display.show()

    # Cleaning the GPIO pins
    GPIO.cleanup()

    os.system("mpc stop")  # Stop playing
    
    # Display in the terminal the radio stopped playing
    print("-" * 9 + "\nRadio Off\n" + "-" * 9)
