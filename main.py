#!/usr/bin/env python3

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.storage.jsonstore import JsonStore
from kivy.properties import DictProperty, StringProperty
import random


class StartGrid(GridLayout):

    army_list = DictProperty()
    army_list_name = StringProperty("default")

    def __init__(self, **kwargs):
        super(StartGrid, self).__init__(**kwargs)

        self.army_list_data = JsonStore("army_list.json", indent=4, sort_keys=True)
        try:
            self.army_list = self.army_list_data[self.army_list_name]
        except KeyError:
            self.army_list_data[self.army_list_name] = self.army_list
            self.army_list = {
                "hq": {"major": None, "captain": None, "infantry": None},
                "platoons": [],
                "blubb": 0,
            }
            print("created empty army list")

        print(self.army_list)

        self.ids['label_number'].text=str(self.army_list["blubb"])

    def set_random_number(self, instnace):
        a = random.randint(0, 10)
        self.army_list["blubb"] = a
        self.ids['label_number'].text=str(self.army_list["blubb"])

    def on_army_list(self, instance, army_list):
        self.army_list_data[self.army_list_name] = army_list

    def select_army_list(self, instance):
        ArmySelectPopup().open()


class ArmySelectPopup(Popup):

    def __init__(self, **kwargs):
        super(ArmySelectPopup, self).__init__(**kwargs)


class CompanyCommanderApp(App):
    def build(self):
        return StartGrid()


if __name__ == "__main__":
    CompanyCommanderApp().run()
