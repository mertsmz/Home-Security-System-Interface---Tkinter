import os
import sys
import RPi.GPIO as gpio
from mfrc522 import SimpleMFRC522
import time

CardRead = SimpleMFRC522()

load1 = 11
load2 = 12
load3 = 13

gpio.setmode(gpio.BOARD)
gpio.setwarnings(False)
gpio.setup(load1, gpio.OUT)
gpio.setup(load2, gpio.OUT)
gpio.setup(load3, gpio.OUT)

id = 0


def card_read():
    print('Card Scanning')
    print('for Cancel Press ctrl+c')

    try:
        for index in range(200):
            global id
            id, text = CardRead.read_no_block()#No block ile okuduğumuzda for döngüsündeki döngü sayısı kadar okunmazsa da read işlemi bitiriliyor id=None olarak. Böylece kitlenmiyor sistem kart okuma esnasında.
            print(id)
            print(text)
            if id != None:#Bir kere okunduysa process bitiriliyor, sürenin tamamı beklenmez ve boşa okumalar olmaz.
                break


    except KeyboardInterrupt:
        gpio.cleanup()




