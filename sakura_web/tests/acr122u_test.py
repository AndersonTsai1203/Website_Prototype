from smartcard.System import readers
from smartcard.Exceptions import NoCardException

def read_nfc():
    # 列出所有可用的讀卡機
    available_readers = readers()
    if not available_readers:
        print("找不到任何讀卡機，請檢查設備連接。")
        return

    print("可用的讀卡機:")
    for index, reader in enumerate(available_readers):
        print(f"{index}: {reader}")

    # 選擇第一個讀卡機（可以改成手動選擇）
    reader = available_readers[0]
    print(f"\n正在使用讀卡機: {reader}")

    connection = reader.createConnection()

    # 嘗試連接卡片
    try:
        connection.connect()
    except NoCardException:
        print("讀卡機中沒有偵測到卡片，請插入卡片後重試。")
        return

    # 發送命令以讀取 NFC 晶片 UID
    GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
    try:
        data, sw1, sw2 = connection.transmit(GET_UID)
        if sw1 == 0x90 and sw2 == 0x00:
            if data:
                print(f"NFC 晶片 UID: {''.join(format(x, '02X') for x in data)}")
            else:
                print("沒有讀取到任何卡片，請嘗試再次掃描。")
        else:
            print(f"讀取失敗，狀態碼: {sw1:02X} {sw2:02X}")
    except Exception as e:
        print(f"讀取過程中出現錯誤: {e}")

if __name__ == "__main__":
    read_nfc()