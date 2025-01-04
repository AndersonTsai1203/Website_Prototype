import nfc
import time

# 定義靜態子網域模板
STATIC_SUBDOMAIN_TEMPLATE = "https://nfc.sakurahighschool.com/?uid={uid}"

def generate_url(uid):
    """
    根據 UID 生成靜態子網域 URL
    """
    return STATIC_SUBDOMAIN_TEMPLATE.format(uid=uid)

def on_connect(tag):
    """
    當 NFC 晶片連接時執行的邏輯
    """
    try:
        # 獲取晶片的 UID
        uid = tag.identifier.hex().upper()  # 將 UID 轉為大寫十六進制
        print(f"檢測到 UID：{uid}")
        
        # 生成 URL
        unique_url = generate_url(uid)
        print(f"生成的靜態子網域 URL：{unique_url}")
        
        # 寫入 URL 到 NFC 晶片
        if tag.ndef:  # 檢查晶片是否支援 NDEF
            record = nfc.ndef.UriRecord(unique_url)
            tag.ndef.records = [record]
            print("成功將 URL 寫入到 NFC 晶片！")
        else:
            print("錯誤：此卡片不支援 NDEF 格式")
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
