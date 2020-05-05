import pygame
from abc import ABC, abstractmethod


class Input(ABC):
    def __init__(self):
        self.value = 0

    @abstractmethod
    def get_raw_input(self):
        pass


class KeyInput(Input):
    def __init__(self, key):
        super(KeyInput, self).__init__()
        self.key = key

    def get_raw_input(self):
        return pygame.key.get_pressed()[self.key]


class ButtonInput(Input):  # MAKE SURE pygame.event.pump() IS RAN BEFORE GETTING INPUTS
    def __init__(self, joystick_num, button_num):
        super(ButtonInput, self).__init__()
        self.joystick = pygame.joystick.Joystick(joystick_num)
        self.button_num = button_num

    def get_raw_input(self):
        return self.joystick.get_button(self.button_num)


class AxisInput(Input):
    def __init__(self, joystick_num, axis_num):
        super(AxisInput, self).__init__()
        self.joystick = pygame.joystick.Joystick(joystick_num)
        self.axis_num = axis_num

    def get_raw_input(self):
        return self.joystick.get_axis(self.axis_num)

    def get_normalised_input(self):  # assuming max is 1 and min is -1
        min_val = -1
        max_val = 1
        return (self.get_raw_input()-min_val)/(max_val-min_val)

    def __str__(self):
        return self.joystick.get_name() + " input number: " + str(self.axis_num)


def load_joysticks():
    for i in range(pygame.joystick.get_count()):
        pygame.joystick.Joystick(i).init()
        print(i)


def get_new_button_press():  # only support axis at the minute
    axis = None
    while axis is None:
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION and abs(event.value) > 0.3:
                return AxisInput(event.joy, event.axis)  # return the new axis


pygame.init() # start the pygame system
load_joysticks()

if __name__ == "__main__":

    example_axis = get_new_button_press()

    while True:
        print(example_axis.get_normalised_input())
        pygame.event.pump()
