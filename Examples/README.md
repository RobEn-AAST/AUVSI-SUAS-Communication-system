
# RSA Encryption

Each pair of the RSA algorithm has two keys, i.e. a public key and a private key. One key is used for encrypting the message which can only be decrypted by the other key.



## Acknowledgements

 - [Learning Concept Of RSA](https://www.tutorialspoint.com/cryptography_with_python/cryptography_with_python_understanding_rsa_algorithm.htm)
 - [How to implement](https://www.geeksforgeeks.org/how-to-encrypt-and-decrypt-strings-in-python/)

## Notes

- Python version 3.8.10
- There are four functions in this module 
                                          
        -> Encryption()
        -> Decryption()
        -> Private_Key()
        -> Public_Key()




## Deployment

Install RSA library

```bash
$ pip install rsa
```
You can input the data from a file or you can input it by yourself


### Data from a file
```bash
file = open(file_path_to_be_encrypted,"rb")#reading in binary
msg = file.read()
encrypted = encryptor.encrypt(self.msg)
```
Here we converted plaintext into binary

### Input data
```bash
encrypted = encryptor.encrypt(b'Hello World')
```
Here we converted plaintext into bytes

## Conclusion
- encrypt() function can't takes plaintext so we converted it into bytes or binary.
