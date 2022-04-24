import RSA as rsa

x = rsa.RSA_ENCRYPTION("file.txt")
encrypted_data = x.Encrypted_Data()
decrypted_data = x.Decrypted_Data(encrypted_data)
public_key = x.Public_key()
private_key = x.Private_Key()

print(encrypted_data)
print(decrypted_data)
print(public_key)
print(private_key)