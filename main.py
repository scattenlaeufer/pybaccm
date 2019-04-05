#!/usr/bin/env python3

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
import random


class StartGrid(GridLayout):

    def __init__(self, **kwargs):
        super(StartGrid, self).__init__(**kwargs)
        self.cols = 2
        self.button = Button(text='press')
        self.add_widget(self.button)
        self.label = Label(text='0')
        self.add_widget(self.label)
        self.button.bind(on_press=self.set_random_number)

    def set_random_number(self, instnace):
        self.label.text = str(random.randint(0,10))


class CompanyCommanderApp(App):

    def build(self):
        return StartGrid()


if __name__ == '__main__':
    CompanyCommanderApp().run()
