class LED:
    def __init__(self, pin: int):
        self.pin = pin
        self.state = False

    def on(self):
        self.state = True
        print(f"[MOCK] LED on pin {self.pin} turned ON")

    def off(self):
        self.state = False
        print(f"[MOCK] LED on pin {self.pin} turned OFF")