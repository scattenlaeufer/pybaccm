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
import os


nationalities = [
    "Britain",
    "France",
    "Germany",
    "Italy",
    "Japan",
    "Soviet Union",
    "United States",
]


class StartGrid(GridLayout):

    army_list = DictProperty()

    def __init__(self, **kwargs):
        super(StartGrid, self).__init__(**kwargs)

        self.army_list_data = JsonStore(os.path.join(App.get_running_app().user_data_dir, "army_list.json"), indent=4, sort_keys=True)
        try:
            self.army_list["lists"] = self.army_list_data["lists"]
            self.army_list["session_data"] = self.army_list_data["session_data"]
        except KeyError:
            self.army_list["lists"] = {
                "default": {
                    "hq": {"major": None, "captain": None, "infantry": None},
                    "platoons": [],
                    "nationality": "Britain",
                }
            }
            self.army_list["session_data"] = {"current_list": "default"}

        self.ids["label_current_list"].text = self.army_list["session_data"][
            "current_list"
        ]

    def on_army_list(self, instance, army_list):
        self.army_list_data["lists"] = army_list["lists"]
        try:
            self.army_list_data["session_data"] = army_list["session_data"]
        except KeyError:
            pass

    def select_army_list(self):
        popup = ArmySelectPopup(self.army_list)
        popup.bind(on_dismiss=self.update_current_army_list)
        popup.open()

    def update_current_army_list(self, instance):
        if instance.selected_list and (
            self.army_list_data["session_data"]["current_list"]
            != instance.selected_list
        ):
            self.ids["label_current_list"].text = instance.selected_list
            session_data = self.army_list_data["session_data"]
            session_data["current_list"] = instance.selected_list
            self.army_list_data["session_data"] = session_data

    def delete_army_lists(self):
        popup = ArmyListDeletePopup(self.army_list)
        popup.open()


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
        # TODO: don't add list name to self.army_listing when creation canceled
        if instance.ids["textinput_name"].text:
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
        self.nation_selection = SelectableListing(nationalities)
        self.ids["layout_nation_selection"].add_widget(self.nation_selection)

    def cancel(self):
        self.dismiss()

    def ok(self):
        if self.ids["textinput_name"].text == "":
            self.name = None
        elif self.ids["textinput_name"].text in self.army_list["lists"].keys():
            MessagePopup(
                "List already exist",
                "There already is a army list with the name {}".format(
                    self.ids["textinput_name"].text
                ),
            )
        else:
            nation = self.nation_selection.get_selection()
            if len(nation) == 1:
                self.name = self.ids["textinput_name"].text
                lists_dict = self.army_list["lists"]
                lists_dict[self.name] = {
                    "natitonality": nation[0]["text"],
                    "hq": {"captain": None, "major": None, "infantry": None},
                    "platoons": [],
                }
                self.army_list["lists"] = lists_dict
                self.dismiss()
            else:
                MessagePopup("No nation selected", "Please select a nation.")


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
        return StartGrid()


if __name__ == "__main__":
    CompanyCommanderApp().run()
