import RPi.GPIO as GPIO

def initialize(Pins):
	# Configures how we are describing our pin numbering
	GPIO.setmode(GPIO.BCM)
	# Desable warnings
	GPIO.setwarnings(False)
	# Set the GPIO pins that are required
	for i in Pins:
		init_output(i)
		set_off(i)
		
def toggle_channel(channel):
	if (channel_active(channel)):
		set_off(channel)
	else:
		set_on(channel)
		
def channel_active(channel):
	return GPIO.input(channel)
	
def init_output(pin):
	GPIO.setup(pin, GPIO.OUT)
	GPIO.output(pin, GPIO.LOW)
	
def set_on(pin):
	GPIO.output(pin, GPIO.HIGH)

def set_off(pin):
	GPIO.output(pin, GPIO.LOW)
	
def cleanup():
	GPIO.cleanup()
	