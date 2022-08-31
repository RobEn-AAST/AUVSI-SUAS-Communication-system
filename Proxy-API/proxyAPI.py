import pickle
import requests
from os import remove

class proxyServer:
    def __init__(
        self, 
        ipaddress):

        self.url = "http://" + ipaddress + "/"

    def submitMission(
        self,
        mission,
        text,
        geolocation,
        image_path):
        
        files = {
            'image': open(image_path,'rb')
        }
        
        values = {
            'text': text,
            'lat': geolocation[0],
            'long': geolocation[1]
        }
        
        return requests.post(
            self.url + "submitMission/" + str(mission),
            data=values,
            files=files) == "success"

    def getMission(self, number):
        res = requests.get(self.url + "getMission/" + str(number))
        file = res._content
        with open(str(number) + ".bin", "wb") as outfile:
            outfile.write(file)
        with open(str(number) + ".bin", "rb") as outfile:
            terminate, geolocation, image  = pickle.load(outfile)
        remove(str(number) + ".bin")
        return terminate, geolocation, image 


if __name__ == "__main__":
    testHandler = proxyServer("127.0.0.1")
    testHandler.submitMission(mission=1, text="E", geolocation=(0,0), image_path='/home/mhwahdan/roBen/AUVSI-SUAS-Communication-system/UAV-Data-Transmission/images/0.jpeg')
    terminate, geolocation, image = testHandler.getMission(0)