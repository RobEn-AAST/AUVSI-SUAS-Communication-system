import ssl
from socket import socket

class SSL_CLIENT_WRAPPER():
    def __init__(self,
                certificate : str,
                key : str,
                server_certificate : str,
                hostname : str) -> None:
        self.hostname = hostname
        self.__ssl = ssl.create_default_context(ssl.Purpose.SERVER_AUTH,
                                                cafile=server_certificate)
        self.__ssl.load_cert_chain(certfile=certificate,
                                   keyfile=key)
    
    def Initiate_Secure_Connection(self, socket : socket):
        s = self.__ssl.wrap_socket(socket,
                                          server_side=False,
                                          server_hostname=self.hostname)
        return s
        
        
class SSL_SERVER_WRAPPER():
    def __init__(self,
                certificate : str,
                key : str,
                clients_certificates) -> None:
        self.__ssl = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.__ssl.verify_mode = ssl.CERT_REQUIRED
        self.__ssl.load_cert_chain(certfile=certificate,
                                   keyfile=key)
    
        self.__ssl.load_verify_locations(cafile=clients_certificates)
    def Initiate_Secure_Connection(self, socket : socket):
        s = self.__ssl.wrap_socket(socket,
                                          server_side=True)
        return s