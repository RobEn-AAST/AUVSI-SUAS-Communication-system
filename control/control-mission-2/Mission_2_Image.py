from __future__ import print_function
import time
from dronekit import connect, Command, VehicleMode, LocationGlobal
from pymavlink import mavutil, mavwp
import math
import Obs_Avoid_Module
import Survey_Module

R = 6371000.0  #Earth radius in meters
Pa = 30 #Pitch Angle in degrees
with open("/home/proxyServer/files/Data.txt","r") as data:
    for ln in data:
        if ln.startswith("home_lat"):
            x = ln.split(" ")
            home_lat = float(x[2])

        if ln.startswith("home_long"):
            x = ln.split(" ")
            home_long = float(x[2])

        if ln.startswith("home_ASL"):
            x = ln.split(" ")
            home_ASL = float(x[2])

        if ln.startswith("Bearing"):
            x = ln.split(" ")
            main_bearing = float(x[2])

        if ln.startswith("Altitude"):
            x = ln.split(" ")
            alt = float(x[2])

        if ln.startswith("waypoints_file"):
            x = ln.split(" ")
            waypoints_file = "/home/proxyServer/files/" + x[2].replace('"','').strip()

        if ln.startswith("obstacles_file"):
            x = ln.split(" ")
            obstacles_file = "/home/proxyServer/files/" + x[2].replace('"','').strip()

        if ln.startswith("payloads_file"):
            x = ln.split(" ")
            payloads_file = "/home/proxyServer/files/" + x[2].replace('"','').strip()

        if ln.startswith("searchgrid_file"):
            x = ln.split(" ")
            searchgrid_file = "/home/proxyServer/files/" + x[2].replace('"','').strip()

# Use UDP to connect to the SITL simulator through the local port 14551
connection_string ='udpin:0.0.0.0:5750' #'tcp:127.0.0.1:5760'  #
print('Connecting to vehicle on: %s' % connection_string)
# The connect function will return an object of type Vehicle, which is the vehicle here
vehicle = connect(connection_string, wait_ready=True)

def readmission(aFileName): #Load a mission from a file into a list
    print("\nReading mission from file: %s" % aFileName)
    cmds = vehicle.commands
    missionlist = []
    with open(aFileName) as f:
        for i, line in enumerate(f):
            if i == 0:
                if not line.startswith('QGC WPL 110'):
                    raise Exception('File is not supported WP version')
            else:
                linearray = line.split('\t')
                ln_index = int(linearray[0])
                ln_currentwp = int(linearray[1])
                ln_frame = int(linearray[2])
                ln_command = int(linearray[3])
                ln_param1 = float(linearray[4])
                ln_param2 = float(linearray[5])
                ln_param3 = float(linearray[6])
                ln_param4 = float(linearray[7])
                ln_param5 = float(linearray[8])
                ln_param6 = float(linearray[9])
                ln_param7 = float(linearray[10])
                ln_autocontinue = int(linearray[11].strip())
                cmd = Command(0, 0, 0, ln_frame, ln_command, ln_currentwp, ln_autocontinue, ln_param1, ln_param2,
                              ln_param3, ln_param4, ln_param5, ln_param6, ln_param7)
                missionlist.append(cmd)
    return missionlist

def FileList(filename): #Enumerate lines of file and add them to a list
    file = open(filename)
    list = []
    for i, line in enumerate(file):
        list.append(line)
    return list, i

def upload_mission(aFileName): #Upload a mission from a file
    missionlist = readmission(aFileName) # Read mission from file
    print("\nUpload mission from a file: %s" % aFileName)
    print(' Clear mission')
    cmds = vehicle.commands
    cmds.clear() # Clear existing mission from vehicle
    # Add new mission to vehicle
    for command in missionlist:
        cmds.add(command)
    print(' Upload mission')
    vehicle.commands.upload()

def download_mission(): #Downloads the current mission and returns it in a list
    #It is used in save_mission() to get the file information to save
    print(" Download mission from vehicle")
    missionlist = []
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    for cmd in cmds:
        missionlist.append(cmd)
    return missionlist

