from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
import requests
import xmltodict

import logging
logging.basicConfig(level=logging.DEBUG)

from api import getEnabledEvents, dbQuery
from config import login, userRole, scheduledReloads
from utilities import hashData
from screens import loginScreen, adminScreen, writeNotesScreen, showNotesScreen
from screens import choosePatientScreen
from notes import createNotesFields, showNotesLayout, clearNotesBox, getNotes, addActivityToNotes, uploadNote
from topBar import topBar, hideTopBar, showTopBar
from connect import addUser, loginUser, startSim, getGraphTitle, createInstance, role, terminate, forceTerminateAdmin

def stopReloads():
    global scheduledReloads
    for reload in scheduledReloads:
        Clock.unschedule(reload)
    scheduledReloads = []

def cleanScreen(app):
    stopReloads()
    app.box_lower.clear_widgets()

def createButtonsOfEnabledEvents(
    graph_id: str,
    sim_id: str,
    auth: (str, str),
    button_layout: BoxLayout):

    events_json = getEnabledEvents(graph_id, sim_id, auth)
    # cleanup of previous widgets
    button_layout.clear_widgets()

    global userRole

    events = []
    # distinguish between one and multiple events
    if not isinstance(events_json['events']['event'], list):
        events = [events_json['events']['event']]
    else:
        events = events_json['events']['event']

    for e in events:
        if hashData(e['@roles']) == userRole or e['@roles'] == "":
            if e['@executed'] == 'false':
                s = SimulationButton(
                    #the actual event id
                    e['@id'],
                    graph_id,
                    sim_id,
                    auth[0],
                    auth[1],
                    #the label of the event
                    e['@label']
                )
                s.manipulate_box_layout = button_layout
                if e.get('@pending') == 'true':
                    s.color = get_color_from_hex("#FFFF00")  # Set text color to yellow for pending events
                button_layout.add_widget(s)

    global start_reload_events
    # Schedule the next call to createButtonsOfEnabledEvents after 5 seconds
    start_reload_events = lambda dt: createButtonsOfEnabledEvents(graph_id, sim_id, auth, button_layout)
    Clock.schedule_once(start_reload_events, 5)
    global scheduledReloads
    scheduledReloads.append(start_reload_events)

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
        createButtonsOfEnabledEvents(self.graph_id, self.simulation_id, auth, self.manipulate_box_layout)


class MainApp(App):
    #Creates the base of the app
    def build(self):
        #One outer box layout that contains the top bar and the lower box layout
        box = BoxLayout(orientation='vertical')
        self.box_lower = BoxLayout(orientation='vertical')
        box.add_widget(self.topBar(self))
        self.loginScreen(self)
        box.add_widget(self.box_lower)

        return box
    
    #Creates the topbar and the buttons that are in the topbar
    def topBar(self, instance):
        return topBar(self)
    
    #Designs the login screen and shows it
    def loginScreen(self, instance):
        stopReloads()
        loginScreen(self)

    def cleanScreen(self, instance):
        cleanScreen(self)

    def adminScreen(self, instance):
        cleanScreen(self)
        adminScreen(self)

    def addUser(self, instance, email, role):
        return addUser(self, instance, email, role)

    def loginUser(self, instance):
        loginUser(self)

    #Function to hide the topbar    
    def hideTopBar(self, instance):
        hideTopBar(self)
    
    #Function to show the topbar
    def showTopBar(self, instance):
        showTopBar(self)

    #Function to create and show the events screen
    def eventsScreen(self, instance):
        cleanScreen(self)

        createButtonsOfEnabledEvents(self.graph_id, self.simulation_id, (self.username.text, self.password.text), self.box_lower)

    #Function to show the notes screen
    def showNotesScreen(self, instance):
        cleanScreen(self)
        showNotesScreen(self)

        global start_reload_notes
        # Schedule the next call to createButtonsOfEnabledEvents after 5 seconds
        start_reload_notes = lambda dt: self.showNotesScreen(instance)
        Clock.schedule_once(start_reload_notes, 5)
        global scheduledReloads
        scheduledReloads.append(start_reload_notes)

    #Function to create the notes fields
    def createNotesFields(self, string, button_num):
        return createNotesFields(self, string, button_num)

    #Function to create the layout for the notes
    def showNotesLayout(self, strings):
        return showNotesLayout(self, strings)

    #Function that shows which patients are available to choose from
    def choosePatientScreen(self, instance):
        cleanScreen(self)
        choosePatientScreen(self)

    def getGraphTitle(self, graph_id):
        return getGraphTitle(self, graph_id)


    #Shows the screen where you can write notes
    def writeNotesScreen(self, instance):
        cleanScreen(self)
        writeNotesScreen(self)
    
    #Uploads the notes to the api, by sending a post request
    def uploadNote(self, instance):
        return uploadNote(self)

    #Gets the notes from the api
    def getNotes(self, instance):
        return getNotes(self)

    #Clears the notes box
    def clearNotesBox(self, instance):
        clearNotesBox(self)


    #This function is used to add a dropdown menu to the writeNotesScreen function, so that you can choose which activity you want to write notes for
    def addActivityToNotes(self, instance):
        logging.debug(f"Calling addActivityToNotes with: graph_id={self.graph_id}, simulation_id={self.simulation_id}, username={self.username.text}")
        return addActivityToNotes(self)

    #Function to start the simulation
    def startSim(self, instance):
        startSim(self)

    #Starts a new simulation or continues one if it is already running
    def createInstance(self, instance):
        createInstance(self, instance)

    #Terminates the simulation
    def terminate(self, instance):
        terminate(self)

    def forceTerminateAdmin(self, instance):
        forceTerminateAdmin(self)

    #Gets the role of the user
    def role(self):
        return role(self)


if __name__ == '__main__':
    mainApp = MainApp()
    MainApp().run()