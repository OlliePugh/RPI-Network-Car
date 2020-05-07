from abc import ABC, abstractmethod
import pickle
import time


class Packet(ABC, object):  # abstract class

    def __init__(self, packet_contents=[]):
        self.data = packet_contents  # convert data to bytes

    def __bytes__(self):  # when a cast to bytes is performed this function will be performed on the class
        return pickle.dumps(self.data)  # use pickle data conversion to handle the byte stream

    @staticmethod
    @abstractmethod
    def construct():  # forces an interface approach for a construct method
        pass


class RTTPacket(Packet):  # packet which contains the controls from the controller
    id = 0

    def __init__(self, packet_contents):
        super(RTTPacket, self).__init__(packet_contents)
        self.send_time = packet_contents[1]

    @staticmethod
    def construct():  # used to create a packet to send
        return RTTPacket([RTTPacket.id, time.time()])  # send a packet with with the unix timestamp of packet creation


class HeartbeatPacket(Packet):
    id = 1

    def __init__(self, packet_contents):
        super(HeartbeatPacket, self).__init__(packet_contents)

    @staticmethod
    def construct():  # used to create a packet to send
        return HeartbeatPacket([HeartbeatPacket.id])


class ControlsPacket(Packet):  # packet which contains the controls from the controller
    id = 2

    def __init__(self, packet_contents):
        super(ControlsPacket, self).__init__(packet_contents)
        self.turning_angle = packet_contents[1]
        self.throttle = packet_contents[2]
        self.brake = packet_contents[3]

    @staticmethod
    def construct(wheel_angle, throttle, brake):  # used to create a packet to send
        return ControlsPacket([ControlsPacket.id, round(wheel_angle*100), round(throttle*100), round(brake*100)])


packet_dict = {RTTPacket.id: RTTPacket,
                   HeartbeatPacket.id: HeartbeatPacket,
               ControlsPacket.id: ControlsPacket}


if __name__ == "__main__":
    print("Packets script ran as main")
