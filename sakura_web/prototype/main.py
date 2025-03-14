import getpass
import hashlib
import helper
import time

current_user = None

def validate_enc(uid, ctr, enc):
    """ 驗證 SDM URL 中的 ENC 是否正確 """
    # 重新計算 ENC
    ctr_str = f"{ctr:08d}"  # 保持 8 位數格式
    enc_data = f"{uid}{ctr_str}".encode()
    expected_enc = hashlib.sha256(enc_data).hexdigest()[:16]  # 取前16位當作加密碼

    # 比對計算出的 ENC 和 URL 內的 ENC
    if expected_enc == enc:
        return True # URL 內的 ENC 驗證成功，UID & CTR 正確
    else:
        return False # URL 內的 ENC 驗證失敗，UID 或 CTR 不匹配

def validate_uid_ctr(uid, ctr):
    """ Check if UID exists, verify CTR value and update CTR value """
    db = helper.load_database()

    card = next((card for card in db["cards"] if card["uid"] == uid), None)
    if not card:
        # 卡片不存在系統裡
        return False, 1, "Error - 卡片不存在系統裡..."

    if ctr == 0:
        # 卡片第一次被開通 or # URL 內的 UID 符合系統儲存的 UID & URL 內的 CTR > 系統儲存的 CTR
        return True, 2, "審核通過 - 卡片已被驗證."

    if ctr > int(card["counter"]):
        # Update counter
        temp_ctr = int(card["counter"])
        temp_ctr += 1  # Increment counter
        card["counter"] = f"{temp_ctr:08d}" # Keep 8-digit format
        helper.save_database(db)

        # 卡片第一次被開通 or # URL 內的 UID 符合系統儲存的 UID & URL 內的 CTR > 系統儲存的 CTR
        return True, 2, "審核通過 - 卡片已被驗證."
    
    # Update counter
    ctr += 1  # Increment counter
    card["counter"] = f"{ctr:08d}" # Keep 8-digit format
    helper.save_database(db)

    # URL 內的 CTR <= 系統儲存的 CTR
    return False, 0, "審核失敗 - Counter值太低."

def login():
    """ User login verification. """
    db = helper.load_database()
    
    username = input("\nEnter username: ")
    password = getpass.getpass("Enter password: ")  # Hide password input

    user = next((user for user in db["users"] if user["username"] == username and user["password"] == password), None)

    return username if user else None

def signup():
    """ Create a new user account. """
    db = helper.load_database()

    username = input("\nEnter new username: ")
    if any(user["username"] == username for user in db["users"]):
        return None, "審核失敗 - 該用戶已經存在系統裡!"

    password = getpass.getpass("Enter new password: ")
    db["users"].append({"username": username, "password": password, "cards": []})

    helper.save_database(db)

    return username, "審核通過 - 用戶登記成功!"

def logout():
    """ Logout the current user """
    global current_user
    message = f"用戶 {current_user} 已被登出."
    current_user = None  # Reset user
    return message

def reset_password():
    """ Reset a user's password. """
    pass

def verify_card_ownership(username, uid):
    """
    Check if a card is registered to a user based on the flag.
    If the flag is False, assign the card to the user.
    If the flag is True, check if the user owns the card.
    """
    db = helper.load_database()

    user = next((user for user in db["users"] if user["username"] == username), None)
    if not user:
        return False, "Error - 查詢不到該用戶!"

    card = next((card for card in db["cards"] if card["uid"] == uid), None)
    if not card:
        return False, "Error - 該卡片沒有被登記在系統裡!"
    
    if not card["registered"]:
        # Card is not assigned -> Assign it to the user
        card["registered"] = True
        user["cards"].append(uid)
        helper.save_database(db)
        return True, f"審核通過 - 卡片序號 {uid} 登記在 {username}."

    if uid in user["cards"]:
        return True, f"審核通過 - 用戶 {username} 已經擁有 {uid}."

    return False, f"審核失敗 - 卡片序號 {uid} 已經登記在其他用戶."


