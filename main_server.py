from tkinter import *
from controller import Controller
import inputs
from threading import Thread, Event
import threading
import time


class MainGui(Tk):
    def __init__(self, controller):
        super(MainGui, self).__init__()
        self.title("RPI Network Car Controller")
        self.controller = controller

        button = Button(self, text="Open Settings", command=lambda: SettingsGUI(self.controller)).pack()

        self.mainloop()


class ControlChangeGUI(Toplevel):
    def __init__(self, controller, target_input, settings_gui):
        super(ControlChangeGUI, self).__init__()
        self.grab_set()  # make this the only intractable window
        self.title("Settings")
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.controller = controller
        self.target_input = target_input
        self.old_control = controller.controls[target_input]
        self.new_control = None
        self.settings_gui = settings_gui

        self.thread_stop_event = Event()

        instructions_label = Label(self, text="Please press/move the input").pack()
        self.new_control_label = Label(self, text="Not Set")
        self.new_control_label.pack()
        cancel_button = Button(self, text="Cancel", command=self.cancel).pack()
        ok_button = Button(self, text="Done", command=self.done).pack()

        self.thread = Thread(target=self.get_new_control, daemon=True)  # this needs to be properly killed
        self.thread.start()

        self.mainloop()

    def get_new_control(self):  # need to cancel this thread if the user presses cancel
        while not self.thread_stop_event.wait(0.1):  # check for 0.1 seconds if thread stop event has occured
            new_input = inputs.get_new_button_press()
            if new_input is not None:
                self.new_control = new_input
                self.new_control_label["text"] = str(self.new_control)
        return

    def cancel(self):
        self.controller.controls[self.target_input] = self.old_control
        self.thread_stop_event.set()
        self.destroy()

    def done(self):
        self.controller.controls[self.target_input] = self.new_control
        self.thread_stop_event.set()
        self.settings_gui.update_control_name(self.target_input)
        self.destroy()


class SettingsGUI(Toplevel):
    def __init__(self, controller):
        super(SettingsGUI, self).__init__()
        self.grab_set()  # make this the only intractable window
        self.title("Settings")
        self.controller = controller

        self.protocol("WM_DELETE_WINDOW", self.close)

        row_num = 1

        self.control_dict = {}  # dictionary which will contain dictionaries

        for control_name, control in self.controller.controls.items():
            self.control_dict[control_name] = {}

            Label(self, text=control_name.title()).grid(row=row_num, column=0)

            self.control_dict[control_name]["curr_control_label"] = Label(self, text=str(control))
            self.control_dict[control_name]["curr_control_label"].grid(row=row_num, column=1)

            self.control_dict[control_name]["control_value"] = StringVar(self, value="0.00")

            Label(self, textvariable=self.control_dict[control_name]["control_value"]).grid(row=row_num, column=2)
            Button(self, text="Reset", command=lambda control_name=control_name: self.reset_control(control_name)).grid(row=row_num, column=3)

            Button(self, text="Change", command=lambda control_name=control_name: ControlChangeGUI(self.controller, control_name, self)).grid(row=row_num, column=4)

            self.control_dict[control_name]["deadzone_value"] = DoubleVar(0.00)

            if control is not None:
                self.control_dict[control_name]["deadzone_value"].set(float(control.deadzone))
                print(control.deadzone)

            self.control_dict[control_name]["deadzone_scale"] = Scale(self, from_=0, to=1, digits=3, resolution=0.01, variable=self.control_dict[control_name]["deadzone_value"], label="Deadzone", orient=HORIZONTAL)
            self.control_dict[control_name]["deadzone_scale"].grid(row=row_num, column=5)

            row_num += 1

        self.update_live_values()

        self.mainloop()

    def update_control_name(self, control_name):
        self.control_dict[control_name]["curr_control_label"]["text"] = str(self.controller.controls[control_name])

    def update_live_values(self):  # this will update the live values and update the deadzone values in the controller
        for control_name, objects in self.control_dict.items():
            if self.controller.controls[control_name] is not None:
                objects["control_value"].set("{:.2f}".format(self.controller.controls[control_name].get_raw_input()))
                self.controller.controls[control_name].deadzone = objects["deadzone_value"].get()
                self.control_dict[control_name]["deadzone_scale"].config(state="active")
            else:
                objects["control_value"].set("0.00")
                self.control_dict[control_name]["deadzone_value"].set(0.00)
                self.control_dict[control_name]["deadzone_scale"].config(state="disable")
        self.after(100, self.update_live_values)

    def reset_control(self, control_name):
        self.controller.controls[control_name] = None
        self.update_control_name(control_name)

    def close(self):
        self.destroy()


def print_threads():
    while True:
        print(threading.active_count())

def main():
    controller = Controller()
    gui = MainGui(controller)


if __name__ == "__main__":
    main()
