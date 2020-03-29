"""
title:   Big 7 segment driver
author:  Dieter Vanderfaeillie
license: GPL attribution share alike
"""

import time
import orangepi.zeroplus2
from OPi import GPIO
GPIO.setmode(orangepi.zeroplus2.BOARD)
GPIO.setwarnings(True)

verbose = True
# pin defs
not_oe = 13     # output enable GPIO 0
clk = 22        # clock		GPIO 2
le = 3          # latch		GPIO 12
sdo = 26        # data out	GPIO 10

btn = 18     	# button pin 	GPIO 18
GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# define which segments are on/off for each digit
# 4th is for the point
letters = {
    ' ': [0, 0, 0, 0, 0, 0, 0, 0],
    '.': [0, 0, 0, 1, 0, 0, 0 ,0],
    '0': [1, 1, 1, 0, 1, 1, 1, 0],
    '1': [1, 0, 0, 0, 1, 0, 0, 0],
    '2': [0, 1, 1, 0, 1, 1, 0, 1],
    '3': [1, 1, 0, 0, 1, 1, 0, 1],
    '4': [1, 0, 0, 0, 1, 0, 1, 1],
    '5': [1, 1, 0, 0, 0, 1, 1, 1],
    '6': [1, 1, 1, 0, 0, 1, 1, 1],
    '7': [1, 0, 0, 0, 1, 1, 0, 0],
    '8': [1, 1, 1, 0, 1, 1, 1, 1],
    '9': [1, 1, 0, 0, 1, 1, 1, 1],
    'P': [0, 0, 1, 0, 1, 1, 1, 1],
    'A': [1, 0, 1, 0, 1, 1, 1, 1],
    'B': [1, 1, 1, 0, 1, 1, 1, 1],
    'C': [0, 1, 1, 0, 0, 1, 1, 0]
}


class Driver:
    def __init__(self):
        GPIO.setup(not_oe, GPIO.OUT)
        GPIO.setup(le, GPIO.OUT)
        GPIO.setup(clk, GPIO.OUT)
        GPIO.setup(sdo, GPIO.OUT)

        # reset any previous message
        self.update('    ')
        # turn off leds
        GPIO.output(not_oe, True)
        # turn off latch
        GPIO.output(le, False)
        # clock starts low
        GPIO.output(clk, False)

        # not yet available in OPi.GPIO (?)
        # freq = 200 #hz
        # self.pwm = GPIO.PWM(not_oe, freq)
        # lights off to start with
        # self.pwm.start(100) #duty cycle

    # sends a string representation of a float, deals with floating points
    def update(self, number):
        point = False
        
        # send digits
        for char in number:
            if char == '.':
                point = True
                continue
            self.send_digit(char, point)
            point = False

        # latch the outputs
        GPIO.output(le, True)
        GPIO.output(le, False)

    # send a char, with optional point
    def send_digit(self, char, point = False):
        # set the point bit
        if point:
            letters[char][3] = 1
        else:
            letters[char][3] = 0

        if verbose:
            print("sending %s = %s" % (
                char,
                ','.join(str(x) for x in letters[char]))
            )

        # 8 clock pulses
        for i in range(8):
            GPIO.output(clk, False)
            # data
            if letters[char][7 - i]:
                GPIO.output(sdo, True)
            else:
                GPIO.output(sdo, False)

            GPIO.output(clk, True)

    # turn off leds
    def turn_off(self):
        GPIO.output(not_oe, False)

    # turn on leds
    def turn_on(self):
        GPIO.output(not_oe, True)

    def cleanup(self):
        self.turn_off()
        GPIO.cleanup()

class Timer:
    def __init__(self):
        self.time_start = time.time()
        self.seconds = 0
        self.minutes = 0
        self.indicator = False
    
    def update(self):
        seconds_passed = int(time.time() - self.time_start) - self.minutes * 60
        self.minutes += seconds_passed // 60
        if (seconds_passed % 60) != self.seconds:
            self.indicator = not(self.indicator)
        self.seconds = seconds_passed % 60
    
    def reset(self):
        self.time_start = time.time()
        self.seconds = 0
        self.minutes = 0
        self.indicator = False
    
    def get_string(self):
        string = "{:02d}".format(self.minutes)
        if self.indicator:
            string += "."
        string += "{:02d}".format(self.seconds)
        if verbose:
            print('time:', string)
        return string


# run main
if __name__ == '__main__':
    time_start = time.time()
    seconds = 0
    minutes = 0
    flag = True
    driver = Driver()
    timer = Timer()

    try:
        print("Press CTRL+C to exit")
        while True:
            #button_state = True
            #if button_state == False:   # btn was pressed, (re)start timer
            #    flag += not(button_state)
            #    timer.reset()

            if flag : timer.update()
            timer_representation = timer.get_string()
            if verbose : print(timer_representation)
            driver.update(timer_representation)
            time.sleep(0.1)

    except KeyboardInterrupt:
        driver.cleanup()
        print("Bye")

