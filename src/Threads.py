import os
from PyQt5.QtCore import pyqtSignal, QRunnable, QObject, QWaitCondition, QMutex, QMutexLocker
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

KEY_LENGTH = 32  # 密钥长度：256bit(32bytes)
BLOCK_SIZE = 128  # 可加密的固定长度


def password_pad(password):
    """
    密码填充
    """
    _pad = (KEY_LENGTH - len(password))*"$"
    return (password+_pad).encode("utf-8")


class CipherSignals(QObject):
    """
    密码器信号类
    """
    ENCODE_PROCESS = 0
    DECODE_PROCESS = 1
    FINISHED = 2
    PW_ERROR = 3
    FILE_EXIST = 4
    FILE_BROKEN = 5
    status_sig = pyqtSignal(int)
    process_sig = pyqtSignal(int)


class EncodeThread(QRunnable):
    """
    加密线程
    """

    def __init__(self, src: str, password: str, dst: str = None):
        """
        :param src: 源文件路径
        :param password: 密码
        :param dst: 目标文件（夹）路径
        """
        super().__init__()
        self.signals = CipherSignals()
        self.mutex = QMutex()
        self.wait_condition = QWaitCondition()
        self.__is_paused = False
        self.__is_stopped = False
        self.__progress = 0
        self.__src = src
        self.__password = password_pad(password)
        self.__dst = self.__get_dst(dst)

    def __get_dst(self, dst: str):
        """
        获取目标文件路径
        """
        if dst is None:
            # 如果没有指定目标文件路径，则默认在源文件所在目录生成同名文件
            dst = os.path.splitext(self.__src)[0] + ".hlx"
        elif os.path.isdir(dst):
            # 如果指定的是目录，则在该目录下生成同名文件
            src_name = os.path.splitext(os.path.basename(self.__src))[0]
            dst = os.path.join(dst, src_name + ".hlx")
        return dst

    def pause_trigger(self):
        """
        暂停/继续
        """
        if self.__is_paused:
            with QMutexLocker(self.mutex):
                self.__is_paused = False
                self.wait_condition.wakeOne()
        else:
            with QMutexLocker(self.mutex):
                self.__is_paused = True

    def quit(self):
        """
        停止
        """
        self.__is_stopped = True
        with QMutexLocker(self.mutex):
            self.__is_paused = False
            self.wait_condition.wakeOne()

    def run(self):
        # 检查是否存在同名文件
        if os.path.exists(self.__dst):
            self.signals.status_sig.emit(CipherSignals.FILE_EXIST)
            return
        _cipher = AES.new(self.__password, AES.MODE_ECB)  # 生成AES对象
        _file_size = os.path.getsize(self.__src)  # 要加密的文件大小
        _times = _file_size // BLOCK_SIZE  # 计算读取次数
        _remain = _file_size % BLOCK_SIZE  # 计算最后一次读取的大小
        self.signals.status_sig.emit(CipherSignals.ENCODE_PROCESS)
        with open(self.__src, 'rb') as rfs:
            with open(self.__dst, 'wb') as wfs:
                # 把password加密后写入到文件头部以备校验
                _password = _cipher.encrypt(self.__password)
                wfs.write(_password)
                # 把文件名加密后写入到文件头部以备解密时使用
                _filename = os.path.basename(self.__src)
                if len(_filename) > BLOCK_SIZE:
                    _filename = _filename[-BLOCK_SIZE:]
                _filename = _cipher.encrypt(
                    pad(_filename.encode("utf-8"), BLOCK_SIZE))
                wfs.write(_filename)
                # 循环读取并加密、写入到新文件
                for time in range(_times):
                    if self.__is_stopped:
                        return
                    with QMutexLocker(self.mutex):
                        while self.__is_paused:
                            self.wait_condition.wait(self.mutex)
                        _data = rfs.read(BLOCK_SIZE)
                        _data = _cipher.encrypt(_data)
                        wfs.write(_data)
                        _new_progress = time * 100 // _times
                        if _new_progress > self.__progress:
                            self.__progress = _new_progress
                            self.signals.process_sig.emit(self.__progress)
                _data = rfs.read(_remain)  # 最后一次读取
                _data = pad(_data, BLOCK_SIZE)  # 填充
                _data = _cipher.encrypt(_data)  # 加密
                wfs.write(_data)
                self.signals.process_sig.emit(100)
        self.signals.status_sig.emit(CipherSignals.FINISHED)


