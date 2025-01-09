import nfc
import time
import pandas as pd

# 初始化空的 DataFrame，存儲編號和 UID 的對應關係
columns = ['Number', 'UID']
df = pd.DataFrame(columns=columns)

def generate_number():
    """
    根據 DataFrame 自動生成流水號
    """
    if df.empty:
        return 1  # 如果 DataFrame 為空，從 1 開始
    return df['Number'].max() + 1  # 否則取最大編號 + 1

def add_uid_to_dataframe(uid):
    """
    檢查 UID 是否已存在，否則新增到 DataFrame
    """
    global df

    # 檢查 UID 是否已存在
    if uid in df['UID'].values:
        number = df.loc[df['UID'] == uid, 'Number'].iloc[0]
        print(f"UID 已存在，對應編號為：{number}")
        return number
    else:
        # 生成新流水號並新增至 DataFrame
        number = generate_number()
        new_row = {'Number': number, 'UID': uid}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        print(f"生成新編號：{number} 並綁定 UID：{uid}")
        return number

def generate_url(number, uid):
    """
    根據編號和 UID 生成靜態子網域 URL
    """
    STATIC_SUBDOMAIN_TEMPLATE = "https://nfc.sakurahighschool.com/s/{number}?uid={uid}"
    return STATIC_SUBDOMAIN_TEMPLATE.format(number=number, uid=uid)

def on_connect(tag):
    """
    當 NFC 晶片連接時執行的邏輯
    """
    try:
        # 獲取 UID
        uid = tag.identifier.hex().upper()
        print(f"檢測到 UID：{uid}")

        # 檢查 UID 並獲取編號
        number = add_uid_to_dataframe(uid)

        # 生成 URL
        unique_url = generate_url(number, uid)
        print(f"生成的靜態子網域 URL：{unique_url}")

        # 寫入 URL 到 NFC 晶片
        if tag.ndef:
            record = nfc.ndef.UriRecord(unique_url)
            tag.ndef.records = [record]
            print("成功將 URL 寫入到 NFC 晶片！")
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

def login_app():
    # get email address and password
    # check if the email is existed in the database, if yes, then check password, else go to "sign up"
    return True

def signup_app():
    # get username, email address, and create password confirm password
    # check if the email address is existed in the database, if yes, then go to "login", else create new account
    return True

if __name__ == "__main__":
    write_to_nfc()
