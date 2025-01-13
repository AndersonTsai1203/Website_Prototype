from smartcard.System import readers
from smartcard.util import toHexString, toBytes
from Crypto.Cipher import AES
import os

# Developer AES key (replace with your actual key)
DEVELOPER_AES_KEY = bytes.fromhex("00000000000000000000000000000000")

class CardErrorHandler:
    """Handles NTAG 424 DNA error codes based on SW1 SW2 values."""
    
    ERROR_CODES = {
        0x9100: "OPERATION_OK: Successful operation.",
        0x911C: "ILLEGAL_COMMAND_CODE: Command code not supported.",
        0x911E: "INTEGRITY_ERROR: CRC or MAC does not match data. Padding bytes not valid.",
        0x9140: "NO_SUCH_KEY: Invalid key number specified.",
        0x917E: "LENGTH_ERROR: Length of command string invalid.",
        0x919D: "PERMISSION_DENIED: Current configuration/status does not allow the requested command.",
        0x919E: "PARAMETER_ERROR: Value of the parameter(s) invalid.",
        0x91AD: "AUTHENTICATION_DELAY: Currently not allowed to authenticate. Keep trying until the full delay is spent.",
        0x91AE: "AUTHENTICATION_ERROR: Current authentication status does not allow the requested command.",
        0x91AF: "ADDITIONAL_FRAME: Additional data frame is expected to be sent.",
        0x91BE: "BOUNDARY_ERROR: Attempt to read/write data beyond file/record limits or exceed value file limits.",
        0x91CA: "COMMAND_ABORTED: Previous command was not fully completed.",
        0x91F0: "FILE_NOT_FOUND: Specified file number does not exist.",
    }

    @staticmethod
    def handle_error(sw1, sw2):
        """Handles the error based on SW1 and SW2 values."""
        error_code = (sw1 << 8) | sw2  # Combine SW1 and SW2 into a single error code
        message = CardErrorHandler.ERROR_CODES.get(error_code, f"UNKNOWN_ERROR: SW1={sw1:02X}, SW2={sw2:02X}")
        return message


class CardReader:
    def __init__(self):
        self.connection = None
    
    def connect(self):
        reader_list = readers()
        if not reader_list:
            raise Exception("No card reader found.")
        
        self.reader = reader_list[0]
        self.connection = self.reader.createConnection()
        self.connection.connect()
        print(f"Connected to Reader: {self.reader}")
    
    def disconnect():
        pass
    
    def send_apdu(self, apdu):
        """Send Application Data Unit command to the card"""
        if not self.connection:
            raise Exception("No active connection to the card")
        
        response, sw1, sw2 = self.connection.transmit(apdu)
        print(f"APDU command sent: {toHexString(apdu)}")
        
        if sw1 == 0x91:
            return response, sw1, sw2
        else:
            # Use the ErrorHandler class to get a detailed error message
            error_message = CardErrorHandler.handle_error(sw1, sw2)
            raise Exception(f"Command failed SW1={toHexString(sw1)}, SW2={toHexString(sw2)} {error_message}")

class Authentication:
    def __init__(self, card_reader, aes_key):
        self.card_reader = card_reader
        self.aes_key = aes_key
    
    def authenticate(self):
        """Authenticate as Developer with AES KEY"""
        print("Authenticate as DEVELOPER...")
        
        # step 1: send AuthenticateEV2First command
        AUTH_CMD_PART1 = [] 
        
        encrypted_rnd_b, sw1, sw2 = CardReader.send_apdu(self.card_reader, AUTH_CMD_PART1)
        
        if (sw1, sw2) != (0x90, 0x00):
            raise Exception()
        
class CardDataManager:
    def __init__(self):
        pass
    
    def read_url():
        pass
    
    def read_token_id():
        pass
    
    def read_counter():
        pass
    
    def read_timer():
        pass
    
    def write_url():
        pass
    
    def write_token_id():
        pass
    
    def write_counter():
        pass
    
    def write_timer():
        pass
    
    
def main():
    # step 1: create connection to NFC card by the reader
    connection = CardReader.connect()
    
    # step 2 (optional for now): authenticate as developer
    # customer can only read the data and no permission to change data
    Authentication.authenticate()
    
    # step 3: select NDEF file (the file stores url, counter, etc..)
    
    

if __name__ == "__main__":
    main()
    
    