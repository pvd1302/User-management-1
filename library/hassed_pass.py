import bcrypt


def hash_password(password):
    # Băm mật khẩu
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password


# # Sử dụng hàm hash_password
# password_from_json = "your_password_from_json"
# hashed_password_result = hash_password(password_from_json)
# print(hashed_password_result)
