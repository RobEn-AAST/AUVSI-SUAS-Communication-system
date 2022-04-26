from Cryptodome.PublicKey.RSA import generate as generate_keys
from Cryptodome.Cipher.PKCS1_OAEP import new as OAEP 


class RSA_DECRYPTO():

    def __init__(self)-> None:
        key = generate_keys(3072)
        private = key.export_key()
        self.__public = key.public_key().export_key()
        self.__decrypto = OAEP(private)
    
    def get_public_key(self):
        return self.__public

    def decrypt(self, cipher):
        message = self.__decrypto.decrypt(ciphertext= cipher)
        return message
    
class RSA_ENCRYPTO():
    def __init__(self, public)-> None:
        self.__public = public
        self.__encrypto = OAEP(public)
        
    def get_public_key(self):
        return self.__public
    
    def encrypt(self, message):
        cipher = self.__encrypto.encrypt(message= message)
        return cipher