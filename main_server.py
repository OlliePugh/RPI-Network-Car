from tkinter import *
from controller import Controller
import inputs
from threading import Thread, Event
import threading


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
        new_input = None
        while new_input is None and not self.thread_stop_event.wait(0.1):  # check for 0.1 seconds if thread stop event has occured
            new_input = inputs.get_new_button_press()
            self.new_control = new_input
            self.new_control_label["text"] = str(self.new_control)
        print("ENDING THREAD")
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
        self.thread_stop_event = Event()

        row_num = 1

        self.control_dict = {}  # dictionary which will contain dictionaries

        for control_name, control in self.controller.controls.items():
            self.control_dict[control_name] = {}

            self.control_dict[control_name]["name_label"] = Label(self, text=control_name.title())
            self.control_dict[control_name]["name_label"].grid(row=row_num, column=0)

            self.control_dict[control_name]["curr_control_label"] = Label(self, text=str(control))
            self.control_dict[control_name]["curr_control_label"].grid(row=row_num, column=1)

            self.control_dict[control_name]["control_value"] = Label(self, text=str(0.00))
            self.control_dict[control_name]["control_value"].grid(row=row_num, column=2)

            self.control_dict[control_name]["change_button"] = Button(self, text="Change", command=lambda control_name=control_name: ControlChangeGUI(self.controller, control_name, self))
            self.control_dict[control_name]["change_button"].grid(row=row_num, column=3)

            row_num += 1

        self.thread = Thread(target=self.update_live_values, daemon=True).start()  # this needs to be properly killed
        self.mainloop()

    def update_control_name(self, control_name):
        self.control_dict[control_name]["curr_control_label"]["text"] = str(self.controller.controls[control_name])

    def update_live_values(self):
        while not self.thread_stop_event.wait(0.05):
            inputs.joystick_pump()
            for control_name, objects in self.control_dict.items():
                copy_objects = objects
                if self.controller.controls[control_name] is None:
                    copy_objects["control_value"]["text"] = "0.00"
                else:
                    copy_objects["control_value"]["text"] = "{:.2f}".format(self.controller.controls[control_name].get_raw_input())
        return

    def close(self):
        self.thread_stop_event.set()
        self.destroy()

def print_threads():
    while True:
        print(threading.active_count())

def main():
    controller = Controller()
    #Thread(target=print_threads, daemon=True).start()
    gui = MainGui(controller)


if __name__ == "__main__":
    main()