class DecodeThread(QRunnable):
    """
    解密线程
    """

    def __init__(self, src: str, password: str, dst: str = None):
        """
        :param src: 源文件路径
        :param password: 密码
        :param dst: 目标文件夹路径
        """
        super().__init__()
        self.signals = CipherSignals()
        self.mutex = QMutex()
        self.wait_condition = QWaitCondition()
        self.__is_paused = False
        self.__is_stopped = False
        self.__progress = 0
        self.__src = src
        self.__password = password_pad(password)
        self.__dst = self.__get_dst(dst)

    def __get_dst(self, dst: str):
        """
        获取目标文件夹路径
        """
        if dst is None:
            # 如果没有指定目标文件路径，则默认在源文件所在目录生成文件
            dst = os.path.dirname(self.__src)
        if not os.path.isdir(dst):
            raise TypeError("dst must be a directory or None")
        return dst

    def pause_trigger(self):
        """
        暂停/继续
        """
        if self.__is_paused:
            with QMutexLocker(self.mutex):
                self.__is_paused = False
                self.wait_condition.wakeOne()
        else:
            with QMutexLocker(self.mutex):
                self.__is_paused = True

    def quit(self):
        """
        停止
        """
        self.__is_stopped = True
        with QMutexLocker(self.mutex):
            self.__is_paused = False
            self.wait_condition.wakeOne()

    def run(self):
        _cipher = AES.new(self.__password, AES.MODE_ECB)  # 生成AES对象
        _filesize = os.path.getsize(self.__src)  # 获取 文件大小
        _times = (_filesize-KEY_LENGTH) // BLOCK_SIZE - \
            1  # 计算读取次数，由于被填充过，所以可以整除，只有最后一次需要去除填充
        self.signals.status_sig.emit(CipherSignals.DECODE_PROCESS)
        with open(self.__src, 'rb') as rfs:
            # 读取文件头部的password并解密，用于校验
            _password = rfs.read(KEY_LENGTH)
            _password = _cipher.decrypt(_password)
            if _password != self.__password:
                self.signals.status_sig.emit(CipherSignals.PW_ERROR)
                return
            # 读取文件头部的filename并解密，用于生成新文件名
            _block_temp = b''
            while True:
                # 读取一个block，_times减一
                _block_temp += rfs.read(BLOCK_SIZE)
                if _times > 0:
                    _times -= 1
                else:
                    self.signals.status_sig.emit(CipherSignals.FILE_BROKEN)
                    return
                # 尝试解密，如果成功则跳出循环
                try:
                    _filename = unpad(_cipher.decrypt(_block_temp), BLOCK_SIZE)
                    break
                except ValueError:
                    pass
            _filename = _filename.decode("utf-8")
            _filename = os.path.join(self.__dst, _filename)
            # 检查是否存在同名文件
            if os.path.exists(_filename):
                self.signals.status_sig.emit(CipherSignals.FILE_EXIST)
                return
            self.__dst = _filename
            with open(self.__dst, 'wb') as wfs:
                # 循环读取文件
                for time in range(_times):
                    if self.__is_stopped:
                        return
                    with QMutexLocker(self.mutex):
                        while self.__is_paused:
                            self.wait_condition.wait(self.mutex)
                        _data = rfs.read(BLOCK_SIZE)
                        _data = _cipher.decrypt(_data)
                        wfs.write(_data)
                        _new_progress = time * 100 // _times
                        if _new_progress > self.__progress:
                            self.__progress = _new_progress
                            self.signals.process_sig.emit(self.__progress)
                _data = rfs.read(BLOCK_SIZE)  # 最后一次读取
                try:
                    _data = unpad(_cipher.decrypt(_data),
                                  BLOCK_SIZE)  # 解密并去除填充的内容
                except ValueError:
                    # 如果解密失败，则说明文件已损坏
                    self.signals.status_sig.emit(CipherSignals.FILE_BROKEN)
                    return
                wfs.write(_data)
                self.signals.process_sig.emit(100)
        self.signals.status_sig.emit(CipherSignals.FINISHED)
