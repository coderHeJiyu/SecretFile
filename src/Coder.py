import os
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64

block_size = 128


def aes_encrypt(secret_key, data):
    """加密数据
    :param secret_key: 加密秘钥
    :param data: 需要加密数据
    """
    # 将数据转换为byte类型
    # data = data.encode("utf-8")
    secret_key = secret_key.encode("utf-8")

    # 填充数据采用pkcs7
    padder = padding.PKCS7(block_size).padder()
    pad_data = padder.update(data) + padder.finalize()

    # 创建密码器
    cipher = Cipher(
        algorithms.AES(secret_key),
        mode=modes.ECB(),
        backend=default_backend()
    )
    # 加密数据
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(pad_data)
    return base64.b64encode(encrypted_data)


def aes_decrypt(secret_key, data):
    """解密数据
    """
    secret_key = secret_key.encode("utf-8")
    data = base64.b64decode(data)

    # 创建密码器
    cipher = Cipher(
        algorithms.AES(secret_key),
        mode=modes.ECB(),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    decrypt_data = decryptor.update(data)
    unpadder = padding.PKCS7(block_size).unpadder()
    unpad_decrypt_data = unpadder.update(decrypt_data) + unpadder.finalize()
    return unpad_decrypt_data


# 加密
def encode(source, save, key):
    key = adjust(key)
    file1 = open(source, 'rb')
    file2 = open(save, 'wb')
    for line in file1:
        temp = aes_encrypt(key, line)
        file2.write(temp + "\n".encode("utf-8"))
    file1.close()
    file2.close()


# 解密
def decode(save, result, key):
    key = adjust(key)
    file1 = open(save, 'rb')
    file2 = open(result, 'wb')
    try:
        for line in file1:
            temp = aes_decrypt(key, line)
            file2.write(temp)
    except ValueError:
        file1.close()
        file2.close()
        os.remove(result)
        return False
    else:
        file1.close()
        file2.close()
        return True


def adjust(key):
    n = 16 - len(key)
    return key + n * "$"
