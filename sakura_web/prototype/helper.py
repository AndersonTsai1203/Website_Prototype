import hashlib
import json
import random
import re

DATABASE = "database.json"

# 設定網址
BASE_URL = "https://nfc.sakurahighschool.com"
PREFIX = "/a/"


########## Functions for Database Management ##########

def load_database():
    """Load the database from a JSON file."""
    try:
        with open(DATABASE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"cards": [], "users": []}  # Default structure

def save_database(data):
    """Save the updated database to the JSON file."""
    with open(DATABASE, "w") as file:
        json.dump(data, file, indent=4)

def clear_database():
    """Reset the database by removing all cards and users."""
    empty_db = {"cards": [], "users": []}

    with open(DATABASE, "w") as file:
        json.dump(empty_db, file, indent=4)

########## Functions for URL Management ##########

def generate_new_uid():
    # 模擬 UID（10 Bytes）
    return ''.join(random.choices('0123456789ABCDEF', k=14))

def get_all_uid():
    """Retrieve all UIDs from the card section of the database."""
    db = load_database()
    
    # 從資料庫提取 UID
    if "cards" in db and db["cards"]:
        return [card["uid"] for card in db["cards"]]
    
    return []  # Return an empty list if no cards exist

def generate_new_sdm_url(uid, num):
    # 模擬 CTR（8 Bytes，計數器）
    ctr = "00000000"
    
    # 假設 ENC 為 SHA256（c實際上應該是 AES-CMAC）
    enc_data = f"{uid}{ctr}".encode()
    enc = hashlib.sha256(enc_data).hexdigest()[:16]  # 取前16位當作加密碼
    
    # 生成完整 SDM URL
    sdm_url = f"{BASE_URL}{PREFIX}{num}?uid={uid}&ctr={ctr}&enc={enc}"

    return sdm_url

def parse_sdm_url(url):
    """ 解析 SDM URL，提取 prefix（流水號）、UID 和 CTR """
    match = re.search(r"https://[^/]+(/a/\d+)\?uid=([A-F0-9]+)&ctr=(\d+)&enc=([a-f0-9]+)", url)
    if match:
        prefix, uid, ctr, enc = match.groups()
        return prefix, uid, int(ctr), enc  # 轉換 CTR 為整數
    else:
        raise ValueError("URL 格式錯誤，無法解析 prefix, UID 和 CTR")

def generate_next_sdm_url(base_url, url):
    """ Generate next SDM URL by incrementing CTR. """
    prefix, uid, ctr, _ = parse_sdm_url(url)

    ctr += 1  # Increment counter
    ctr_str = f"{ctr:08d}"  # Keep 8-digit format

    enc_data = f"{uid}{ctr_str}".encode()
    enc = hashlib.sha256(enc_data).hexdigest()[:16]  # Generate new ENC

    new_sdm_url = f"{base_url}{prefix}?uid={uid}&ctr={ctr_str}&enc={enc}"
    return new_sdm_url

########## Function for testing ##########

def generate_test_database(num=5):
    # reset the database
    clear_database()

    db = load_database()

    # generate n new card uid
    for _ in range(num):
        uid = generate_new_uid()
        db["cards"].append({"uid": uid, "counter": "00000000", "registered": False})

    save_database(db)

    all_card_uid = get_all_uid()

    # generate n new sdm url
    if not all_card_uid:
        print("Error: all_card_uid is empty.")
        return 0
    else:
        for i in range(min(num, len(all_card_uid))):
            print(f"\n{i+1}. {generate_new_sdm_url(all_card_uid[i], i)}")
