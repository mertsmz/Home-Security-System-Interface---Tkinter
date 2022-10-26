import RPi.GPIO as gpio
##Door Servo 
gpio.setmode(gpio.BOARD)
gpio.setup(18,gpio.OUT)
servo_door = gpio.PWM(18,50)

gpio.setup(37, gpio.OUT)

#Buzzer
gpio.setmode(gpio.BOARD)
gpio.setup(11, gpio.OUT)