from proxyAPI import proxyServer
from configparser import ConfigParser
from random import randint



if __name__ == "__main__":
    config = ConfigParser()
    config.readfp(open('proxy.config', 'r'))
    proxyConfig = config["proxy"]
    testHandler = proxyServer(config["mission"])
    terminate = True
    counter = 0
    default_alphanumberics = ["M", "T", "C", "6"]
    while terminate:
        terminate, isavailable, geolocation, image = testHandler.getMission()
        alphanumeric = default_alphanumberics[randint(0, len(default_alphanumberics) - 1)]
        if(isavailable):
            ##################################
            # do your image processing here and save the image to a directory with the following
            # format ==> proxyConfig["ImageDirectory"] + str(counter) + proxyConfig["ImageExtension"]



            ##################################
            # Use this function to upload your code modifying the function input paramters
            submission_result = testHandler.submitMission(
                text=alphanumeric,
                geolocation=geolocation, 
                image_path= proxyConfig["ImageDirectory"] + str(counter) + proxyConfig["ImageExtension"])
            while(submission_result == False):
                ##################################
                # Handle submission errors here



                ##################################
                # re-submit the Object of interest
                submission_result = testHandler.submitMission(
                    text=alphanumeric,
                    geolocation=geolocation, 
                    image_path= proxyConfig["ImageDirectory"] + str(counter) + proxyConfig["ImageExtension"])
            alphanumeric += 1
            counter += 1