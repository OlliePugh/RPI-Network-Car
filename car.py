import socket
from threading import Thread
from packets import *
import traceback

CONTROLLER_ADDRESS = ("127.0.0.1", 51697)
BUFFER_SIZE = 1024


class Car:

    def __init__(self):

        self.reaction_dictionary = {
            ExamplePacket: self.example_packet_response,
            ControlsPacket: self.control_packet_response}  # a dictionary that stores the function that handles the packet

        self.connected = False

        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_DGRAM)  # declare the socket as a UDP internet connection socket

        self.socket.connect(CONTROLLER_ADDRESS)

        Thread(target=self.incoming_packet_handler, daemon=True).start()  # assign thread to listen to incoming traffic

    def incoming_packet_handler(self):
        while True:
            print("listening")
            data, address = self.socket.recvfrom(1024)  # 1024 bytes buffer size

            packet_contents = pickle.loads(data)
            print(packet_contents)
            packet = packet_dict[packet_contents[0]](packet_contents)  # create the packet from the packet ID
            self.reaction_dictionary[packet.__class__](packet)  # call the function that corresponds to the packet

    def send_example_packet(self):
        print("Sending Example Packet")
        self.socket.sendto(bytes(ExamplePacket.construct()), CONTROLLER_ADDRESS)  # this function is used for testing a connection

    def example_packet_response(self, example_packet):
        print(example_packet.data[1])

    def control_packet_response(self, control_packet):
        pass


def main():
    try:
        car = Car()
        car.send_example_packet()
        while True:
            pass
    except Exception:
        print("EXCEPTION OCCURED")
        car.socket.close()
        track = traceback.format_exc()
        print(track)


if __name__ == "__main__":
    main()
