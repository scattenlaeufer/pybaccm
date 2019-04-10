#!/usr/bin/env python3

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
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
import os


nations = [
    "Britain",
    "France",
    "Germany",
    "Italy",
    "Japan",
    "Soviet Union",
    "United States",
]

theater_selector_dict = {
    n: ["{} - {}".format(n, i) for i in range(20)] for n in nations
}

default_list_dict = {
    "lists": {
        "default": {
            "hq": {"major": None, "captain": None, "infantry": None},
            "platoons": [],
            "nationality": "Britain",
            "theater_selector": "1944 - Normandy",
        }
    },
    "session_data": {"current_list": "default"},
}


class ManagerLayout(BoxLayout):

    army_list = DictProperty()

    def __init__(self, **kwargs):
        super(ManagerLayout, self).__init__(**kwargs)

        self.army_list_data = JsonStore(
            os.path.join(App.get_running_app().user_data_dir, "army_list.json"),
            indent=4,
            sort_keys=True,
        )
        try:
            self.army_list["lists"] = self.army_list_data["lists"]
            self.army_list["session_data"] = self.army_list_data["session_data"]
        except KeyError:
            self.army_list["lists"] = default_list_dict["lists"]
            self.army_list["session_data"] = default_list_dict["session_data"]

        start_grid = StartGrid(self.army_list)
        self.add_widget(start_grid)

    def on_army_list(self, instance, army_list):
        for key, value in army_list.items():
            self.army_list_data[key] = value

    def switch_to_start(self, instance):
        self.remove_widget(instance)
        start_grid = StartGrid(self.army_list)
        self.add_widget(start_grid)

    def switch_to_game(self, instance):
        self.remove_widget(instance)
        game_grid = GameGrid(self.army_list)
        self.add_widget(game_grid)


class StartGrid(GridLayout):
    def __init__(self, army_list, **kwargs):
        super(StartGrid, self).__init__(**kwargs)

        self.army_list = army_list

        self.ids["label_current_list"].text = self.army_list["session_data"][
            "current_list"
        ]

    def select_army_list(self):
        popup = ArmySelectPopup(self.army_list)
        popup.bind(on_dismiss=self.update_current_army_list)
        popup.open()

    def update_current_army_list(self, instance):
        if instance.selected_list and (
            self.army_list["session_data"]["current_list"] != instance.selected_list
        ):
            self.ids["label_current_list"].text = instance.selected_list
            session_data = self.army_list["session_data"]
            session_data["current_list"] = instance.selected_list
            self.army_list["session_data"] = session_data

    def delete_army_lists(self):
        popup = ArmyListDeletePopup(self.army_list)
        popup.open()

    def start_game(self):
        self.parent.switch_to_game(self)


class GameGrid(GridLayout):
    def __init__(self, army_list, **kwargs):
        super(GameGrid, self).__init__(**kwargs)
        self.army_list = army_list

    def switch(self):
        self.parent.switch_to_start(self)


class ArmySelectPopup(Popup):
    def __init__(self, army_list, **kwargs):
        super(ArmySelectPopup, self).__init__(**kwargs)
        self.army_list = army_list
        self.selected_list = None
        self.army_listing = SelectableListing(self.army_list["lists"].keys())
        self.ids["army_listing_container"].add_widget(self.army_listing)

    def create_new_army_list(self, instance):
        popup = NewArmyListPopup(self.army_list)
        popup.bind(on_dismiss=self.add_new_army_list)
        popup.open()

    def add_new_army_list(self, instance):
        if instance.list_name:
            self.army_listing.add_data_item(instance.ids["textinput_name"].text)

    def ok(self):
        selected = self.army_listing.get_selection()
        if len(selected) == 1:
            self.selected_list = selected[0]["text"]
            self.dismiss()


