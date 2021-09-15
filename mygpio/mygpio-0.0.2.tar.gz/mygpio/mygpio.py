import RPi.GPIO as GPIO

OutputPins = [2, 3]

def initialize():
	# Configures how we are describing our pin numbering
	GPIO.setmode(GPIO.BCM)
	# Desable warnings
	GPIO.setwarnings(False)
	# Set the GPIO pins that are required
	
	for i in OutputPins:
		GPIO.setup(i, GPIO.OUT)
		GPIO.setup(i, GPIO.LOW)

def say_hello(name=None):
	if name is None:
		return 'Hello, World!'
	else:
		return f'Hello, {name}!'
