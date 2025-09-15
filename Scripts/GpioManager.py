try:
    import RPi.GPIO as GPIO
    RPI_ENV = True
except ImportError:
    RPI_ENV = False

class GpioManager:
    def __init__(self):
        if RPI_ENV:
            print("Running on Raspberry Pi environment.")
            GPIO.setmode(GPIO.BCM)
        else:
            print("Running in a non-Raspberry Pi environment. GPIO operations will be simulated.")
        self.state = {}

    def setup(self, pin, mode):
        if RPI_ENV:
            gpioMode = GPIO.OUT if mode else GPIO.IN
            GPIO.setup(pin, gpioMode)
        self.state[pin] = False

    def output(self, pin, value):
        if RPI_ENV:
            GPIO.output(pin, value)
        self.state[pin] = value

    def input(self, pin):
        if RPI_ENV:
            return GPIO.input(pin)
        return self.state.get(pin, False)

    def cleanup(self):
        if RPI_ENV:
            GPIO.cleanup()
        self.state.clear()
