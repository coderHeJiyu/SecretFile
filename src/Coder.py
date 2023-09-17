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
        # return base64.b64encode(encrypted_data)
        # return encrypted_data
        return encrypted_data.decode("utf-8").encode("utf-8")

    def __aes_decrypt(self, secret_key, data):
        """解密数据
        """
        secret_key = secret_key.encode("utf-8")
        # data = base64.b64decode(data)
        data = data.decode("utf-8")

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

    def __safe_output(self, dst_path, suffix):
        """
        生成安全的结果路径，防止文件被覆盖
        :param dst_path: 结果存放的路径（不包含后缀）
        :param suffix: 后缀名
        """
        if os.path.exists(dst_path + suffix):
            __count = 1
            while os.path.exists(dst_path + f"({__count})" + suffix):
                __count += 1
            dst_path += f"({__count})"
        return dst_path + suffix

    def encode(self, src_path, dst_path, key):
        """
        加密文件
        :param src_path: 待加密文件路径
        :param dst_path: 结果存放的路径（不包含后缀）
        :param key: 密钥
        """
        # 打开待加密文件
        with open(src_path, 'rb') as __src_file:
            # 计算文件行数
            self.length = -1
            for line in __src_file:
                self.length = self.length + 1
            #计算完成
            self.count_done()
            __src_file.seek(0)
            # 打开输出文件
            dst_path = self.__safe_output(dst_path, ".hlx")
            key = self.__adjust(key)
            with open(dst_path, 'wb') as __dst_file:
                # 写入源文件后缀
                __suffix = os.path.splitext(src_path)[-1]
                __suffix = f"#suffix={__suffix}".encode("utf-8")
                __suffix = self.__aes_encrypt(key, __suffix)
                __dst_file.write(__suffix + "\n".encode("utf-8"))
                # 进度条归零
                self.progress = 0
                self.progress_change()
                # 逐行加密
                for i, line in enumerate(__src_file):
                    __temp = self.__aes_encrypt(key, line)
                    __dst_file.write(__temp + "\n".encode("utf-8"))
                    # __dst_file.write(__temp)
                    if self.progress != i * 100 // self.length:
                        self.progress = i * 100 // self.length
                        self.progress_change()
                # 加密完成
                __src_file.close()
                __dst_file.close()

    # 解密
    def decode(self, src_path, dst_path, key):
        """
        解密文件
        :param src_path: 待解密文件路径
        :param dst_path: 结果存放的路径（不包含后缀）
        :param key: 密钥
        """
        key = self.__adjust(key)
        # 打开待解密文件
        with open(src_path, 'rb') as __src_file:
            # 计算文件行数
            self.length = -1
            for line in __src_file:
                self.length = self.length + 1
            #计算完成
            self.count_done()
            __src_file.seek(0)
            # 读取后缀
            try:
                __suffix: str = self.__aes_decrypt(key, __src_file.readline()
                                                   .decode("utf-8")
                                                   .replace("\n", "")
                                                   .encode("utf-8")).decode("utf-8")
            except ValueError:
                # 默认的解密类型，兼容旧版本.hlx文件
                __suffix = ".mp4"  
                __src_file.seek(0)
            else:
                __suffix = __suffix.split("#suffix=")[-1]
                self.length -= 1
            # 打开输出文件
            dst_path = self.__safe_output(dst_path, __suffix)
            key = self.__adjust(key)
            with open(dst_path, 'wb') as __dst_file:
                try:
                    # 进度条归零
                    self.progress = 0
                    self.progress_change()
                    # 逐行解密
                    for i, line in enumerate(__src_file):
                        __temp = self.__aes_decrypt(key, line)
                        __dst_file.write(__temp)
                        if self.progress != i * 100 // self.length:
                            self.progress = i * 100 // self.length
                            self.progress_change()
                except ValueError:
                    print(ValueError)
                    __src_file.close()
                    __dst_file.close()
                    os.remove(dst_path)
                    return False
                __src_file.close()
                __dst_file.close()
                return True

    def __adjust(self, key):
        n = 16 - len(key)
        return key + n * "$"

    @abstractmethod
    def progress_change(self):
        pass

    @abstractmethod
    def count_done(self):
        pass


if __name__ == '__main__':
    coder = Coder()
    # file1 = "../"
    # file2 = "../password = 666.hlx"
    # coder.decode(file2, file1, "6666")
    # name = os.path.basename(file1)
    # print(name)
    # coder.decode(file1, file2, "666")
