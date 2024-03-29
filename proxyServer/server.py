#!/usr/bin/env python3
# CLI for interacting with interop server.
from __future__ import print_function
from configparser import ConfigParser
from interop import interop_client
from flask import Flask, request, send_file, render_template, abort
from os import system
from os.path import exists
from json import dump, loads
config = ConfigParser()
config.readfp(open('/home/proxyServer/config/system.config', 'r'))
Interop_config = config["Interop"]

interopEnabled = Interop_config["enabled"] == 1
interopClient = None

if interopEnabled:
    interopClient = interop_client(
                                url=Interop_config["url"], 
                                username=Interop_config["username"],
                                password=Interop_config["password"])

missionCounter = 0
app = Flask(__name__)

@app.route('/startmission/', methods=["POST"])
def startMission():
    if interopEnabled == False:
        return "Interop Disabled"
    
    data = dict(request.form)
    print(data)
    waypoints, payloads, obstacles, flyZones, searchArea = interopClient.get_mission(data["mission"])
    with open('/home/proxyServer/files/Waypoints.txt', 'w') as f:
        for line in waypoints:
            f.write(line)
            f.write('\n')
    with open('/home/proxyServer/files/Payloads.txt', 'w') as f:
        for line in payloads:
            f.write(line)
            f.write('\n')
    with open('/home/proxyServer/files/Obstacles.txt', 'w') as f:
        for line in obstacles:
            f.write(line)
            f.write('\n')
    with open('/home/proxyServer/files/GeoFence.txt', 'w') as f:
        for line in flyZones:
            f.write(line)
            f.write('\n')
    with open('/home/proxyServer/files/SearchGrid.txt', 'w') as f:
        for line in searchArea:
            f.write(line)
            f.write('\n')
    if(data["type"] == '0'):
        system("python /home/proxyServer/control/control-mission-1/Mission_1_Payload.py")
    elif (data["type"] == '1'):
        system("python /home/proxyServer/control/control-mission-2/Mission_2_Image.py")
    return "success"

@app.route('/submitMission/<number>', methods= ["POST"])
def submitMission(number):
    if interopEnabled == False:
        return "Interop Disabled"
    
    request.get_data()
    image = request.files["image"]
    mission = dict(request.form)
    interopClient.send_standard_object(
        mission=int(number),
        geolocation= (float(mission["lat"]), float(mission["long"])),
        text= mission["text"],
        image= image
        )
    return "success"

@app.route('/getMission/image/<number>')
def getMissionImage(number):
    path = "/home/proxyServer/missions/images/" + str(number) + ".jpeg"
    if exists(path) == False:
        return abort(404)
    return send_file(path)

@app.route('/getMission/geoLocation/<number>')
def getMissionGeoLocation(number):
    path = "/home/proxyServer/missions/geolocations/" + str(number) + ".json"
    if exists(path) == False:
        return abort(404)
    return send_file(path)


@app.route('/sendMission', methods=['POST'])
def ReceiveStream():
    global missionCounter
    geoLocation = loads(request.args.get('geoLocation'))
    image = request.files['image']
    image.save("/home/proxyServer/missions/images/" + str(missionCounter) + ".jpeg")
    # Save query parameters to a JSON file
    with open("/home/proxyServer/missions/geolocations/" + str(missionCounter) + ".json", 'w') as file:
        dump(geoLocation, file)
    missionCounter += 1
    return "success"
    
    
@app.route('/')
def index():
    return render_template("load_mission.html")

if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)
