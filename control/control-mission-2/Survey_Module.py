import math
def survey_search_grid(waypoints_file, searchgrid_file):
    #waypoints_file = 'Waypoints'
    #searchgrid_file = 'SearchGrid'
    R = 6371000.0  #Earth radius in meters
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

            if ln.startswith("Take_off_angle"):
                x = ln.split(" ")
                takeoff_angle = float(x[2])

            if ln.startswith("Take_off_alt"):
                x = ln.split(" ")
                takeoff_alt = float(x[2])

            if ln.startswith("Survey_Altitude"):
                x = ln.split(" ")
                survey_alt = float(x[2])

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

        def write(self, name='Survey'):
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

    def SearchGrid_Coordinates(index, listname):
        i = listname[index]
        xlist = i.split(',') #split obstacle lines to get lat, long and radius
        return xlist[0].strip(), xlist[1].strip() #lat[0] long[1] alt[2]

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

    my_mission = automission('plane')
    WpsList, WpsNo = WP_FileList(waypoints_file)
    GridList, GridNo = FileList(searchgrid_file)

    min_y = 0
    for x in range(GridNo + 1):
        GridLat, GridLong = SearchGrid_Coordinates(x, GridList)
        for y in range(WpsNo + 1):
            LatA, LongA, AltA = Waypoint_Coordinates(y, WpsList) #get coordinates of first waypoint
            dist = distance(LatA, LongA, GridLat, GridLong)
            if y == 0:
                min_dist = dist
            if dist < min_dist:
                min_dist = dist
                min_y = y

    LatA, LongA, AltA = Waypoint_Coordinates(0, WpsList) #get coordinates of first waypoint
    my_mission.takeoff(takeoff_angle, LatA, LongA, AltA)
    for d in range (1, WpsNo + 1):
        LatB, LongB, AltB = Waypoint_Coordinates(d, WpsList) #get coordinates of second waypoint
        my_mission.waypoint(LatB, LongB, AltB)
        if d == min_y:
            for i in range(GridNo + 1):
                GridLat, GridLong = SearchGrid_Coordinates(i, GridList)
                my_mission.waypoint(GridLat, GridLong, survey_alt)
    my_mission.write()
    return 'Survey'
