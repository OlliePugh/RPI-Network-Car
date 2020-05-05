from tkinter import *
from controller import Controller
import inputs
from threading import Thread


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
        self.controller = controller
        self.target_input = target_input
        self.old_control = controller.controls[target_input]
        self.new_control = None
        self.settings_gui = settings_gui

        instructions_label = Label(self, text="Please press/move the input").pack()
        self.new_control_label = Label(self, text="Not Set")
        self.new_control_label.pack()
        cancel_button = Button(self, text="Cancel", command=self.cancel).pack()
        ok_button = Button(self, text="Done", command=self.done).pack()

        Thread(target=self.get_new_control, daemon=True).start()  # this needs to be properly killed

        self.mainloop()

    def get_new_control(self):  # need to cancel this thread if the user presses cancel
        self.new_control = inputs.get_new_button_press()
        self.new_control_label["text"] = str(self.new_control)

    def cancel(self):
        self.controller.controls[self.target_input] = self.old_control
        self.destroy()

    def done(self):
        self.controller.controls[self.target_input] = self.new_control
        self.destroy()
        self.settings_gui.update_control_name(self.target_input)



class SettingsGUI(Toplevel):
    def __init__(self, controller):
        super(SettingsGUI, self).__init__()
        self.grab_set()  # make this the only intractable window
        self.title("Settings")
        self.controller = controller

        row_num = 1

        self.control_dict = {}  # dictionary which will contain dictionaries

        for control_name, control in self.controller.controls.items():
            self.control_dict[control_name] = {}
            self.control_dict[control_name]["name_label"] = Label(self, text=control_name.title())
            self.control_dict[control_name]["name_label"].grid(row=row_num, column=0)

            self.control_dict[control_name]["curr_control_label"] = Label(self, text=str(control))
            self.control_dict[control_name]["curr_control_label"].grid(row=row_num, column=1)

            self.control_dict[control_name]["change_button"] = Button(self, text="Change", command=lambda control_name=control_name: ControlChangeGUI(self.controller, control_name, self))
            self.control_dict[control_name]["change_button"].grid(row=row_num, column=2)

            row_num += 1
        self.mainloop()

    def update_control_name(self, control_name):
        self.control_dict[control_name]["curr_control_label"]["text"] = str(self.controller.controls[control_name])


def main():
    controller = Controller()

    gui = MainGui(controller)


if __name__ == "__main__":
    main()
