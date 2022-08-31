#!/usr/bin/env python3
# CLI for interacting with interop server.
from __future__ import print_function
from copyreg import pickle
import logging
import time
import threading
from pymavlink import mavutil
from auvsi_suas.client.client import AsyncClient
from auvsi_suas.proto.interop_api_pb2 import Mission, Telemetry
from configparser import ConfigParser
from interop import interop_client
from flask import Flask, request
import pickle

config = ConfigParser()
config.readfp(open('/home/proxyServer/config/system.config', 'r'))
Interop_config = config["Interop"]


interopClient = interop_client(
                            url=Interop_config["url"], 
                            username=Interop_config["username"],
                            password=Interop_config["password"])

app = Flask(__name__)

@app.route('/startmission/')
def startMission():
    waypoints, payloads, obstacles, flyZones, searchArea = interopClient.get_mission(1)
    with open('/home/proxyServer/files/Waypoints.txt', 'w') as f:
        f.write('QGC WPL 110')
        f.write('\n')
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
    with open('/home/proxyServer/files/SearchArea.txt', 'w') as f:
        for line in searchArea:
            f.write(line)
            f.write('\n')
    return "success"

@app.route('/submitMission/<number>')
def submitMission(number):
    image = request.files["image"]
    mission = request.data
    interopClient.send_standard_object(
        number,
        geolocation= mission["geolocation"],
        text= mission["text"],
        image= image
        )
    return "success"

@app.route('/getMission/<number>')
def getMission(number):
    with open("missionPool/" + str(number) + ".bin", "rb") as outfile:
        mission = outfile.read()
    return mission

if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)














