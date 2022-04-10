# AUVSI-SUAS-Communication-system

data transmission system that handles the transmission of the data between the UAV and ground station in many different aspects including :
- Encrypting the data before transmission
- Authentication between the different system components.
- establishing a secure transmission channel for ensuring data delivery in a reliable and secure manner.
- Maintaining this secure channel and handling connection failures and data corruption. 
- providing a shield between the image recognition system, control system host environment and the external network.
- verifying data integrity and checking it for manipulation or corruption.
- Load balancing between different system components and reducing network traffic. 

<p align="center">
<img  src='system diagram.png'></img>
</p>

## System components:-
    1 - UAV software.
    2 - Proxy server.
    3 - communications API.


### UAV software:-
    This component consists of 2 components
    - Frame capturing and forwarding software.
    - mav proxy

#### Frame capturing and forwarding software
    The software responsible for :
    - capturing camera frames.
    - geo tagging these frames.
    - encrypting the data
    - sending the data to the proxy server

#### mavproxy
    A tool used to forward MAVLink messages to the proxy server.

### proxy server:-
    This component is responsible for receiving data from UAV software, decrypting it and forwarding MAVLink messages to interop server and also storing the frames info inside it's buffer for the image recognition system to receive it on demand.

### communications API:-
    An python API for different systems to communicate with each other through the proxy server.
