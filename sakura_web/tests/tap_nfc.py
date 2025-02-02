import hashlib
import re

def parse_sdm_url(url):
    """ 解析 SDM URL，提取 prefix（流水號）、UID 和 CTR """
    match = re.search(r"https://[^/]+(/a/\d+)\?uid=([A-F0-9]+)&ctr=(\d+)&enc=([a-f0-9]+)", url)
    if match:
        prefix, uid, ctr, enc = match.groups()
        return prefix, uid, int(ctr), enc  # 轉換 CTR 為整數
    else:
        raise ValueError("URL 格式錯誤，無法解析 prefix, UID 和 CTR")

def generate_next_sdm_url(base_url, url):
    """ 根據當前的 SDM URL 解析 prefix、UID，然後產生下一次 Tap 的 SDM URL """
    
    # 解析 prefix、UID 和 CTR
    prefix, uid, ctr, _ = parse_sdm_url(url)

    # 增加 CTR（模擬下一次 Tap）
    ctr += 1
    ctr_str = f"{ctr:08d}"  # 保持 8 位數格式

    # 重新計算 ENC（模擬加密驗證碼，實際應該用 AES-CMAC）
    enc_data = f"{uid}{ctr_str}".encode()
    enc = hashlib.sha256(enc_data).hexdigest()[:16]  # 取前16位當作加密碼

    # 生成新的 SDM URL（prefix 跟著變）
    new_sdm_url = f"{base_url}{prefix}?uid={uid}&ctr={ctr_str}&enc={enc}"
    
    return new_sdm_url

# 測試：提供不同 prefix 的 SDM URL
base_url = "https://nfc.sakurahighschool.com"

# 生成下一次 Tap 的 SDM URL
current_url1 = input("請輸入當前URL")
next_url1 = generate_next_sdm_url(base_url, current_url1)
print("下一次 Tap 的 SDM URL:", next_url1)