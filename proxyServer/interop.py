from threading import TIMEOUT_MAX
from time import time
from auvsi_suas.proto import interop_api_pb2
from urllib import request
from re import findall
import functools
from cv2 import imencode
import json
import requests
from google.protobuf import json_format

class interop_client(object):
    __responses = {
        200 : ("The request was successful","no action needed"),
        400 : ("The request was bad/invalid","Check the contents of the request"),
        401 : ("The request is unauthorized","check the login credentials"),
        403 : ("The request is forbidden","check that you are not sending to admin page"),
        404 : ("The request was made to an invalid URL","check the URL string"),
        405 : ("The request used an invalid method","check whether you are using a get request or a post request"),
        500 : ("The server encountered an internal error","report what happened to the judges")
    }

    def __init__(self,
                 url,
                 username,
                 password,                 
                 max_concurrent=128,
                 timeout=10,
                 max_retries=10):
        self.url = url
        self.username = username
        self.password = password
        self.timeout = timeout
        creds = interop_api_pb2.Credentials()
        creds.username = username
        creds.password = password
        self.session = requests.Session()
        self.session.mount(
            'http://', 
            requests.adapters.HTTPAdapter(pool_maxsize=max_concurrent,
                                                     max_retries=max_retries)
            )
        self.session.post(self.url + '/api/login', timeout=self.timeout, data=json_format.MessageToJson(creds))
    
    def is_alive(self):
        result = request.urlopen("http://" + self.ipadress + ":" + self.port).getcode()
        return True if result == 200 else False, result


    def get_teams(self):
        return self.__this_client.get_teams()

    def get_mission(self, mission):
        r = self.session.get(self.url + '/api/missions/' + str(mission))
        response = json.loads(r.text)
        waypoints = []
        payloads = []
        obstacles = []
        flyZones = []
        searchArea = []
        if(type(response["waypoints"]) is dict):
            waypoints.append(str(counter) + "\t0\t0\t16\t0\t0\t0\t0\t" + str(response["waypoints"]["latitude"]) + "\t" + str(response["waypoints"]["longitude"]) + "\t" + str(response["waypoints"]["altitude"]) + "\t1")
        else:
            counter = 1    
            for waypoint in response["waypoints"]:
                waypoints.append(str(counter) + "\t0\t0\t16\t0\t0\t0\t0\t" + str(waypoint["latitude"]) + "\t" + str(waypoint["longitude"]) + "\t" + str(waypoint["altitude"]) + "\t1")
                counter +=1
        if(type(response["airDropPos"]) is dict):
            payloads.append(str(response["airDropPos"]["latitude"]) + "," + str(response["airDropPos"]["longitude"]))
        else:
            for payload in response["airDropPos"]:
                payloads.append(str(payload["latitude"]) + "," + str(payload["longitude"]))
        if(type(response["stationaryObstacles"]) is dict):
            payloads.append(str(response["stationaryObstacles"]["latitude"]) + "," + str(response["stationaryObstacles"]["longitude"]) + str(response["stationaryObstacles"]["radius"]))
        else:
            for obstacle in response["stationaryObstacles"]:
                obstacles.append(str(obstacle["latitude"]) + "," + str(obstacle["longitude"]) + "," + str(obstacle["radius"]))
        if(type(response["flyZones"][0]["boundaryPoints"]) is dict):
            payloads.append(str(response["flyZones"][0]["boundaryPoints"]["latitude"]) + "," + str(response["flyZones"][0]["boundaryPoints"]["longitude"]))
        else:
            for flyZone in response["flyZones"][0]["boundaryPoints"]:
                flyZones.append(str(flyZone["latitude"]) + "," + str(flyZone["longitude"]))
        if(type(response["searchGridPoints"]) is dict):
            payloads.append(str(response["searchGridPoints"]["latitude"]) + "," + str(response["searchGridPoints"]["longitude"]))
        else:
            for searchPoint in response["searchGridPoints"]:
                searchArea.append(str(searchPoint["latitude"]) + "," + str(searchPoint["longitude"]))
        return waypoints, payloads, obstacles, flyZones, searchArea
    
    def send_telemtry(self, telem):
        self.session.post(self.url + '/api/telemetry', data=json_format.MessageToJson(telem))

    def send_standard_object(self,
    mission,
    geolocation,
    text,
    image,
    orientation = interop_api_pb2.Odlc.N,
    shape = interop_api_pb2.Odlc.SQUARE,
    shape_color = interop_api_pb2.Odlc.BLACK,
    text_color= interop_api_pb2.Odlc.BLACK):
        object_of_interset = interop_api_pb2.Odlc()
        object_of_interset.type = interop_api_pb2.Odlc.STANDARD
        object_of_interset.latitude = geolocation[0]
        object_of_interset.longitude = geolocation[1]
        object_of_interset.orientation = orientation
        object_of_interset.shape = shape
        object_of_interset.shape_color = shape_color
        object_of_interset.alphanumeric = text
        object_of_interset.alphanumeric_color = text_color
        object_of_interset.autonomous = True
        object_of_interset.mission = mission
        #object_of_interset = self.__this_client.post_odlc(object_of_interset)
        r = self.session.post(self.url + '/api/odlcs', data=json_format.MessageToJson(object_of_interset))
        res = interop_api_pb2.Odlc()
        json_format.Parse(r.text, res)
        self.session.put(self.url + '/api/odlcs/%d/image' % res.id, data=image)

    def send_emergant_object(self,mission,latitude,longitude,image_path,description = None):
        object_of_interset = interop_api_pb2.Odlc()
        object_of_interset.mission = mission
        object_of_interset.type = 4
        object_of_interset.latitude = latitude
        object_of_interset.longitude = longitude
        if description != None:
            object_of_interset.description = description
        object_of_interset.autonomous = True
        object_of_interset = self.__this_client.post_odlc(object_of_interset)
        with open(image_path, 'rb') as f:
            image_data = f.read()
            self.__this_client.put_odlc_image(object_of_interset.id, image_data)



if __name__ == '__main__':
    home = {
        "latitude": 0,
        "longitude": 0,
        "altitude": 0
    }
    myclient = interop_client('164.92.120.251','8000','dragobots','P@ssw0rd') 
    waypoints, payloads, obstacles, flyZones, searchArea = myclient.get_mission(1)
    with open('Waypoints.txt', 'w') as f:
        f.write('QGC WPL 110')
        f.write('\n')
        for line in waypoints:
            f.write(line)
            f.write('\n')
    with open('Payloads.txt', 'w') as f:
        for line in payloads:
            f.write(line)
            f.write('\n')
    with open('Obstacles.txt', 'w') as f:
        for line in obstacles:
            f.write(line)
            f.write('\n')
    with open('GeoFence.txt', 'w') as f:
        for line in flyZones:
            f.write(line)
            f.write('\n')
    with open('SearchArea.txt', 'w') as f:
        for line in searchArea:
            f.write(line)
            f.write('\n')