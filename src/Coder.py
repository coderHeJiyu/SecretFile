import os
from typing import BinaryIO
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
from abc import abstractmethod


class Coder:
    def __init__(self):
        """
        加解密器，self.progress是当前进度，是一个从0-100的数字
        """
        self.length = 0
        self.progress = 0
        self.__block_size = 128

    def __aes_encrypt(self, secret_key, data):
        """加密数据
        :param secret_key: 加密秘钥
        :param data: 需要加密数据
        """
        # 将数据转换为byte类型
        # data = data.encode("utf-8")
        secret_key = secret_key.encode("utf-8")

        # 填充数据采用pkcs7
        padder = padding.PKCS7(self.__block_size).padder()
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

    def __aes_decrypt(self, secret_key, data):
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
        unpadder = padding.PKCS7(self.__block_size).unpadder()
        unpad_decrypt_data = unpadder.update(
            decrypt_data) + unpadder.finalize()
        return unpad_decrypt_data

    # 加密
    def encode(self, source, save, key):
        """
        加密，参数为(待加密文件路径，结果路径，密钥)
        """
        suffix = os.path.splitext(source)[-1]
        # name = os.path.basename(source).split('.')[0]
        while os.path.exists(save + ".hlx"):
            save += "(1)"
        save += ".hlx"
        key = self.__adjust(key)
        file1: BinaryIO = open(source, 'rb')
        file2: BinaryIO = open(save, 'wb')
        suffix = f"#suffix={suffix}".encode("utf-8")
        suffix = self.__aes_encrypt(key, suffix)
        file2.write(suffix + "\n".encode("utf-8"))
        lines = file1.readlines()
        self.length = len(lines) - 1
        self.set_length()
        for i, line in enumerate(lines):
            temp = self.__aes_encrypt(key, line)
            file2.write(temp + "\n".encode("utf-8"))
            self.progress = i
            self.progress_change()
        file1.close()
        file2.close()

    # 解密
    def decode(self, save, result, key):
        """
        解密，参数为(待解密文件路径，结果路径，密钥)
        """
        key = self.__adjust(key)
        file1: BinaryIO = open(save, 'rb')
        try:
            suffix: str = self.__aes_decrypt(key, file1.readline()
                                             .decode("utf-8")
                                             .replace("\n", "")
                                             .encode("utf-8")).decode("utf-8")
        except:
            suffix = ".mp4"  # 默认的解密类型，兼容旧版本.hlx文件
            file1.seek(0)
        else:
            suffix = suffix.split("#suffix=")[-1]
        # 防止文件被覆盖
        while os.path.exists(result + suffix):
            result += "(1)"
        result += suffix
        file2: BinaryIO = open(result, 'wb')
        try:
            lines = file1.readlines()
            self.length = len(lines) - 1
            self.set_length()
            for i, line in enumerate(lines):
                temp = self.__aes_decrypt(key, line)
                file2.write(temp)
                self.progress = i
                self.progress_change()
        except ValueError:
            print(ValueError)
            file1.close()
            file2.close()
            os.remove(result)
            return False
        else:
            file1.close()
            file2.close()
            return True

    def __adjust(self, key):
        n = 16 - len(key)
        return key + n * "$"

    @abstractmethod
    def progress_change(self):
        pass

    @abstractmethod
    def set_length(self):
        pass


if __name__ == '__main__':
    coder = Coder()
    # file1 = "../"
    # file2 = "../password = 666.hlx"
    # coder.decode(file2, file1, "6666")
    # name = os.path.basename(file1)
    # print(name)
    # coder.decode(file1, file2, "666")
