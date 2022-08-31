<h1 align="center"> UAV Interop system Client API</h1>


## Over View :
A library that provides an api for data exchange with the interop system

#### prequsites :-
- protoc binaries

### protoc binaries :-
- for windows
  - copy the protoc binaries folder in the place you want to keep it ( located in the repository ).
  - export this location to the path variable
        - toturial for exporting to path variable on windows : <a>https://www.youtube.com/watch?v=gb9e3m98avk</a>

- for linux there is a big chance its already installed so you can check using the following command.
```bash
protoc --version
```
if not you can install it using the following commands.
```bash
sudo apt-get install autoconf automake libtool curl make g++ unzip

git clone https://github.com/protocolbuffers/protobuf.git

cd protobuf

git submodule update --init --recursive

./autogen.sh

./configure

make

make check

sudo make install
 
sudo ldconfig
```

## client setup :-
- create the virtual enviroment using one of the following methods using pip installation.
```bash
conda create -n <environment-name> python=3.6.8

pip install -r requirements.txt
```
- activate the enviroment.
- enter the interop client library directory ( located inside the repository ) and run the following command.
 ```bash
python setup.py install 
```
- with the enviroment ready now you can add the following line to the code to import the interop system module.
 ```bash
from interop import interop_client
```

## usage :-
- create a client object.
  - object paramters are : 
    - ip address : <b>127.0.0.1</b> during testing
    - port number : <b>8000</b>
    - user name : <b>testuser</b> during testing and will be given to us during the compition by the judges
    - password : <b>testpass</b> during testing and will be given to us during the compition by the judges
  - create the client object using the following line.

```bash
myclientname = interop_client(ipadrress,port,username,password)
```
## features :-
1. attributes
    - ip address : string that represents the ipaddress of the interop server. ex: "10.10.130.2"
    - port number : string that represents the port number used to connect to the interop server. ex: "8000"
    - user name : string that represents the user name used to connect to the interop server. ex: "testuser"
    - password : string that represents the password used to connect to the interop server. ex: "testpass"
2. methods
    - is_alive() : check if the interop server is reachable or not.
    - send_standard_object(mission,latitude,longitude,orientation,shape,shape_color,letter,letter_color,image_path) : used to send standard objects found.
      - mission : integer representing the id of the mission.
      - latitude : integer representing the lattitude of the object.
      - longitude : integer representing the longitude of the object.
      - orientation : integer representing the orientation of the object.
      - shape : integer representing the shape of the object.
      - shape_color : integer representing the color of the object.
      - letter : character represeting the character detected in the object.
      - letter_color : character represeting the color of the character detected in the object.
      - image_path : string representing the path of the image object.
    - send_emergant_object(mission,latitude,longitude,image_path,description = None) : used to send emergant object.
      - mission : integer representing the id of the mission.
      - latitude : integer representing the lattitude of the object.
      - longitude : integer representing the longitude of the object.
      - image_path : string representing the path of the image object.
      - description : string represneting the image description.
    - test(ipadrress,port,username,password)
      - ip address : string that represents the ipaddress of the interop server. ex: "10.10.130.2"
      - port number : string that represents the port number used to connect to the interop server. ex: "8000"
      - user name : string that represents the user name used to connect to the interop server. ex: "testuser"
      - password : string that represents the password used to connect to the interop server. ex: "testpass"


### Licensing :-
BSD 3-Clause License
Copyright (c) 2021, RobEn
All rights reserved. 
