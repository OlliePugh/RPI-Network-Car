import socket
from packets import *
from threading import Thread
import inputs
import time


LOCAL_HOST = ("127.0.0.1", 51697)
BUFFER_SIZE = 1024


class NetworkManager:

    rtt_freq = 2  # how many seconds between rtt tests
    # if the rtt delay in seconds is greater than the rtt_freq the calculated rtt will be incorrect

    rtt_timeout = 10  # how many seconds before giving up waiting for an rtt response

    def __init__(self, controller):
        self.controller = controller

        self.reaction_dictionary = {
            RTTPacket: self.rtt_packet_response,
            HeartbeatPacket: self.heartbeat_packet_response}  # a dictionary that stores the function that handles the packet
        self.car_address = None  # the address of the car is currently unknown

        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_DGRAM)  # declare the socket as a UDP internet connection socket

        self.socket.bind(LOCAL_HOST)

        self.last_rtt_time = 0  # set the last rtt send time as 0 so a call should be sent very quickly
        self.awaiting_rtt = False

        Thread(target=self.scheduled_packet_send_loop, daemon=True).start()
        Thread(target=self.incoming_packet_handler, daemon=True).start()  # assign thread to listen to incoming traffic

    def incoming_packet_handler(self):
        while True:
            print("listening")
            try:
                data, address = self.socket.recvfrom(1024)  # 1024 bytes buffer size

                packet_contents = pickle.loads(data)
                if packet_contents[0] not in packet_dict.keys():
                    print("Packet unknown ID received. Packet ID = ", str(packet_contents[0]))
                    continue  # go back to the start of the loop

                packet = packet_dict[packet_contents[0]](packet_contents)  # create the packet from the packet ID

                if packet.__class__ not in self.reaction_dictionary.keys():
                    print("Packet of unknown type received. Type =  " + packet.__class__.__name__)
                    continue

                self.reaction_dictionary[packet.__class__](packet, address)  # call the function that corresponds to the packet
            except ConnectionResetError:
                self.car_address = None

    def scheduled_packet_send_loop(self):  # handles gathering control information and transmitting to the car
        while True:
            if self.car_address is not None:
                if (time.time() - self.last_rtt_time > self.rtt_freq and not self.awaiting_rtt) or (time.time() - self.last_rtt_time > 10):  # if it has been 2 seconds since last rtt packet send one or if it has been 10 seconds since the last packet was sent
                    self.send_rtt_packet()
                self.send_controller_packet()
                time.sleep(0.032)  # send 30 control packets a second

    def rtt_packet_response(self, rtt_packet, addr):
        self.awaiting_rtt = False
        print(round((time.time() - self.last_rtt_time) * 1000), "ms")

    def heartbeat_packet_response(self, heartbeat_packet, addr):
        print("heartbeat received")
        self.car_address = addr

    def send_rtt_packet(self):  # send an RTT packet back to the server
        # This approach still isnt great as there is a chance that the packet may be lost
        self.last_rtt_time = time.time()
        self.awaiting_rtt = True
        if self.car_address is not None:
            self.socket.sendto(bytes(RTTPacket.construct()), self.car_address)  # this function is used for testing a connection
        else:
            print("CANT SEND PACKET NOT CONNECTED TO CAR")

    def send_controller_packet(self):
        packet = ControlsPacket.construct(self.controller.turning_angle, self.controller.throttle, self.controller.brake)
        if self.car_address is not None:
            self.socket.sendto(bytes(packet), self.car_address)
        else:
            print("CANT SEND PACKET NOT CONNECTED TO CAR")


class Controller:
    def __init__(self):
        self.network_controller = NetworkManager(self)

        self.controls = {"throttle": None,
                         "brake": None,
                         "turning": None}
        self.throttle = 0
        self.brake = 0
        self.turning_angle = 0

        Thread(target=self.update_inputs, daemon=True).start()  # create a thread to keep the inputs

    def update_inputs(self):
        while True:
            inputs.event_pump()  # get the most recent event cycle
            if self.controls["throttle"] is not None:  # if the control is set
                self.throttle = self.controls["throttle"].get_input()  # assign the value to the attribute
            else:
                self.throttle = 0  # if the control is not set just set the value to 0

            if self.controls["brake"] is not None:
                self.brake = self.controls["brake"].get_input()
            else:
                self.brake = 0

            if self.controls["turning"] is not None:
                self.turning_angle = self.controls["turning"].get_input()
            else:
                self.turning_angle = 0

            time.sleep(0.032)  # update 30 times a second
