import nfc
import time

# 靜態子網域 URL 模板
STATIC_SUBDOMAIN_TEMPLATE = "https://nfc.example.com/?uid={uid}"

def generate_url(uid):
    """
    根據 UID 生成靜態子網域 URL
    """
    return STATIC_SUBDOMAIN_TEMPLATE.format(uid=uid)

def on_connect(tag):
    """
    NFC 晶片連接時執行的邏輯
    """
    try:
        # 獲取晶片的 UID
        uid = tag.identifier.hex().upper()
        print(f"檢測到 UID：{uid}")
        
        # 生成 URL
        unique_url = generate_url(uid)
        print(f"生成的靜態子網域 URL：{unique_url}")
        
        # 檢查是否支援 NDEF
        if tag.ndef:
            # 建立 URI 記錄並寫入
            record = nfc.ndef.UriRecord(unique_url)
            tag.ndef.records = [record]
            print("成功寫入 URL 到 NFC 晶片！")
        else:
            print("此卡片不支援 NDEF 格式")
    except Exception as e:
        print(f"寫入失敗：{str(e)}")
    return False

def write_to_nfc():
    """
    自動化寫入 NFC 晶片的主函數
    """
    with nfc.ContactlessFrontend('usb') as clf:
        while True:
            print("請將卡片靠近讀寫器...")
            try:
                # 等待 NFC 晶片靠近並執行 on_connect
                clf.connect(rdwr={'on-connect': on_connect})
            except Exception as e:
                print(f"讀取器錯誤：{str(e)}")
            time.sleep(1)  # 防止快速重複操作

if __name__ == "__main__":
    write_to_nfc()
