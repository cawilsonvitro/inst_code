# a class to manage an instrument, each intrument will be assigend this 


class instrument():
    '''
    instrument class
    '''
    
    def __init__(self, name, address):
        '''
        constructor
        '''
        self.name = name
        self.address = address
        self.Status = False
    
    def connect(self):
        '''
        connects to instrument
        '''
        # Simulate connection logic
        self.connected = True
        print(f"Connected to {self.name} at {self.address}")
    
    def disconnect(self):
        '''
        disconnects from instrument
        '''
        self.connected = False
        print(f"Disconnected from {self.name}")