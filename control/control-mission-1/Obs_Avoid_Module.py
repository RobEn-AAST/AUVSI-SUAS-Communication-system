import math
def obstacle_avoidance(waypoints_file, obstacles_file):
    #waypoints_file = 'Waypoints'
    #obstacles_file = 'Obstacles'
    R = 6371000.0  #Earth radius in meters
    safe_dist = 2
    with open("/home/proxyServer/control/control-mission-1/Data.txt","r") as data:
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

            if ln.startswith("Take_off_angle"):
                x = ln.split(" ")
                takeoff_angle = float(x[2])

            if ln.startswith("Take_off_alt"):
                x = ln.split(" ")
                takeoff_alt = float(x[2])

    class automission(object):
        # docstring for automission
        def __init__(self, vehicle_type):

            super(automission, self).__init__()
            assert vehicle_type == 'plane'
            self.mlist = []  # each element of the array represents a command, ie waypoint, with its parameters
            self.counter = 1

            # these two lines are by default, exists every mission planner file
            self.mlist.append(f"QGC WPL 110\n0\t1\t0\t16\t0\t0\t0\t0\t{home_lat}\t{home_long}\t{home_ASL}\t1\n") # Current Home Location

        def param_to_mcommand(self,
                              *args):  # takes command and its parameters, appends them to mlist while adjusting formatting
            string = str(self.counter) + '\t'
            self.counter += 1

            for i in args:
                string += str(i) + '\t'
            string = string.rstrip('\t')
            string += '\n'
            self.mlist.append(string)

        ### Mission Commands ###
        # every parameter list begins with '0,3,' and ends with ',1'

        def waypoint(self, lat, lon, alt, delay=0):
            waypoint_id = 16
            self.param_to_mcommand(0, 3, waypoint_id, delay, 0, 0, 0, lat, lon, alt, 1)

        def takeoff(self, angle, lat, lon, alt):
            takeoff_id = 22
            self.param_to_mcommand(0, 3, takeoff_id, angle, 0, 0, 0, lat, lon, alt, 1)

        def write(self, name='Evasion'):
            # saves final command list mlist as WP file.
            # Missionplanner can direcly open this text document in flight plan / load WP file button
            # open(str(name)+".waypoints", 'w').close()
            with open(str(name) + ".txt", "w") as text_file:
                for i in self.mlist:
                    print(i)
                    text_file.write(i)

    def WP_FileList(filename): #Enumerate lines of waypoint file and add them to a list
        filename = filename + '.txt' #waypoint file as text
        file = open(filename)
        list = []
        for i, line in enumerate(file):
            if i<2: #to disregard adding 'QGC WPL 110' line & home line to list
                continue
            else:
                list.append(line) #adding waypoints to list
        i = i-2 #to disregard counting 'QGC WPL 110' line & home line in file
        return list, i

    def FileList(filename): #Enumerate lines of file and add them to a list
        filename = filename + '.txt' #obstacles/payloads file as text
        file = open(filename)
        list = []
        for i, line in enumerate(file):
            list.append(line) #adding obstacles/payloads to list
        return list, i

    def Waypoint_Coordinates(index, listname):
        i = listname[index]
        xlist = i.split() #split waypoint lines to get lat and long
        return xlist[8], xlist[9], xlist[10] #lat[8] long[9] alt[10]

    def Obstacle_Coordinates_Radius(index, listname):
        i = listname[index]
        xlist = i.split(',') ##split obstacle lines to get lat, long and radius
        return xlist[0], xlist[1], xlist[2]

    def Convert(lat, lon): #Convert LAT & LONG from degree to radian
        lat = float(lat) * math.pi / 180
        lon = float(lon) * math.pi / 180
        return lat, lon

    def ReConvert(lat, lon): #Convert LAT & LONG from radian to degree
        lat = float(lat) * 180 / math.pi
        lon = float(lon) * 180 / math.pi
        return lat, lon

    def distance(LatA, LongA, LatB, LongB): #Get distance between 2 points
        LatA_r, LongA_r = Convert(LatA, LongA)
        LatB_r, LongB_r = Convert(LatB, LongB)
        LatAB_r = LatB_r - LatA_r
        LongAB_r = LongB_r - LongA_r
        a = ((math.sin(LatAB_r / 2)) * (math.sin(LatAB_r / 2))) + math.cos(LatA_r) * math.cos(LatB_r) * ((math.sin(LongAB_r / 2)) * (math.sin(LongAB_r / 2)))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = R * c
        return (d)

    def get_bearing(lat1, long1, lat2, long2): #get bearing between 2 points
        lat1_r, long1_r = Convert(lat1, long1)
        lat2_r, long2_r = Convert(lat2, long2)
        y = math.sin(long2_r - long1_r) * math.cos(lat2_r)
        x = math.cos(lat1_r) * math.sin(lat2_r) - math.sin(lat1_r) * math.cos(lat2_r) * math.cos(long2_r - long1_r)
        i = math.atan2(y, x)
        bearing = (i * 180 / math.pi + 360) % 360
        return bearing

    def new_waypoint(lat1, long1, d, brng): #Calculate new waypoint using waypoint, distance and bearing
        brng = brng * (math.pi/180)
        lat1_r, long1_r = Convert(lat1, long1)
        lat2_r = math.asin(math.sin(lat1_r) * math.cos(d / R) + math.cos(lat1_r) * math.sin(d / R) * math.cos(brng))
        long2_r = long1_r + math.atan2((math.sin(brng) * math.sin(d / R) * math.cos(lat1_r)),(math.cos(d / R) - math.sin(lat1_r) * math.sin(lat2_r)))
        lat2, long2 = ReConvert(lat2_r, long2_r)
        brng = brng * (180/math.pi)
        return lat2, long2

    def check_2nd_time(x1, y1, z1, x2, y2, z2, yy): #
        print("\n")
        for y in range(ObsNo + 1):
            if y != yy:
                ObsLat, ObsLong, ObsRad = Obstacle_Coordinates_Radius(y, ObsList)
                ObsRad = float(ObsRad)
                dAB = distance(x1, y1, x2, y2)  #total distance from A to B
                dAob = distance(x1, y1, ObsLat, ObsLong)  #distance from A to Obstacle
                dobB = distance(ObsLat, ObsLong, x2, y2)  #distance from Obstacle to B
                brngAB = get_bearing(x1, y1, x2, y2)   #bearing between A and B
                brngBA = brngAB - 180   #bearing between B and A
                brngobs = brngAB - 90   #bearing of obs (perpendicular to AB bearing)
                brngAob = get_bearing(x1, y1, ObsLat, ObsLong) #bearing between A and Obstacle
                brngobA = get_bearing(ObsLat, ObsLong, x1, y1)  #bearing between Obstacle and A
                brngobB = get_bearing(ObsLat, ObsLong, x2, y2)  #bearing between Obstacle and B

                if brngAB > brngAob:
                    brng = brngAB - brngAob
                else:
                    brng = brngAob - brngAB

                L = dAob * math.sin(brng*(math.pi/180))

                if (brng <= 270 and brng >= 90 ) or (L >= (safe_dist * ObsRad)) or (dAob > dAB):
                    print("re Obs",y,"--> No Effect")

                else:
                    print("re Obs",y,"--> Effect")
                    add_obs_waypoints(x1, y1, z1, x2, y2, z2, ObsLat, ObsLong, ObsRad, brngAB, brngBA, brngobs, dAob, dobB, y)
            else:
                    continue

    def add_obs_waypoints(LatA, LongA, AltA, LatB, LongB, AltB, ObsLat, ObsLong, ObsRad, brngAB, brngBA, brngobs, dAob, dobB, y):
        d3 = ObsRad * (safe_dist)
        x2, y2 = new_waypoint(ObsLat, ObsLong, d3, brngobs)
        check_2nd_time(LatA, LongA, AltA, x2, y2, AltA, y)
        check_2nd_time(x2, y2, AltB, LatB, LongB, AltB, y)
        my_mission.waypoint(x2, y2, AltA)

    def take_off_sequence():
        brng = main_bearing
        take_off_lat, take_off_long = new_waypoint(home_lat, home_long, 1, brng)
        my_mission.takeoff(takeoff_angle, take_off_lat, take_off_long, takeoff_alt)


    my_mission = automission('plane')
    WpsList, WpsNo = WP_FileList(waypoints_file)
    ObsListo, ObsNoo = FileList(obstacles_file)

    take_off_sequence()

    #Create new obstacle file to add obstacles with close proximity to each other as one
    with open(obstacles_file + 'edited.txt', "a+") as f:
        f.seek(0) #point at beginning of file
        f.truncate()
        flag = 0
        for i in range (ObsNoo):
            if flag == 1:
                flag = 0 #reintialize the flag to zero after adding past obstacles
                continue
            ObsLat, ObsLong, ObsRad = Obstacle_Coordinates_Radius(i, ObsListo) #get fist obstacle's lat,long and radius
            ObsRad = float(ObsRad)

            ObsLat2, ObsLong2, ObsRad2 = Obstacle_Coordinates_Radius(i+1, ObsListo) #get second obstacle's lat,long and radius
            ObsRad2 = float(ObsRad2)

            d_ob1_ob2 = distance(ObsLat, ObsLong, ObsLat2, ObsLong2) #distance between 2 obstacles
            brng_ob1_ob2 = get_bearing(ObsLat, ObsLong, ObsLat2, ObsLong2) #bearing between 2 obstacles
            if d_ob1_ob2 <= 100: #if distance is less that 30 m
                flag = flag + 1 #increment flag to indicate presence of 2 close obstacles
                m_d_ob1_ob2 = d_ob1_ob2/2  #get midpoint between the radii of the 2 obstacles (to be the new obstacle midpoint)
                ObsLat_new, ObsLong_new = new_waypoint(ObsLat, ObsLong, m_d_ob1_ob2, brng_ob1_ob2) #add new combined obstacle
                ObsRad_new = ObsRad + ObsRad2 #new obstacle's radius as sum of both radii
                #write new obstacle data to new file
                f.write(str(ObsLat_new))
                f.write(",")
                f.write(str(ObsLong_new))
                f.write(",")
                f.write(str(ObsRad_new))

            else:
                #write existing obstacle data to new file
                f.write(str(ObsLat))
                f.write(",")
                f.write(str(ObsLong))
                f.write(",")
                f.write(str(ObsRad))
            if i < ObsNoo:
                f.write("\n")

        #add last obstacle to new obstacle file
        ObsLat, ObsLong, ObsRad = Obstacle_Coordinates_Radius(ObsNoo, ObsListo)
        ObsRad = float(ObsRad)
        f.write(str(ObsLat))
        f.write(",")
        f.write(str(ObsLong))
        f.write(",")
        f.write(str(ObsRad))

    ObsList, ObsNo = FileList(obstacles_file + 'edited')

    for x in range(WpsNo):
        print("\n")
        print("Between Wp",x,"and Wp",x+1)
        LatA, LongA, AltA = Waypoint_Coordinates(x, WpsList) #get coordinates of first waypoint
        LatB, LongB, AltB = Waypoint_Coordinates(x+1, WpsList) #get coordinates of first waypoint

        my_mission.waypoint(LatA, LongA, AltA)
        for y in range(ObsNo + 1):
            ObsLat, ObsLong, ObsRad = Obstacle_Coordinates_Radius(y, ObsList) #get obstacle's lat,long and radius
            ObsRad = float(ObsRad)
            dAB = distance(LatA, LongA, LatB, LongB)  #total distance from A to B
            dAob = distance(LatA, LongA, ObsLat, ObsLong)  #distance from A to Obstacle
            dobB = distance(ObsLat, ObsLong, LatB, LongB)  #distance from Obstacle to B
            brngAB = get_bearing(LatA, LongA, LatB, LongB) #bearing between A and B
            brngBA = brngAB - 180 #bearing between B and A
            brngobs = brngAB - 90 #bearing of obs (perpendicular to AB bearing)
            brngAob = get_bearing(LatA, LongA, ObsLat, ObsLong) #bearing between A and Obstacle
            brngobA = get_bearing(ObsLat, ObsLong, LatA, LongA) #bearing between Obstacle and A
            brngobB = get_bearing(ObsLat, ObsLong, LatB, LongB) #bearing between Obstacle and B

            if brngAB > brngAob:
                brng = brngAB - brngAob
            else:
                brng = brngAob - brngAB

            L = dAob * math.sin(brng*(math.pi/180))

            if (brng <= 270 and brng >= 90 ) or (L >= (safe_dist * ObsRad)) or (dAob > dAB):
                print("Obs",y,"--> No Effect")

            else:
                print("Obs",y,"--> Effect")
                add_obs_waypoints(LatA, LongA, AltA, LatB, LongB, AltB, ObsLat, ObsLong, ObsRad, brngAB, brngBA, brngobs, dAob, dobB, y)

    my_mission.waypoint(LatB, LongB, AltB) #add last waypoint to output file
    my_mission.write()
    return 'Evasion'
