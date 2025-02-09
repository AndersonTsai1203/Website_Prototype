import sys
import getpass
import hashlib
import helper

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
    """ Check if UID exists and verify CTR value. """
    db = helper.load_database()

    card = next((card for card in db["cards"] if card["uid"] == uid), None)
    if not card:
        print("\nError - Card not found in system...") # 卡片不存在系統裡
        sys.exit() # Exit the program
    elif ctr == 0 or ctr > int(card["counter"]):
        # Update counter
        card["counter"] = f"{ctr+1:08d}"
        helper.save_database(db)

        # 卡片第一次被開通 or # URL 內的 UID 符合系統儲存的 UID & URL 內的 CTR > 系統儲存的 CTR
        return True 
    else:
        # Update counter
        card["counter"] = f"{ctr+1:08d}"
        helper.save_database(db)

        # URL 內的 CTR <= 系統儲存的 CTR
        return False

def login():
    """ User login verification. """
    db = helper.load_database()
    
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")  # Hide password input

    user = next((user for user in db["users"] if user["username"] == username and user["password"] == password), None)

    return username if user else None

def signup():
    """ Create a new user account. """
    db = helper.load_database()

    username = input("Enter new username: ")
    if any(user["username"] == username for user in db["users"]):
        return None, "Access Denied - User already exists!"

    password = getpass.getpass("Enter new password: ")
    db["users"].append({"username": username, "password": password, "cards": []})

    helper.save_database(db)

    return username, "Access Granted - User registered successfully!"

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
        print("\nError - User not found!")
        sys.exit() # Exit the program 

    card = next((card for card in db["cards"] if card["uid"] == uid), None)
    if not card:
        print("\nError - Card not registered in the system!")
        sys.exit() # Exit the program
    
    if not card["registered"]:
        # Card is not assigned -> Assign it to the user
        card["registered"] = True
        user["cards"].append(uid)
        helper.save_database(db)
        return f"Access Granted - Card {uid} assigned to {username}."

    if uid in user["cards"]:
        return f"Access Granted - User {username} already owns card {uid}."

    return f"Access Denied - Card {uid} is already registered to another user."


def main():
    """ Main function to handle the complete flow """
    given_url = input("\n請輸入當前URL: ")

    try:
        # Step 1: Extract UID, CTR, and ENC
        _, uid, ctr, enc = helper.parse_sdm_url(given_url)

        # Step 2: Validate ENC
        if validate_enc(uid, ctr, enc):
            print(f"\nAccess Granted - URL 內的 ENC 驗證成功，UID 和 CTR 正確")
        else:
            print("Access Denied - URL 內的 ENC 驗證失敗，UID 或 CTR 不匹配")
            sys.exit() # Exit the program
        
        # Step 3: Validate UID and CTR
        if not validate_uid_ctr(uid, ctr):
            # URL 內的 CTR <= 系統儲存的 CTR
            print("\nAccess Denied - Counter too low.")  
            sys.exit() # Exit the program
        else:
            # 卡片第一次被開通 or # URL 內的 UID 符合系統儲存的 UID & URL 內的 CTR > 系統儲存的 CTR
            print("\nAccess Granted - Card Verified.")

        # Step 4: User Login or Signup Choice
        while True:
            choice = input("\nDo you want to [1] Login or [2] Signup? (Enter 1 or 2): ").strip()
            if choice == "1":
                username = login()
                if username:
                    break
                print("\nLogin failed: Incorrect username or password. Try again.")
            elif choice == "2":
                username, signup_message = signup()
                if username:
                    print(f"\n{signup_message}")
                    break
                print("\nSignup failed: User already exists. Try again.")
            else:
                print("\nInvalid choice. Please enter '1' for Login or '2' for Signup.")

        # Step 5: Verify if the card is assigned or assign it
        print(f"\n{verify_card_ownership(username, uid)}")

        # Step 6: Generate and display the next SDM URL (Always happens)
        next_url = helper.generate_next_sdm_url(helper.BASE_URL, given_url)
        print(f"\nNext SDM URL: {next_url}")

    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Create 5 different UIDs and URLs
    helper.generate_test_database()

    # Run the test script
    main()