class NewArmyListPopup(Popup):

    army_list_name = None

    def __init__(self, army_list, **kwargs):
        super(NewArmyListPopup, self).__init__(**kwargs)
        self.army_list = army_list
        self.list_name = None
        self.nation_dropdown = DropDown()
        for nation in theater_selector_dict.keys():
            button = DropDownButton(text=nation)
            button.bind(on_release=lambda btn: self.nation_dropdown.select(btn.text))
            self.nation_dropdown.add_widget(button)
        self.ids["button_nation_selection"].bind(on_release=self.nation_dropdown.open)
        self.nation_dropdown.bind(on_select=self.set_nationality)
        self.theater_dropdown = DropDown()
        self.ids["button_theater_selector"].bind(on_release=self.theater_dropdown.open)
        self.theater_dropdown.bind(on_select=self.set_theater_selector)

    def set_nationality(self, instance, nationality):
        self.theater_dropdown.dismiss()
        if nationality != self.ids["button_nation_selection"].text:
            self.ids["button_nation_selection"].text = nationality
            self.ids["button_theater_selector"].text = "select"
            self.theater_dropdown.clear_widgets()
            for selector in theater_selector_dict[nationality]:
                button = DropDownButton(text=selector)
                button.bind(
                    on_release=lambda btn: self.theater_dropdown.select(btn.text)
                )
                self.theater_dropdown.add_widget(button)

    def set_theater_selector(self, instance, theater_selector):
        self.ids["button_theater_selector"].text = theater_selector

    def cancel(self):
        self.dismiss()

    def ok(self):
        if self.ids["textinput_name"].text == "":
            MessagePopup("List With No Name", "Please give your new list a name")
        elif self.ids["textinput_name"].text in self.army_list["lists"].keys():
            MessagePopup(
                "List already exist",
                "There already is a army list with the name {}".format(
                    self.ids["textinput_name"].text
                ),
            )
        elif self.ids["button_nation_selection"].text == "select":
            MessagePopup("No nation selected", "Please select a nation.")
        elif self.ids["button_theater_selector"].text == "":
            MessagePopup(
                "No theater selector selected", "Please select a theater selector"
            )
        else:
            self.list_name = self.ids["textinput_name"].text
            lists_dict = self.army_list["lists"]
            lists_dict[self.list_name] = default_list_dict["lists"]["default"]
            lists_dict[self.list_name]["nationality"] = self.ids[
                "button_nation_selection"
            ].text
            lists_dict[self.list_name]["theater_selector"] = self.ids[
                "button_theater_selector"
            ].text
            self.army_list["lists"] = lists_dict
            self.dismiss()


class DropDownButton(Button):
    pass


class ArmyListDeletePopup(Popup):
    def __init__(self, army_list, **kwargs):
        super(ArmyListDeletePopup, self).__init__(**kwargs)
        self.army_list = army_list
        self.army_listing = SelectableListing(
            self.army_list["lists"].keys(), multiselect=True
        )
        self.ids["army_listing_container"].add_widget(self.army_listing)

    def delete(self):
        if len(self.army_listing.get_selection()) == 0:
            MessagePopup(
                "No lists selected", "There are no lists seleted to be deleted."
            ).open()
        else:
            confirmation_popup = ConfirmationPopup(
                "Confirm deletion",
                "Do you really want to delete the selected army lists?",
            )
            confirmation_popup.bind(on_dismiss=self.actually_delete)
            confirmation_popup.open()

    def actually_delete(self, instance):
        if instance.confirmation:
            if self.army_list["session_data"]["current_list"] in [
                l["text"] for l in self.army_listing.get_selection()
            ]:
                MessagePopup(
                    "No lists deleted",
                    "Current list was selected to be deleted. No lists deleted.",
                ).open()
            else:
                lists = self.army_list["lists"]
                for l in self.army_listing.get_selection():
                    del lists[l["text"]]
                self.army_list["lists"] = lists
            self.dismiss()


class MessagePopup(Popup):
    def __init__(self, title, message, **kwargs):
        super(MessagePopup, self).__init__(**kwargs)
        self.title = title
        self.ids["label_message"].text = message
        self.open()


class ConfirmationPopup(Popup):
    def __init__(self, title, message, **kwargs):
        super(ConfirmationPopup, self).__init__(**kwargs)
        self.title = title
        self.ids["label_message"].text = message
        self.confirmation = False

    def ok(self):
        self.confirmation = True
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
            rv.data[index]["selected"] = True
        else:
            rv.data[index]["selected"] = False


class SelectableRecycleBoxLayout(
    FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout
):
    pass


class SelectableListing(RecycleView):
    def __init__(self, data, multiselect=False, **kwargs):
        super(SelectableListing, self).__init__(**kwargs)
        self.data = [{"text": l, "selected": False} for l in data]
        self.children[0].multiselect = multiselect
        self.children[0].touch_multiselect = multiselect

    def add_data_item(self, data_item):
        self.data.append({"text": data_item, "selected": False})
        self.data = sorted(self.data, key=lambda k: k["text"])
        self.refresh_from_data()

    def get_selection(self):
        selection = []
        for item in self.data:
            if item["selected"]:
                selection.append(item)
        return selection


class CompanyCommanderApp(App):
    def build(self):
        return ManagerLayout()


if __name__ == "__main__":
    CompanyCommanderApp().run()
