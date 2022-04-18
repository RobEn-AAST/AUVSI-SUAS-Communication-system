
# SSL/TLS Secure Socket Programming (Python)

Here we are using socket programming but by encrypting and decrypting the data sent between the server and the client.


## Acknowledgements

 - [Using Socket programming in Python](https://realpython.com/python-sockets/)
 - [How does the ssl works](https://www.youtube.com/watch?v=33VYnE7Bzpk&t=253s)
 - [How to create and customize you own certificate and key](https://www.electricmonk.nl/log/2018/06/02/ssl-tls-client-certificate-verification-with-python-v3-4-sslcontext/)


## Notes

- Python version 3.8.10, Openssl version 1.1.1
- Testing certificates are self-assigned with openssl
- Using wireshark to ensure the encryption for the data transfered
- Change ip address in server.py and client.py script correspond to your own ip addresss


## Creating Key && Certificate For Ends (Server, Client)

Create a certificate and key for the server <Make sure that enter "Safty" for the Common Name>

```bash
$ openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout server.key -out server.crt
```


Create a certificate and key for the client

```bash
 $ openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout client.key -out client.crt
```


## Checking With Wireshark :
- After opening it click on loopback -> As you are fetching localy
- Filter by typing SSL
- Click on the packet that have in it's info Application Data -> Transport Layer Secuirty -> Encrypted Application Data