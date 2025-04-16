from business_api.settings import SECRET_KEY
from cryptography.fernet import Fernet
from datetime import datetime
import base64
import hashlib

class Encryption:
    """Шифрование данных при помощи приватного ключа FERNET"""

    fernet = Fernet(base64.b64encode(SECRET_KEY.encode()[:32]))

    part_1_sign = hashlib.sha256(datetime.now().strftime("%m-%d").__str__().encode('UTF-8')).hexdigest()
    part_2_sign = hashlib.sha256(SECRET_KEY.encode('UTF-8')).hexdigest()
    part_3_sign = hashlib.sha256(str(part_2_sign+part_1_sign).encode('UTF-8')).hexdigest()

    sign = hashlib.sha256((part_1_sign+part_2_sign+part_3_sign).encode('UTF-8')).hexdigest().encode()

    @staticmethod
    def encrypt_data(data) -> bytes: 
        """Шифрование"""

        try:
            if type(data) != bytes: data = data.encode()
        except:
            if type(data) != bytes: data = bytes(data)
        return Encryption.fernet.encrypt(data)

    @staticmethod 
    def decrypt_data(data) -> str:
        """Дешифрование"""

        try:
            if type(data) != bytes: data = data.encode()
        except:
            if type(data) != bytes: data = bytes(data)
        return Encryption.fernet.decrypt(data).decode()