from abc import ABC, abstractmethod
import pickle


class Packet(ABC, object):  # abstract class

    def __init__(self, packet_contents=[]):
        self.data = packet_contents  # convert data to bytes

    def __bytes__(self):  # when a cast to bytes is performed this function will be performed on the class
        return pickle.dumps(self.data)  # use pickle data conversion to handle the byte stream

    @staticmethod
    @abstractmethod
    def construct():  # forces an interface approach for a construct method
        pass


class ExamplePacket(Packet):  # packet which contains the controls from the controller
    id = 0

    def __init__(self, packet_contents):
        super(ExamplePacket, self).__init__(packet_contents)

    @staticmethod
    def construct():  # used to create a packet to send
        return ExamplePacket([ExamplePacket.id, "This is an example Packet with some text inside"])


class ControlsPacket(Packet):  # packet which contains the controls from the controller
    id = 1

    def __init__(self, packet_contents):
        super(ControlsPacket, self).__init__(packet_contents)
        self.wheel_angle = packet_contents[1]
        self.throttle = packet_contents[2]
        self.brake = packet_contents[3]


    @staticmethod
    def construct(wheel_angle, throttle, brake):  # used to create a packet to send
        return ControlsPacket([ControlsPacket.id, wheel_angle, throttle, brake])


packet_dict = {ExamplePacket.id: ExamplePacket,
               ControlsPacket.id: ControlsPacket}


if __name__ == "__main__":
    print("Packets script ran as main")
