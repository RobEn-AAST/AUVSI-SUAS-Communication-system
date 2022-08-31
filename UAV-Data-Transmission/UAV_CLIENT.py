#!/usr/bin/python3
from socket import socket, AF_INET, SOCK_STREAM, IPPROTO_TCP, SOL_SOCKET, SO_REUSEADDR
import cv2
import pickle
import struct
from threading import Thread
import logging
from SSL import SSL_CLIENT_WRAPPER



class ConnectionThread(Thread):
    def __init__(self, UAV_CLIENT):
        Thread.__init__(self)
        self.UAV_CLIENT = UAV_CLIENT
    
    def run(self):
        self.UAV_CLIENT.__init__(ADDRESS = self.UAV_CLIENT.ADDRESS, 
                                 isInitial = False)
        logging.warning("Connection regained")


class UAV_CLIENT():
    def __init__(self,
                 certificate : str = 'client.crt',
                 key : str = 'client.key',
                 server_certificate : str = 'server.crt',
                 hostname : str = 'Safty',
                 ADDRESS: str = '127.0.0.1',
                 PORT: int = 7500,
                 TIMEOUT: int = 2,):
            
        self.ADDRESS = ADDRESS
        self.PORT = PORT
        s = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.__ssl_wrapper = SSL_CLIENT_WRAPPER(certificate=certificate,
                                         key=key,
                                         server_certificate=server_certificate,
                                         hostname=hostname)
        self.__connection = self.__ssl_wrapper.Initiate_Secure_Connection(s)
        self.__connection.settimeout(TIMEOUT)
        while True:
            try:
                self.__connection.connect((ADDRESS, PORT))
                break
            except KeyboardInterrupt:
                print('Keyboard Interrupted Detected')
                print('Exiting program')
                exit()
            except Exception as ex:
                if not (self.__connection):
                    self.__connection.close()
        self.initialized = True


    def receiveMissions(self):
        image  = None
        payload_size = struct.calcsize(">L")
        try:
            string = b""
            while len(string) < payload_size:
                bits = self.__connection.recv(1024)
                if (len(bits) < 1 ) :
                    break
                string += bits
            packed_msg_size = string[:payload_size]
            data = string[payload_size:]
            msg_size = struct.unpack(">L", packed_msg_size)[0]
            
            while len(data) < msg_size:
                bits = self.__connection.recv(1024)
                data += bits
            
            frame_data = data[:msg_size]
            data = data[msg_size:]
            mission = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
            
            if mission["finished"]:
                return False,None,None
            
            image=cv2.resize(cv2.imdecode(mission["image"], cv2.IMREAD_COLOR),(1450,1080))
            geolocation = mission["geo"]
            self.__connection.sendall(b"success")
            return True,geolocation, image
        except Exception as ex:
            self.initialized = False
            print("Mission receiving failed")
            print("RE-establishing connection")
            print(ex)
            self.__connection.close()
            s = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
            s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.__connection = self.__ssl_wrapper.Initiate_Secure_Connection(s)
            self.__connection.settimeout(2)
            while True:
                try:
                    self.__connection.connect((self.ADDRESS, self.PORT))
                    break
                except Exception as ex2:
                    print("regain time out: " + str(ex2))
                    self.__connection.close()
                    s = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
                    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                    self.__connection = self.__ssl_wrapper.Initiate_Secure_Connection(s)
                    self.__connection.settimeout(2)
                    continue
            self.initialized = True
            print("connection regained")
            return True, None, None

    
#Driver code to the program
#driver code to test the program
if __name__ == '__main__':
    myserver = UAV_CLIENT(ADDRESS = '192.168.1.44')
    terminate = True
    counter = 0
    while terminate:
        mission= myserver.receiveMissions()
        if mission[1] is None:
            continue
        else:
            with open("missionPool/" + str(counter) + ".bin", "wb") as outfile:
                outfile.write(pickle.dumps(mission))
            cv2.imwrite("images/" + str(counter) + ".jpeg", mission[2])
            counter += 1  
    print("finished")
    cv2.destroyAllWindows()
