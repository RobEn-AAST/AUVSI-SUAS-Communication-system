import ast
from socket import MsgFlag
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import binascii

from matplotlib.pyplot import cla
 
class RSA_ENCRYPTION():

    def __init__(self,
                file_path_to_be_encrypted)-> None:

        
        keyPair = RSA.generate(3072)
        pubKey = keyPair.publickey()
        file = open(file_path_to_be_encrypted,"rb")#reading in binary
        msg = file.read()
        file.close()

        self.msg = msg
        self.pubKey = pubKey
        self.keyPair = keyPair

    def Public_key(self):
        return (f"Public key:  (n={hex(self.pubKey.n)}, e={hex(self.pubKey.e)})")

    def Private_Key(self):
        return (f"Private key: (n={hex(self.pubKey.n)}, d={hex(self.keyPair.d)})")
    
    def Encrypted_Data(self):
        encryptor = PKCS1_OAEP.new(self.pubKey)
        encrypted = encryptor.encrypt(self.msg)
        return encrypted

    def Decrypted_Data(self,encrypted):
        decryptor =  PKCS1_OAEP.new(self.keyPair)
        decrypted = decryptor.decrypt(ast.literal_eval(str(encrypted)))
        return decrypted