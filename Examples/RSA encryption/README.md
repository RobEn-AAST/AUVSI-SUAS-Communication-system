
# RSA Encryption

Each pair of the RSA algorithm has two keys, i.e. a public key and a private key. One key is used for encrypting the message which can only be decrypted by the other key.



## Acknowledgements

 - [Learning Concept Of RSA](https://www.tutorialspoint.com/cryptography_with_python/cryptography_with_python_understanding_rsa_algorithm.htm)
 - [How to implement](https://www.geeksforgeeks.org/how-to-encrypt-and-decrypt-strings-in-python/)

## Notes

- Python version 3.8.10
- There are three functions in this module 
                                          
        -> encrypt()
        -> decrypt()
        -> get_public_key()


## Deployment

Install RSA library

```bash
$ pip3 install pycryptodomex
```
You can input the data from a file or you can input it by yourself


### Data from a file
```bash
file = open(file_path_to_be_encrypted,"rb")#reading in binary
msg = file.read()
cipher = self.__encrypto.encrypt(message = msg)
```
Here we converted plaintext into binary

### Initilization from RSA_ENCRYPTO class
```bash
rsa_encryption = RSA_ENCRYPTO(public_key)

```
This public_key will be recieved from the server 

```bash
public_key = rsa_encryption.get_public_key()

```

```bash
cipher = rsa_encryption.encrypt(msg)

```
### Initilization from RSA_DECRYPTO class
```bash
rsa_decryption = RSA_DECRYPTO()

```

```bash
public_key = rsa_decryption.get_public_key()

```

```bash
plain_message = rsa_decryption.decrypt(cipher)

```

## Conclusion
- The entire security premise of the RSA algorithm is based on using prime factorization as a method of one way encryption.
- The public_key which is recieved from any server is used to encrypt plain_message can't be decrypted only by the private_key that the server is only who have it, that's why it is one direction.