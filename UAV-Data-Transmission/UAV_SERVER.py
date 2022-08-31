from socket import socket, AF_INET, SOCK_STREAM, IPPROTO_TCP, SOL_SOCKET, SO_REUSEADDR
import cv2
import struct
import pickle
from SSL import SSL_SERVER_WRAPPER
import logging
from ssl import SSLZeroReturnError, SSLEOFError
from threading import Thread
from pymavlink.mavutil import mavlink_connection
class ConnectionThread(Thread):
    def __init__(self, UAV_SERVER):
        Thread.__init__(self)
        self.UAV_SERVER = UAV_SERVER
    
    def run(self):
        self.UAV_SERVER.__init__(certificate = self.UAV_SERVER.certificate,
                                    key = self.UAV_SERVER.key,
                                    clients_certificates = self.UAV_SERVER.clients_certificates,
                                    PORT = self.UAV_SERVER.PORT,
                                    isInitial = False)
        logging.warning("Connection regained")

class UAV_SERVER():
    def __init__(self,
                 certificate : str = 'server.crt',
                 key : str = 'server.key',
                 clients_certificates: str = 'client.crt',
                 PORT = 7500,
                 isInitial = True):
        if isInitial:
            self.__Queue = []
        self.certificate = certificate
        self.clients_certificates = clients_certificates
        self.PORT = PORT
        self.key = key
        self.__ssl_wrapper = SSL_SERVER_WRAPPER(certificate=certificate,
                  key=key,
                  clients_certificates=clients_certificates)
        
        self.__socket = socket(AF_INET,
                   SOCK_STREAM,
                   IPPROTO_TCP)
        
        self.__socket.setsockopt(SOL_SOCKET,
                     SO_REUSEADDR,
                     1)
        self.__socket.bind(("",PORT))
        self.__socket.listen()
        print("UAV SERVER is in listening mode...")
        try:
            UnSecureConnection, self.FROM = self.__socket.accept() # accept 3 way hand shake for session establishment
            self.__conn_image = self.__ssl_wrapper.Initiate_Secure_Connection(UnSecureConnection)
            self.__conn_image.settimeout(2)
            self.FROM = self.FROM[0]
            self.initialized = True
            print("3-way TCP Hand shake established with PI (" + self.FROM +") on port : " + str(PORT))    
        except Exception as ex:
            print("3-way TCP Hand shake failed due to ", str(ex))
            
            self.initialized = False
        return
        
    def __send(self):
        try:
            out = self.__Queue.pop(0)
            if not self.initialized:
                self.__Queue.append(out)
                return True
            
            Segments = pickle.dumps(out, 0)
            SegmentsNumber = len(Segments)
            self.__conn_image.sendall(struct.pack(">L", SegmentsNumber) + Segments)
            
            response = self.__conn_image.recv(1024)
            if response == b'success':
                return True
        
        except KeyboardInterrupt:
            print('Keyboard Interrupted Detected')
            print('Exiting program')
            exit()

        except SSLZeroReturnError:
            return False
        
        except Exception:
            self.__conn_image.close()
            self.initialized = False
            logging.warning("Connection failed due to : SSLEOFError")
            logging.info("RE-establishing connection")
            new_connection = ConnectionThread(self)
            new_connection.start()
            self.initialized = False
        print("ok")
        return True
    
    def sendMission(self, geolocation, image):
        _, frame = cv2.imencode('.jpg', image)
        
        mission = {
            "geo" : geolocation,
            "image" : frame,
            "finished" : False
            }
        
        self.__Queue.append(mission)
        res = self.__send()
        
        if(res == False):
            self.__Queue.append(mission)
        return res
                
        
    def endMission(self):
        while len(self.__Queue) != 0:
            self.__send()
        mission = { "finished" : True }
        res = True
        while res:
            self.__Queue.append(mission)
            res = not self.__send()
        return False
    
   



if __name__ == '__main__':
    logging.basicConfig(filename= 'AIclient.log', filemode= 'a',format='%(asctime)s-%(levelname)s-%(message)s')
    connection_string ='/dev/ttyACM0'
    logging.info("Connecting to PIX-HAWK on serial port= " + connection_string + " with baud= 115200")
    vehicle = mavlink_connection(device= connection_string, baud= 115200)
    logging.info("The PIX-HAWK has been connected successfully")
    logging.info("Connecting to the ground station on PORT= 5000")
    mysocket = UAV_SERVER()
    logging.info("The ground station has been connected successfully")
    cap = cv2.VideoCapture(0)
    logging.info("Camera stream has been captured")
    loop = True
    coordinates = (0,0)
    while loop:
        ret, frame = cap.read()
        coordinates = vehicle.location()
        geolocation = coordinates.split(",")
        geolocation = map(lambda x : float(x[4:]), coordinates)
        coordinates = list(coordinates)
        if ret:
            loop = mysocket.sendMission(coordinates, frame)
            if loop:
                logging.info("Frame with location= { " + str(coordinates) + " } has been sent to the ground station")
        else:
            logging.info("Ending the mission")
            loop = mysocket.endMission()
            if loop:
                logging.info("Mission ended successfully")
            break
    cap.release()
    logging.info("Camera stream has been released")
    logging.info("Program exited with no errors")
