import math
def payload_drop_off(waypoints_file,payloads_file):
    #waypoints_file = 'Waypoints'
    #payloads_file = 'Payloads'
    R = 6371000.0
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

            if ln.startswith("Aircraft's_Velocity"):
                x = ln.split(" ")
                v_plane = float(x[2])

            if ln.startswith("Aircraft's_Altitude"):
                x = ln.split(" ")
                s = float(x[2])

            if ln.startswith("Wind_Speed"):
                x = ln.split(" ")
                w = float(x[2])

            if ln.startswith("Wind_Bearing"):
                x = ln.split(" ")
                wind_brng = float(x[2])

            if ln.startswith("Take_off_angle"):
                x = ln.split(" ")
                takeoff_angle = float(x[2])

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

        def DO_SET_SERVO(self, SerNo, PWM, lat, lon, alt):
            do_set_servo_id = 183
            self.param_to_mcommand(0, 3, do_set_servo_id, SerNo, PWM, 0, 0, lat, lon, alt, 1)

        def write(self, name='Waypoints+Payloads'):
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

    def Air_Drop_Coordinates(index, listname):
        i = listname[index]
        xlist = i.split(',') ##split payload drop lines to get lat, long and radius
        return xlist[0], xlist[1]

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

    def new_waypoint(lat1, long1, d, brng): #Calculate new waypoint using waypoint, distance and bearing
        brng = brng * (math.pi/180)
        lat1_r, long1_r = Convert(lat1, long1)
        lat2_r = math.asin(math.sin(lat1_r) * math.cos(d / R) + math.cos(lat1_r) * math.sin(d / R) * math.cos(brng))
        long2_r = long1_r + math.atan2((math.sin(brng) * math.sin(d / R) * math.cos(lat1_r)),(math.cos(d / R) - math.sin(lat1_r) * math.sin(lat2_r)))
        lat2, long2 = ReConvert(lat2_r, long2_r)
        brng = brng * (180/math.pi)
        return lat2, long2

    def add_PL_waypoints(LatPL, LongPL, d_drop):
        brng = wind_brng
        d_wp = 30
        Lat_drop,Long_drop = new_waypoint(LatPL,LongPL,d_drop,brng)
        wp3_lat,wp3_long = new_waypoint(Lat_drop,Long_drop,d_wp,brng)
        wp2_lat,wp2_long = new_waypoint(wp3_lat,wp3_long,d_wp,brng)
        wp1_lat,wp1_long = new_waypoint(wp2_lat,wp2_long,d_wp,brng - 90)

        my_mission.waypoint(wp1_lat,wp1_long, alt)
        my_mission.waypoint(wp2_lat,wp2_long, alt)
        my_mission.waypoint(wp3_lat,wp3_long, alt)
        my_mission.waypoint(Lat_drop,Long_drop, alt)
        my_mission.DO_SET_SERVO(5, 1100, Lat_drop, Long_drop, alt)

    def payload_drop_eq (v_plane, s, w):
        g = 9.81 #Gravity
        PL_mass = 0.5 #Payload's Mass (kg)
        PL_mass_lbs = 2.20462262*PL_mass #Payload's Mass (lbs)
        PL_d = 0.07 #Payload's diameter
        PL_dsq = PL_d*PL_d #Payload's diameter squared
        PL_dsqf = PL_dsq*10.7639 #Payload's diameter squared (ft)
        PL_area = 0.001442 #Payload's Area (m^2)
        Drag_coeff = 0.47 #Coefficient of Drag
        roh = 1.275 #Density of air
        muz_v = v_plane*3.28084 #Muzzle speed (ft/s)

        x=0.0
        y=0.0
        z = 0.0

        v_z=0.0
        a_z=0

        fdz = 0.0
        fg = 0.0

        inc = 0.0
        time=0.0

        f_sum=0.0

        # at z-axi.s
        while ( z <= s ):
            f_sum = (0.5*roh*v_z*v_z*Drag_coeff*PL_area) + (PL_mass*g) # net forces= drag + force gravity
            a_z=f_sum/PL_mass
            z=z+v_z*0.01+0.5*a_z*0.01*0.01
            v_z = v_z + a_z * 0.01
            inc=inc+0.01

        #at x-axis direction
        time = inc
        v_proj=v_plane
        fdx=-0.5*roh*PL_area*Drag_coeff*v_proj*v_proj
        a=fdx/PL_mass

        while (inc >= 0):
            v_proj=v_proj+a*0.01
            fdx=-0.5*roh*PL_area*Drag_coeff*v_proj*v_proj
            a=fdx/PL_mass
            x=x+v_proj*0.01+0.5*(0.01*0.01)*a
            inc = inc - 0.01

        #print("time =",time)

        #at y-axis
        t=0.01
        y=0.0
        vy=0.0
        while (t<=time):
            # a=(0.5*roh*w_meter*w_meter*PL_area*Drag_coeff)/PL_mass+0.5*roh*vy*vy*PL_area*Drag_coeff/PL_mass
            # vy=vy+a*t
            y = y + (0.3048*0.000067*w*(PL_dsqf*PL_dsqf)*t*t*muz_v*Drag_coeff)/PL_mass
            t=t+0.01

        #print("x =",x)
        #print("y =",y)
        return x, y


    drop_x, drop_y = payload_drop_eq (v_plane, s, w)

    my_mission = automission('plane')
    WpsList, WpsNo = WP_FileList(waypoints_file)
    PL_List, PL_No = FileList(payloads_file)

    pll =[]
    min_id_wp = []
    for x in range (PL_No + 1):
        id_wp = []
        dist = []
        PL_Lat, PL_Long = Air_Drop_Coordinates(x, PL_List)
        pll.append(x)

        for y in range (WpsNo + 1):
            LatA, LongA, AltA = Waypoint_Coordinates(y,WpsList) #get coordinates of first waypoint
            d_PL_Wp = distance(PL_Lat,PL_Long,LatA,LongA)
            dist.append(d_PL_Wp)
            id_wp.append(y)
        wp_dist = [list(x) for x in zip(id_wp, dist)]
        #print(wp_dist)

        for distt in sorted(wp_dist,key=lambda l:l[1]):
            min_dist = distt[1]
            min_id_wp.append(distt[0])
            break
        #print(min_dist)
        #print(min_id_wp,'\n')

    min_pl_wp = [list(x) for x in zip(pll, min_id_wp)]
    #print(min_pl_wp)

    min_pl_wp_sort = sorted(min_pl_wp,key=lambda l:l[1])
    #print(min_pl_wp_sort)

    LatA, LongA, AltA = Waypoint_Coordinates(0, WpsList) #get coordinates of first waypoint
    my_mission.takeoff(takeoff_angle, LatA, LongA, AltA)
    for d in range (1, WpsNo + 1):
        LatB, LongB, AltB = Waypoint_Coordinates(d, WpsList) #get coordinates of second waypoint
        my_mission.waypoint(LatB, LongB, AltB)
        for f in min_pl_wp_sort:
            if d == f[1]:
                PL_Lat, PL_Long = Air_Drop_Coordinates(f[0], PL_List)
                add_PL_waypoints(PL_Lat, PL_Long, drop_x)

    my_mission.write()
    return 'Waypoints+Payloads'
