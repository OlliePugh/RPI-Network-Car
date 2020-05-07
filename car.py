import socket
from threading import Thread
from packets import *
import traceback

CONTROLLER_ADDRESS = ("127.0.0.1", 51697)
BUFFER_SIZE = 1024


class Car:

    def __init__(self):

        self.reaction_dictionary = {
            RTTPacket: self.rtt_packet_response,
            ControlsPacket: self.control_packet_response}  # a dictionary that stores the function that handles the packet

        self.connected = False

        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_DGRAM)  # declare the socket as a UDP internet connection socket

        self.socket.connect(CONTROLLER_ADDRESS)  # connect to the car

        Thread(target=self.incoming_packet_handler, daemon=True).start()  # assign thread to listen to incoming traffic
        Thread(target=self.scheduled_packet_send_loop, daemon=True).start()

    def incoming_packet_handler(self):
        while True:
            try:
                data, address = self.socket.recvfrom(1024)  # 1024 bytes buffer size
                packet_contents = pickle.loads(data)
                if packet_contents[0] not in packet_dict:  # check that the packet id is in the list of packets with known ID's
                    print("Packet unknown ID received. Packet ID = ", str(packet_contents[0]))
                    continue  # go back to the start of the loop

                packet = packet_dict[packet_contents[0]](packet_contents)  # create the packet from the packet ID

                if packet.__class__ not in self.reaction_dictionary:
                    print("Packet of unknown type received. Type =  " + packet.__class__.__name__)
                    continue
                self.reaction_dictionary[packet.__class__](packet)  # call the function that corresponds to the packet
            except ConnectionResetError:
                print("Can't reach server")

    def scheduled_packet_send_loop(self):  # handles gathering control information and transmitting to the car
        while True:
            self.send_heartbeat_packet()
            time.sleep(3)  # send 30 control packets a second

    def send_rtt_packet(self):  # send an RTT packet back to the server
        self.socket.sendto(bytes(RTTPacket.construct()), CONTROLLER_ADDRESS)  # this function is used for testing a connection

    def send_heartbeat_packet(self):
        self.socket.sendto(bytes(HeartbeatPacket.construct()), CONTROLLER_ADDRESS)

    def rtt_packet_response(self, rtt_packet):  # if an rtt packet is received just send it straight back
        self.send_rtt_packet()

    def control_packet_response(self, control_packet):
        print(control_packet.throttle, control_packet.brake, control_packet.turning_angle)


def main():
    try:
        car = Car()
        car.send_rtt_packet()
        while True:
            pass
    except Exception:
        print("EXCEPTION OCCURED")
        car.socket.close()
        track = traceback.format_exc()
        print(track)


if __name__ == "__main__":
    main()
