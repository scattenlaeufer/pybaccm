#!/usr/bin/env python3

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.storage.jsonstore import JsonStore
from kivy.properties import DictProperty, BooleanProperty
import random


class StartGrid(GridLayout):

    army_list = DictProperty()

    def __init__(self, **kwargs):
        super(StartGrid, self).__init__(**kwargs)

        self.army_list_data = JsonStore("army_list.json", indent=4, sort_keys=True)
        try:
            self.army_list["lists"] = self.army_list_data["lists"]
            self.army_list["session_data"] = self.army_list_data["session_data"]
        except KeyError:
            self.army_list["lists"] = {
                "default": {
                    "hq": {"major": None, "captain": None, "infantry": None},
                    "platoons": [],
                    "blubb": 0,
                }
            }
            self.army_list["session_data"] = {"current_list": "default"}
            print("created empty army list")

        self.ids["label_number"].text = str(
            self.army_list["lists"][self.army_list["session_data"]["current_list"]][
                "blubb"
            ]
        )

    def set_random_number(self, instnace):
        a = random.randint(0, 10)
        list_dict = self.army_list["lists"]
        list_dict[self.army_list["session_data"]["current_list"]]["blubb"] = a
        self.army_list["lists"] = list_dict
        self.ids["label_number"].text = str(
            self.army_list["lists"][self.army_list["session_data"]["current_list"]][
                "blubb"
            ]
        )

    def on_army_list(self, instance, army_list):
        self.army_list_data["lists"] = army_list["lists"]
        try:
            self.army_list_data["session_data"] = army_list["session_data"]
        except KeyError:
            pass
        print("saved army list")

    def select_army_list(self, instance):
        ArmySelectPopup(self.army_list).open()


class ArmySelectPopup(Popup):
    def __init__(self, army_list, **kwargs):
        super(ArmySelectPopup, self).__init__(**kwargs)
        self.army_list = army_list
        self.army_listing = ArmyListing(self.army_list)
        self.ids['army_listing_container'].add_widget(self.army_listing)

    def create_new_army_list(self, instance):
        popup = NewArmyListPopup(self.army_list)
        popup.bind(on_dismiss=self.add_new_army_list)
        popup.open()

    def add_new_army_list(self, instance):
        if instance.ids["textinput_name"].text:
            self.ids["label_army_list"].text = instance.ids["textinput_name"].text
            self.army_list["session_data"]["current_list"] = instance.ids[
                "textinput_name"
            ].text


class NewArmyListPopup(Popup):

    army_list_name = None

    def __init__(self, army_list, **kwargs):
        super(NewArmyListPopup, self).__init__(**kwargs)
        self.army_list = army_list

    def cancel(self):
        self.dismiss()

    def ok(self):
        if self.ids["textinput_name"].text == "":
            self.name = None
        else:
            self.name = self.ids["textinput_name"].text
            lists_dict = self.army_list["lists"]
            lists_dict[self.name] = {"blubb": 0}
            self.army_list["lists"] = lists_dict
        self.dismiss()


class SelectableLabel(RecycleDataViewBehavior, Label):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        """ Catch and handle the view changes """
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        """ Add selection on touch down """
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """ Respond to the selection of items in the view. """
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))


class SelectableRecycleBoxLayout(
    FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout
):
    pass


class ArmyListing(RecycleView):
    def __init__(self, army_list, **kwargs):
        super(ArmyListing, self).__init__(**kwargs)
        self.data = [{'text': l} for l in army_list['lists'].keys()]


class CompanyCommanderApp(App):
    def build(self):
        return StartGrid()


if __name__ == "__main__":
    CompanyCommanderApp().run()
