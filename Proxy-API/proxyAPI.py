import pickle
import requests


class serverHandler:
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
            'geolocation': geolocation
        }
        
        return requests.post(
            self.url + "submitImage/" + str(mission),
            data=values,
            files=files) == "success"

    def getMission(self, number):
        mission_binary = requests.get(self.url + "submitImage/" + str(number))
        terminate, geolocation, image = pickle.loads(mission_binary)
        return terminate, geolocation, image 