import socket
from packets import *
import pyautogui
from threading import Thread
import traceback

LOCAL_HOST = ("127.0.0.1", 51697)
BUFFER_SIZE = 1024


class Controller:
    def __init__(self):

        self.reaction_dictionary = {
            ExamplePacket: self.example_packet_response}  # a dictionary that stores the function that handles the packet
        self.car_address = None  # the address of the car is currently unknown

        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_DGRAM)  # declare the socket as a UDP internet connection socket

        self.socket.bind(LOCAL_HOST)

        Thread(target=self.incoming_packet_handler, daemon=True).start()  # assign thread to listen to incoming traffic

    def incoming_packet_handler(self):
        while True:
            print("listening")
            data, address = self.socket.recvfrom(1024)  # 1024 bytes buffer size

            self.car_address = address  # store the cars address

            packet_contents = pickle.loads(data)
            packet = packet_dict[packet_contents[0]](packet_contents)  # create the packet from the packet ID
            self.reaction_dictionary[packet.__class__](packet)  # call the function that corresponds to the packet

    def example_packet_response(self, example_packet):
        print(example_packet.data[1])

    def send_controller_packet(self):
        packet = ControlsPacket.construct(100, 90, 90)
        self.socket.sendto(bytes(packet), self.car_address)


def main():
    try:
        controller = Controller()
        while True:
            if controller.car_address is not None:
                controller.send_controller_packet()
    except Exception:  # just to ensure that the socket is closed if something goes wrong
        print("EXCEPTION OCCURED")
        controller.socket.close()
        track = traceback.format_exc()
        print(track)


if __name__ == "__main__":
    main()
