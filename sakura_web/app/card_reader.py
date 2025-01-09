from smartcard.System import readers
from smartcard.Exceptions import NoCardException
from smartcard.util import toHexString, toBytes
import time

# Constant Variables

GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
"""發送命令以讀取 NFC 晶片 UID"""
SELECT_APP = [0x00, 0xA4, 0x04, 0x00, 0x05, 0xD2, 0x76, 0x00, 0x00, 0x85]
"""
[0x00, 0xA4, 0x04, 0x00] - Select command header
[0x05] - Length of AID (application ID)
[0xD2, 0x76, 0x00, 0x00, 0x85] - NTAG 424 DNA application ID
"""

class NFC_Reader:
    def __init__(self):
        self.reader = None
        self.connection = None
        self.last_uid = None
    
    def initialize_reader(self):
        # 列出所有可用的讀卡機
        available_readers = readers()
        
        if not available_readers:
            print("找不到任何讀卡機，請檢查設備連接。Exiting...")
            return

        print("可用的讀卡機:")
        for index, reader in enumerate(available_readers):
            print(f"{index}: {reader}")
        
        self.reader = available_readers[0]
        # reader_index = input("選擇讀卡機 (choose number): ")
        # self.reader = available_readers[reader_index]
        
        print(f"\n正在使用讀卡機: {self.reader}")
        
        return True

    def connect_card(self):
        # 嘗試連接卡片
        try:
            print("嘗試連接卡片...\n")
            self.connection = self.reader.createConnection()
            self.connection.connect()
            print(self.reader, toHexString(self.connection.getATR()))
            return True
        except NoCardException:
            print("讀卡機中沒有偵測到卡片，請插入卡片後重試。")
            return False
        except Exception as e:
            print(f"Connection Error: {e}")
            return False

    def send_apdu(self, apdu):
        """Send APDU (Application Data Unit) command to card"""
        if not self.connection:
            print("No card connection established!")
            return None, 0, 0
            
        try:
            response, sw1, sw2 = self.connection.transmit(apdu)
            return response, sw1, sw2
        except Exception as e:
            print(f"APDU Transmission Error: {e}")
            return None, 0, 0
        
    def get_card_uid(self):
        """Read card UID"""
        try:
            data, sw1, sw2 = self.connection.transmit(GET_UID)
            if sw1 == 0x90 and sw2 == 0x00 and data:
                return ''.join(format(x, '02X') for x in data)
            return None
        except Exception as e:
            print(f"Error reading card UID: {e}")
            return None
    
    def read_nfc_card(self, offset=0, length=416):
        """
        Read data from NTAG 424 DNA
        offset: Starting position to read from (0-415)
        length: Number of bytes to read (max 416-offset)
        """
        response, sw1, sw2 = self.send_apdu(SELECT_APP)
        
        if (sw1, sw2) != (0x90, 0x00):
            print("Failed to select application")
            return None

        # Read in chunks
        CHUNK_SIZE = 32
        all_data = []
        bytes_remaining = min(length, 416-offset)
        current_offset = offset

        while bytes_remaining > 0:
            chunk_size = min(CHUNK_SIZE, bytes_remaining)
            READ_DATA = [0x00, 0xB0, current_offset >> 8, current_offset & 0xFF, chunk_size]
            response, sw1, sw2 = self.send_apdu(READ_DATA)
            
            if (sw1, sw2) != (0x90, 0x00):
                print(f"Read failed at offset {current_offset}")
                return None

            all_data.extend(response)
            current_offset += chunk_size
            bytes_remaining -= chunk_size

        return all_data
    
    def write_nfc_card(self, data, offset=0):
        """Write data to NTAG 424 DNA"""
        if offset + len(data) > 416:
            print("Data exceeds card memory limit")
            return False

        # Select application
        SELECT_APP = [0x00, 0xA4, 0x04, 0x00, 0x05, 0xD2, 0x76, 0x00, 0x00, 0x85]
        response, sw1, sw2 = self.send_apdu(SELECT_APP)
        
        if (sw1, sw2) != (0x90, 0x00):
            print("Failed to select application")
            return False

        # Write in chunks
        CHUNK_SIZE = 32
        bytes_remaining = len(data)
        current_offset = offset
        data_position = 0

        while bytes_remaining > 0:
            chunk_size = min(CHUNK_SIZE, bytes_remaining)
            chunk_data = data[data_position:data_position + chunk_size]
            WRITE_DATA = [0x00, 0xD6, current_offset >> 8, current_offset & 0xFF, chunk_size] + chunk_data
            response, sw1, sw2 = self.send_apdu(WRITE_DATA)
            
            if (sw1, sw2) != (0x90, 0x00):
                print(f"Write failed at offset {current_offset}")
                return False

            current_offset += chunk_size
            data_position += chunk_size
            bytes_remaining -= chunk_size

        return True

        
def main():
    reader = NFC_Reader()
    if reader.initialize_reader():
        if reader.connect_card():
            card_uid = reader.get_card_uid()
            print(f"Card UID: {card_uid}")
            print("Reading card data...")
            card_data = reader.read_nfc_card()
            print(f"Card data: {card_data}")
if __name__ == "__main__":
    main()