def save_mission(aFileName): #Save a mission in the Waypoint file format
    print("\nSave mission from Vehicle to file: %s" % aFileName)
    missionlist = download_mission() #Download mission from vehicle
    # Add file-format information
    output = 'QGC WPL 110\n'
    home = vehicle.home_location #Add home location as 0th waypoint
    output += "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (0, 1, 0, 16, 0, 0, 0, 0, home.lat, home.lon, home.alt, 1)
    # Add commands
    for cmd in missionlist:
        commandline = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
        cmd.seq, cmd.current, cmd.frame, cmd.command, cmd.param1, cmd.param2, cmd.param3, cmd.param4, cmd.x, cmd.y,
        cmd.z, cmd.autocontinue)
        output += commandline
    with open(aFileName, 'w') as file_:
        print(" Writing mission to file")
        file_.write(output)

def printfile(aFileName): #Print a mission file to demonstrate "round trip"
    print("\nMission file: %s" % aFileName)
    with open(aFileName) as f:
        for line in f:
            print(' %s' % line.strip())

def Convert(lat, lon): #Convert LAT & LONG from degree to radian
    lat = float(lat) * math.pi / 180
    lon = float(lon) * math.pi / 180
    return lat, lon

def ReConvert(lat, lon): #Convert LAT & LONG from radian to degree
    lat = float(lat) * 180 / math.pi
    lon = float(lon) * 180 / math.pi
    return lat, lon

def new_waypoint(lat1, long1, d, brng): #Calculate new waypoint using waypoint, distance and bearing
    brng = brng * (math.pi/180)
    lat1_r, long1_r = Convert(lat1, long1)
    lat2_r = math.asin(math.sin(lat1_r) * math.cos(d / R) + math.cos(lat1_r) * math.sin(d / R) * math.cos(brng))
    long2_r = long1_r + math.atan2((math.sin(brng) * math.sin(d / R) * math.cos(lat1_r)),(math.cos(d / R) - math.sin(lat1_r) * math.sin(lat2_r)))
    lat2, long2 = ReConvert(lat2_r, long2_r)
    brng = brng * (180/math.pi)
    return lat2, long2

def landing_sequence(): #Create Landing Sequence
    brng = main_bearing
    alt_total = 70
    land_points_total = alt_total/10
    land_dist_total = 350
    cmd_land = Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0, 0, 0, 0, home_lat, home_long, 0)

    brng = brng - 180
    land_lat_1, land_long_1 = new_waypoint(home_lat, home_long, land_dist_total, brng)
    cmd_land_1 = Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, land_lat_1, land_long_1, 70)
    cmds.add(cmd_land_1)

    brng = brng + 180
    alt1_land = 60
    land_step_dist_1 = 50
    dist1 = land_step_dist_1
    for i in range(3):
        xi, yi = new_waypoint(land_lat_1, land_long_1 , dist1, brng)
        cmd_land_i = Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, xi, yi, alt1_land)
        dist1 = dist1 + land_step_dist_1
        alt1_land = alt1_land - 10
        cmds.add(cmd_land_i)

    alt2_land = 30
    land_step_dist_2 = 50
    dist2 = land_step_dist_2
    for j in range(3):
        xj, yj = new_waypoint(xi, yi, dist2, brng)
        cmd_land_j = Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, xj, yj, alt2_land)
        dist2 = dist2 + land_step_dist_2
        alt2_land = alt2_land - 10
        cmds.add(cmd_land_j)

    cmds.add(cmd_land)

Modified_Waypoints_file = Obs_Avoid_Module.obstacle_avoidance(waypoints_file, obstacles_file)
Modified_Waypoints_file2 = Survey_Module.survey_search_grid(Modified_Waypoints_file, searchgrid_file)

import_mission_filename = Modified_Waypoints_file2 + ".txt"
export_mission_filename = '/home/proxyServer/files/Exported_Mission.txt'

upload_mission(import_mission_filename) #Upload mission from file

cmds = vehicle.commands
cmds.download()
cmds.wait_ready()

landing_sequence()

cmds.upload()  # Send commands

save_mission(export_mission_filename) #Download mission we just uploaded and save to a file

#time.sleep(30) #Same as before, delay 30s

vehicle.close() #Before exiting, clear the vehicle object

printfile(export_mission_filename)
