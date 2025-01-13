from smartcard.System import readers
from smartcard.util import toHexString
from Crypto.Cipher import AES
import os

# Developer AES key (replace with your actual key)
DEVELOPER_AES_KEY = bytes.fromhex("00112233445566778899AABBCCDDEEFF")

def connect_to_reader():
    """Connect to the NFC reader."""
    r = readers()
    if not r:
        raise Exception("No NFC reader found.")
    reader = r[0]
    connection = reader.createConnection()
    connection.connect()
    print(f"Connected to reader: {reader}")
    return connection

def send_apdu(connection, apdu):
    """Send an APDU command and handle the response."""
    response, sw1, sw2 = connection.transmit(apdu)
    print(f"APDU Sent: {toHexString(apdu)}")
    print(f"Response: {toHexString(response)}, SW: {sw1:02X} {sw2:02X}")
    if sw1 == 0x90 and sw2 == 0x00:  # Command successful
        return response, sw1, sw2
    else:
        raise Exception(f"Command failed. SW: {sw1:02X} {sw2:02X}")

def authenticate_developer(connection, aes_key):
    print("Authenticating as developer...")

    # Step 1: Send AuthenticateEV2First command
    AUTH_CMD_PART1 = [0x90, 0x71, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00]

    rnd_b, sw1, sw2 = send_apdu(connection, AUTH_CMD_PART1)
    if sw1 != 0x90 or sw2 != 0x00:
        raise Exception(f"Part 1 failed. SW: {sw1:02X} {sw2:02X}")
    print(f"RndB: {toHexString(rnd_b)}")

    # Step 2: Decrypt RndB and generate RndA
    cipher = AES.new(aes_key, AES.MODE_ECB)
    rnd_b_decrypted = cipher.decrypt(bytes(rnd_b))
    rnd_a = os.urandom(16)
    rnd_ab = rnd_a + rnd_b_decrypted[:8]
    print(f"RndA: {toHexString(rnd_a)}")

    # Step 3: Encrypt RndA + RndB' and send
    rnd_ab_encrypted = cipher.encrypt(rnd_ab)
    AUTH_CMD_PART2 = [0x90, 0xAF, 0x00, 0x00, len(rnd_ab_encrypted)] + list(rnd_ab_encrypted)
    response, sw1, sw2 = send_apdu(connection, AUTH_CMD_PART2)
    if sw1 == 0x90 and sw2 == 0x00:
        print("Developer authentication successful.")
    else:
        raise Exception(f"Part 2 failed. SW: {sw1:02X} {sw2:02X}")


def read_card_uid(connection):
    """Read the card's UID."""
    GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
    response, sw1, sw2 = send_apdu(connection, GET_UID)
    print(f"Card UID: {toHexString(response)}")
    return response

def read_ndef_data(connection, length=16):
    """Read data from the NDEF file."""
    select_file(connection, [0xE1, 0x04])  # Select NDEF file
    READ_BINARY = [0x00, 0xB0, 0x00, 0x00, length]
    response, sw1, sw2 = send_apdu(connection, READ_BINARY)
    print(f"NDEF Data: {toHexString(response)}")
    return response

def write_ndef_data(connection, data):
    """Write data to the NDEF file."""
    select_file(connection, [0xE1, 0x04])  # Select NDEF file
    WRITE_BINARY = [0x00, 0xD6, 0x00, 0x00, len(data)] + data
    send_apdu(connection, WRITE_BINARY)
    print("NDEF data written successfully.")

def select_file(connection, file_id):
    """Select a file by its ID."""
    SELECT_FILE = [0x00, 0xA4, 0x00, 0x0C, 0x02] + file_id
    send_apdu(connection, SELECT_FILE)
    print(f"File {toHexString(file_id)} selected.")

def write_counter_value(connection, counter):
    """Write a counter value to a proprietary file."""
    select_file(connection, [0xE1, 0x05])  # Select proprietary file
    WRITE_BINARY = [0x00, 0xD6, 0x00, 0x00, 0x04] + list(counter.to_bytes(4, 'big'))
    send_apdu(connection, WRITE_BINARY)
    print(f"Counter value {counter} written successfully.")

def write_token_and_timer(connection, token, timer):
    """Write token and timer values to a proprietary file."""
    select_file(connection, [0xE1, 0x05])  # Select proprietary file
    data = token.to_bytes(4, 'big') + timer.to_bytes(4, 'big')
    WRITE_BINARY = [0x00, 0xD6, 0x00, 0x08, len(data)] + list(data)
    send_apdu(connection, WRITE_BINARY)
    print(f"Token ID {token}, Timer {timer} written successfully.")

def main():
    try:
        connection = connect_to_reader()

        # Authenticate developer
        authenticate_developer(connection, DEVELOPER_AES_KEY)

        # Read UID
        print("\nReading Card UID...")
        uid = read_card_uid(connection)

        # Write counter value
        print("\nUpdating Counter...")
        counter_value = 1  # Example counter
        write_counter_value(connection, counter_value)

        # Write URL link
        print("\nWriting URL Link...")
        url_data = [0x03, 0x0F, 0xD1, 0x01, 0x0B, 0x55, 0x03] + [ord(c) for c in "example.com"]
        write_ndef_data(connection, url_data)

        # Write token and timer
        print("\nWriting Token and Timer...")
        token_id = 12345678
        timer_value = 98765432
        write_token_and_timer(connection, token_id, timer_value)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
