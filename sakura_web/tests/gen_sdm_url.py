import hashlib
import random

def generate_sdm_url(base_url, prefix, num):

    # 模擬 UID（10 Bytes）
    uid = ''.join(random.choices('0123456789ABCDEF', k=14))
    
    # 模擬 CTR（8 Bytes，計數器）
    ctr = "00000000" 
    
    # 假設 ENC 為 SHA256（c實際上應該是 AES-CMAC）
    enc_data = f"{uid}{ctr}".encode()
    enc = hashlib.sha256(enc_data).hexdigest()[:16]  # 取前16位當作加密碼
    
    # 生成完整 SDM URL
    sdm_url = f"{base_url}{prefix}{num}?uid={uid}&ctr={ctr}&enc={enc}"
    
    return sdm_url

def generate_multiple_sdm_urls(num):
    for i in range(num):
        sdm_link = generate_sdm_url(base_url, prefix, i)
        print(sdm_link)

# 設定網址
base_url = "https://nfc.sakurahighschool.com"
prefix = "/a/"

# 生成模擬的 SDM URL

num = 5
sdm_link = generate_multiple_sdm_urls(num)