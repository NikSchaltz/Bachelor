from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
import requests

#this class is used to make the buttons that are used to choose a patient/resident
class PatientButton(Button):
    def __init__ (self, graph_id: int, text: str):
        Button.__init__(self)
        self.graph_id = graph_id
        self.text = text
        self.bind(on_press=self.choosePatient)

    def choosePatient(self, instance):
        return self.graph_id
    
class SimulationButton(Button):
    def __init__(self, event_id: int,
                graph_id: str,
                simulation_id: str,
                username: str,
                password: str,
                text: str):
        Button.__init__(self)
        self.event_id = event_id
        self.text = text
        self.graph_id = graph_id
        self.simulation_id = simulation_id
        self.username = username
        self.password = password
        self.manipulate_box_layout: BoxLayout = BoxLayout()
        self.bind(on_press=self.execute_event)

    #When the button is pressed, it will execute the event, which means accessing the api to execute the event
    def execute_event(self, instance):
        url = (f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims/{self.simulation_id}/events/{self.event_id}")
        auth=(self.username, self.password)
        req = requests.Session()
        req.auth = auth
        req.post(url)

        #Creates the new buttons for the tasks that are able to be done in the task list at this moment
        from main import createButtonsOfEnabledEvents
        createButtonsOfEnabledEvents(self.graph_id, self.simulation_id, auth, self.manipulate_box_layout)