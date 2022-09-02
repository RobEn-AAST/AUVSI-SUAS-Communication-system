import pickle
from random import random
from requests import get, post
from os import remove
from configparser import ConfigParser

class proxyServer:
    def __init__(self, config):
        self.config = config 
        self.counter = 0
        self.url = "http://" + config["IPaddress"] + "/"

    def submitMission(self, text, geolocation, image_path):
        files = { 'image': open(image_path,'rb') }
        values = { 'text': text, 'lat': geolocation[0], 'long': geolocation[1] }
        return post(
            self.url + "submitMission/" + self.config["MissionNumber"],
            data=values,
            files=files).status_code == 200

    def getMission(self):
        res = get(self.url + "getMission/" + str(self.counter))
        if(res.status_code == 200):
            file = res._content
            with open(str(self.counter) + ".bin", "wb") as outfile:
                outfile.write(file)
            with open(str(self.counter) + ".bin", "rb") as outfile:
                terminate, geolocation, image  = pickle.load(outfile)
            remove(str(self.counter) + ".bin")
            self.counter += 1
        else:
            return False, False, None, None
        return terminate, True, geolocation, image 



if __name__ == "__main__":
    config = ConfigParser()
    config.readfp(open('proxy.config', 'r'))
    proxyConfig = config["proxy"]
    testHandler = proxyServer(config["mission"])
    terminate = True
    counter = 0
    alphanumeric = "A"
    while terminate:
        terminate, isavailable, geolocation, image = testHandler.getMission()
        if(isavailable):
            ##################################
            # do your image processing here and save the image to a directory with the following
            # format ==> proxyConfig["ImageDirectory"] + str(counter) + proxyConfig["ImageExtension"]



            ##################################
            # Use this function to upload your code modifying the function input paramters
            modified_geolocation = (random(), random())
            submission_result = testHandler.submitMission(
                text=alphanumeric,
                geolocation=modified_geolocation, 
                image_path= proxyConfig["ImageDirectory"] + str(counter) + proxyConfig["ImageExtension"])
            while(submission_result == False):
                ##################################
                # Handle submission errors here

                ##################################
                # re-submit the Object of interest
                submission_result = testHandler.submitMission(
                    text=alphanumeric,
                    geolocation=modified_geolocation, 
                    image_path= proxyConfig["ImageDirectory"] + str(counter) + proxyConfig["ImageExtension"])
            alphanumeric += 1
            counter += 1