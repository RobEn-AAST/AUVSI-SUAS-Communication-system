from Cryptodome.PublicKey.RSA import generate as generate_keys, import_key
from Cryptodome.Cipher.PKCS1_OAEP import new as OAEP 

class RSA_DECRYPTO():
    def __init__(self)-> None:
        key = generate_keys(3072)
        self.__public = key.public_key().export_key()
        self.__decrypto = OAEP(key)
    
    def get_public_key(self):
        return self.__public

    def decrypt(self, cipher):
        message = self.__decrypto.decrypt(ciphertext= cipher)
        return message
    
class RSA_ENCRYPTO():
    def __init__(self, public)-> None:
        key = import_key(public)
        self.__public = key.export_key()
        self.__encrypto = OAEP(key)
        
    def get_public_key(self):
        return self.__public
    
    def encrypt(self, message):
        cipher = self.__encrypto.encrypt(message= message)
        return cipher