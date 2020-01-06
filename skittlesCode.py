import random
import time
import PySimpleGUI as sg
import hashlib

class encoderDecoder():
    def initialize(self, seed):
        # Enterable characters:
        alpha = "abcdefghijklmnopqrstuvwxyz 0123456789!@#$%^&*()-_=+`~/?.>,<;:'[]{}\"ABCDEFGHIJKLMNOPQRSTUVWXYZ\\|\n"

        # Encoding characters lists to choose from:
        encodingSet = "ABCDEF1234567890"

        # Key is valid for 3600s
        validSec = 3600
        ts = int(time.time())
        ts = int(ts / validSec) * validSec

        seed = int(seed)
        randomSeed = seed * ts
        random.seed(randomSeed)

        # variable length encoding (N must be >= 3)
        self.N = (seed % 3 + 1) * 3
        self.numOptions = random.randint(12,22)

        # Create character strings for encoding - N represents encoding depth based on seed
        ds = []
        chosenKeys = []
        for loop in range(0, self.numOptions):
            encodingKeys = []
            while len(encodingKeys) < len(alpha):
                value = self.convert([random.choice(encodingSet) for y in range(0, self.N)])
                if chosenKeys.count(value) == 0:
                    encodingKeys.append(value)
                    chosenKeys.append(value)
        
            # Each input character can be mapped to 2 possible values
            encodeDict = dict(zip(alpha, encodingKeys))     # alpha -> characters
            ds.append(encodeDict)

        # First the decode, decode the multiple encodingKeys to cooresponding 'alpha' characters
        self.decodeDict = {}
        for loop in range(0, self.numOptions):
            decodeDict = dict(zip(ds[loop].values(), ds[loop].keys()))
            self.decodeDict.update(decodeDict)

        # For encoding encode one 'alpha' key to multiple encoding values
        self.encodeDict = {}
        for k in ds[0].keys():
            self.encodeDict[k] = tuple(self.encodeDict[k] for self.encodeDict in ds)

    def convert(self, s):
        new = ""
        for x in s:
            if x != None:
                new += x
        return new

    def encodeMessage(self, msg):
        msgChar = [x for x in msg]
        encodedMsg = []
        for x in msgChar:
            index = random.randint(0,self.numOptions-1)
            encodedMsg.append(self.encodeDict.get(x)[index])

        return self.convert(encodedMsg) + self.checksum(msg).upper()

    def decodeMessage(self, msg):
        msgSha = msg[-64:].lower()
        msg = msg[0:-64]
        msgChar = [msg[i:i+self.N] for i in range(0, len(msg), self.N)]
        decodedMsg = [self.decodeDict.get(x) for x in msgChar ]

        # Message integrity check
        if msgSha == self.checksum(decodedMsg):
            return self.convert(decodedMsg)
        
        return ''

    def checksum(self, st):
        string = ''.join([str(elem) for elem in st])
        hash_object = hashlib.sha256(string.encode())
        hex_dig = hash_object.hexdigest()
        return hex_dig
#
# Simple GUI setup
#
class GUI():
    sg.theme('DarkBlack')
    layout = [  [sg.Text('Enter Seed:'), sg.InputText(size=(25,1)), 
                    sg.InputCombo(('Encode', 'Decode'), size=(10, 1), default_value='Encode', readonly=True,
                    text_color='Black', background_color='White')],
                [sg.Text('Message:')],
                [sg.Multiline(default_text='', size=(50, 10), key='rawMsg')],
                [sg.Text('Encoded Message:')],
                [sg.Multiline(default_text='', size=(50, 15), key='encodedMsg')],
                [sg.Txt('', size=(40,1), key='status')  ],
                [sg.Button('Execute', size=(10,1)), sg.Button('Close', size=(10,1))] ]

    # Create the Window
    window = sg.Window('Skittles Encoder', layout)

    # Create the encoder/decoder object
    coder = encoderDecoder()

    while True:
        event, values = window.read()
        if event in (None, 'Close'):	# if user closes window or clicks cancel
            break

        #
        # Check that input seed is valid integer
        #
        try:
            seed = int(values[0])
        except:
            window['status'].update("Invalid seed, must be integer")
            continue

        coder.initialize(seed)

        #
        # Based on combo box operation
        #
        if values[1] == 'Encode':
            inputMsg = values['rawMsg'][:-1]
            encodedMsg = coder.encodeMessage(inputMsg)
            
            if len(encodedMsg) > 0:
                window['status'].update("Message encoded")
                window['encodedMsg'].update(encodedMsg)
            else:
                window['status'].update("Failed to encode")
                window['encodedMsg'].update('')
        else:
            inputMsg = values['encodedMsg'][:-1]
            decodedMsg = coder.decodeMessage(inputMsg)
            
            if len(decodedMsg) > 0:
                window['status'].update("Message decoded")
                window['rawMsg'].update(decodedMsg)
            else:
                window['status'].update("Failed to decode")
                window['rawMsg'].update('')

    window.close()


gui = GUI()