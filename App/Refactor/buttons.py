from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from config import login, userRole, scheduledReloads
from api import getEnabledEvents
from utilities import hashData


#this class is used to make the buttons that are used to choose a patient/resident
class PatientButton(Button):
    def __init__ (self, graph_id: int, text: str):
        Button.__init__(self)
        self.graph_id = graph_id
        self.text = text
        self.bind(on_press=self.choosePatient)

    def choosePatient(self, instance):
        return self.graph_id