def main():
    # Create 5 different UIDs and URLs
    helper.generate_test_database()

    global current_user

    while True:
        """ Main function to handle the complete flow """
        given_url = input("\n請輸入當前URL (or type 'exit' to quit): ")
        if given_url.lower() == "exit":
            print("\nExiting system...")
            break

        try:
            # Step 1: Extract UID, CTR, and ENC
            print("\n--- Step 1: 解析 UID, CTR, and ENC ---")
            _, uid, ctr, enc = helper.parse_sdm_url(given_url)
            time.sleep(2)
            
            # Step 2: Validate ENC
            print("\n--- Step 2: 正在驗證 ENC ---")
            if not validate_enc(uid, ctr, enc):
                print("\n審核失敗 - URL 內的 ENC 驗證失敗，UID 或 CTR 不匹配")
                time.sleep(2)
                next_new_url = helper.generate_next_sdm_url(helper.BASE_URL, given_url)
                print(f"\nStep 7 - Next SDM URL: {next_new_url}")
                continue  # Loop back to Step 1
            else:
                print(f"\n審核通過 - URL 內的 ENC 驗證成功，UID 和 CTR 正確")
                time.sleep(2)

            # Step 3: Validate UID and CTR
            print("\n--- Step 3: 正在驗證 UID and CTR ---")
            validation, flag, validation_message = validate_uid_ctr(uid, ctr)
            if not validation:
                if flag == 0:
                    # URL 內的 CTR <= 系統儲存的 CTR
                    print(f"\n{validation_message}")
                    time.sleep(2)  
                    next_new_url = helper.generate_next_sdm_url(helper.BASE_URL, given_url)
                    print(f"\nStep 7 - Next SDM URL: {next_new_url}")
                    continue  # Loop back to Step 1
                if flag == 1:
                    print(f"\n{validation_message}")
                    break
            else:
                # 卡片第一次被開通 or # URL 內的 UID 符合系統儲存的 UID & URL 內的 CTR > 系統儲存的 CTR
                print(f"\n{validation_message}")
                time.sleep(2)

            # Step 4: User Login or Signup Choice
            print("\n--- Step 4: 用戶登入 or 登記 ---")
            while True:
                choice = input("\nDo you want to [1] 登入 or [2] 登記? (Enter 1 or 2): ").strip()
                if choice == "1":
                    username = login()
                    if username:
                        current_user = username
                        break
                    print("\n登入失敗: 錯誤用戶名 or 密碼. 請重新嘗試.")
                elif choice == "2":
                    username, signup_message = signup()
                    if username:
                        current_user = username
                        print(f"\n{signup_message}")
                        break
                    print("\n登記失敗: 該用戶已經存在系統裡. 請重新嘗試.")
                else:
                    print("\n錯誤選項. 請輸入 '1' for 登入 or '2' for 登記.")

            time.sleep(2)

            # Step 5: Verify if the card is assigned or assign it
            print("\n--- Step 5: 正在驗證卡片持有者 ---")
            card_ownership, card_ownership_message = verify_card_ownership(username, uid)
            if not card_ownership:
                print(f"{card_ownership_message}. Jumping to Step 7...")
                next_new_url = helper.generate_next_sdm_url(helper.BASE_URL, given_url)
                print(f"\nStep 7 - Next SDM URL: {next_new_url}")
                continue  # Loop back to Step 1
            else:
                print(f"\n卡片持有者驗證結果: {card_ownership_message}")

            while True:
                # After login or signup - Simulate user "using the application"
                print(f"\n{current_user} 正在使用該應用程式中...")
                time.sleep(5)

                # Step 6 Logout choice:
                # Ask the user if they want to logout
                logout_choice = input("\nDo you want to 登出? (yes/no): ").strip().lower()
                if logout_choice == 'yes':
                    logout_message = logout()
                    print(f"\n--- Step 6: {logout_message} - Jumping to Step 7... ---")
                    break  # Exit the application loop and restart from Step 1
            
            time.sleep(2)

            # Step 7: Generate and display the next SDM URL (Always happens)
            print("\n--- Step 7: Generating Next SDM URL ---")
            next_new_url = helper.generate_next_sdm_url(helper.BASE_URL, given_url)
            print(f"\nStep 7 - Next SDM URL: {next_new_url}")
            time.sleep(2)

        except ValueError as e:
            print(f"Error: {e}")
            break # Exit loop if an error occurs

if __name__ == "__main__":
    # Run the test script
    main()