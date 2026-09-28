import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def aes_encrypt(plaintext: str, key: bytes):
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(plaintext.encode('utf-8'), AES.block_size)
    ciphertext = cipher.encrypt(padded_data)
    return iv + ciphertext

def aes_decrypt(ciphertext: bytes, key: bytes):
    iv = ciphertext[:16]
    actual_ciphertext = ciphertext[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = cipher.decrypt(actual_ciphertext)
    plaintext = unpad(padded_data, AES.block_size)
    return plaintext.decode('utf-8')

if __name__ == '__main__':
    key = b'1234567890123456'
    original_message = "Nguyen Minh - K235480106097 - BMTT TNUT"
    print(f"[+] Thong diep goc: {original_message}")
    
    encrypted_data = aes_encrypt(original_message, key)
    print(f"[+] Ban ma (Hex): {encrypted_data.hex()}")
    
    decrypted_message = aes_decrypt(encrypted_data, key)
    print(f"[+] Ket qua giai ma: {decrypted_message}")