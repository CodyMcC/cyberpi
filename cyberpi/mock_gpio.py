class GPIO:
    BCM = 'BCM'
    HIGH = 1
    LOW = 0
    OUT = 'OUT'
    IN = 'IN'

    def __init__(self):
        self.pins = {}


    @classmethod
    def setmode(cls, mode):
        return

    @classmethod
    def setup(cls, pin, mode):
        return
    
    @classmethod
    def output(cls, pin, state):
        return 
    
    @classmethod
    def cleanup(cls):
        return