from RSA import RSA_DECRYPTO, RSA_ENCRYPTO

receiver = RSA_DECRYPTO() # Create decryption object
 
public_key = receiver.get_public_key() # Get public key

sender = RSA_ENCRYPTO(public_key) # Create encryption object

message = b'Hello from roBen' # Sample bytes for testing

cipher = sender.encrypt(message= message) # Encrypt message using RSA encryption

print(cipher) # Print the Cipher bytes

message = receiver.decrypt(cipher= cipher) # Decrypt the cipher to receive the message again

print(message) # Print message bytes

decoded_message = message.decode('utf-8') # Decode the message bytes to a normal string

print(decoded_message) # Print the decoded message