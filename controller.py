import socket
from packets import *
from threading import Thread
import inputs
import time


LOCAL_HOST = ("127.0.0.1", 51697)
BUFFER_SIZE = 1024


class NetworkManager:
    def __init__(self, controller):
        self.controller = controller

        self.reaction_dictionary = {
            ExamplePacket: self.example_packet_response}  # a dictionary that stores the function that handles the packet
        self.car_address = None  # the address of the car is currently unknown

        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_DGRAM)  # declare the socket as a UDP internet connection socket

        self.socket.bind(LOCAL_HOST)

        Thread(target=self.controls_packet_send_loop, daemon=True).start()
        Thread(target=self.incoming_packet_handler, daemon=True).start()  # assign thread to listen to incoming traffic

    def incoming_packet_handler(self):
        while True:
            print("listening")
            data, address = self.socket.recvfrom(1024)  # 1024 bytes buffer size

            self.car_address = address  # store the cars address

            packet_contents = pickle.loads(data)
            if packet_contents[0] not in packet_dict:
                print("Packet unknown ID received. Packet ID = ", str(packet_contents[0]))
                continue  # go back to the start of the loop

            packet = packet_dict[packet_contents[0]](packet_contents)  # create the packet from the packet ID

            if packet.__class__ not in self.reaction_dictionary:
                print("Packet of unknown type received. Type =  " + packet.__class__.__name__)
                continue

            self.reaction_dictionary[packet.__class__](packet)  # call the function that corresponds to the packet

    def controls_packet_send_loop(self):  # handles gathering control information and transmitting to the car
        while True:
            if self.car_address is not None:
                self.send_controller_packet()

    def example_packet_response(self, example_packet):
        print(example_packet.data[1])

    def send_controller_packet(self):
        packet = ControlsPacket.construct(100, 90, 90)
        self.socket.sendto(bytes(packet), self.car_address)


class Controller:
    def __init__(self):
        self.network_controller = NetworkManager(self)

        self.controls = {"throttle": None,
                         "brake": None,
                         "turning": None}
        self.throttle = 0
        self.brake = 0
        self.turning_angle = 0

        Thread(target=self.update_inputs, daemon=True).start() # create a thread to keep the inputs

    def update_inputs(self):  # https://stackoverflow.com/questions/47855725/pygame-how-can-i-allow-my-users-to-change-their-input-keys-custom-keybinding
        while True:  # USE THE ABOVE TO CREATE CUSTOM CONTROLS
            inputs.event_pump()
            if None not in self.controls.values():  # if all controls are set
                self.throttle = self.controls["throttle"]  # GET THE VALUE FROM THE PYGAME INPUT
                self.brake = self.controls["brake"]  # GET THE VALUE FROM THE PYGAME INPUT
                self.turning_angle = self.controls["turning"]  # GET THE VALUE FROM THE PYGAME INPUT
            time.sleep(0.016)  # update 60 times a second
