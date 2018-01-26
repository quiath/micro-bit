# created by Tomasz Kwiatkowski
import radio
from microbit import *
 
TIMEOUT = 100
PWRMAX = 7
SLEEP = 100
 
pwr = PWRMAX
MODE_NONE = 0
MODE_SINGLE = 1
MODE_AUTO = 2
 
mode = MODE_NONE
 
sent = -1
 
radio.on()
 
display.show("?")
 
# class to store and display the smoothed power needed to communicate
class Filter:
    def __init__(self):
        self.scale = 100
        self.ratio = 80 # state is 80% old value and 20% new value
        self.acc = (PWRMAX + 1) * self.scale
    def update(self, p):
        self.acc =  ( self.ratio * self.acc +
                      self.scale * p * (self.scale - self.ratio)) // self.scale
        smooth_pwr = self.acc // self.scale
        if smooth_pwr == 0:
            display.show(Image.HAPPY) # close
        elif smooth_pwr >= PWRMAX:
            display.show(Image.NO) # no response
        else:
            display.show(str(smooth_pwr)) # radio power for which comms possible
 
smooth = Filter()
 
while True:
 
    if mode != MODE_NONE:
        t = running_time()
        if sent == -1:
            # set power, send message
            radio.config(power = pwr)
            radio.send("S" + str(pwr))
            sent = t
        else:
            dt = t - sent
            if dt > TIMEOUT:
                # response not received
                if mode == MODE_SINGLE:
                    mode = MODE_NONE
                    if pwr == PWRMAX:
                        display.show(Image.NO)
                    else:
                        display.show(str(pwr + 1))
                else:
                    sent = -1
                    smooth.update(pwr + 1)
 
                sleep(SLEEP)
 
                pwr = PWRMAX
 
        if mode == MODE_AUTO:
            # turn off auto mode on B pressed
            if button_b.was_pressed():
                mode = MODE_NONE
            # blink a pixel in auto mode
            display.set_pixel(0, 0, (t // SLEEP) % 10)
 
    else: # MODE_NONE
        if button_a.was_pressed():
            mode = MODE_SINGLE
            pwr = PWRMAX
            sent = -1
        elif button_b.was_pressed():
            mode = MODE_AUTO
            pwr = PWRMAX
            sent = -1
            smooth = Filter()
 
    # process incoming transmissions
    incoming = radio.receive()
    if incoming:
        if incoming[0] == 'S':
            radio.config(power = PWRMAX)
            radio.send("R" + incoming[1])
            if mode == MODE_NONE:
                # only show when in passive mode
                display.show(Image.TARGET)
        elif incoming[0] == 'R' and mode >= 1 and incoming[1] == str(pwr):
 
            if pwr == 0:
                # received response with low power, other radio is nearby
                if mode == MODE_SINGLE:
                    # in single mode stop the search
                    mode = MODE_NONE
                    display.show(Image.HAPPY)
                else:
                    # in auto mode continue to search
                    smooth.update(pwr)
                    pwr = PWRMAX
                    sent = -1
 
                sleep(SLEEP)
            else:
                if mode == MODE_SINGLE:
                    # temporarily display power while searching
                    display.show(str(pwr))
                # got response, reduce power and try again
                pwr -= 1
                sent = -1

