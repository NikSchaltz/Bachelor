from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
import requests
import xmltodict
from datetime import date, datetime
import re

from buttons import PatientButton
from api import getEnabledEvents, dbQuery
from config import login, userRole, scheduledReloads
from utilities import hashData
from screens import loginScreen, adminScreen, writeNotesScreen, showNotesScreen
from screens import choosePatientScreen

# def stopReloads():
#     global scheduledReloads
#     for reload in scheduledReloads:
#         Clock.unschedule(reload)
#     scheduledReloads = []

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
        #Creates the buttons for each of the 5 pages in the app
        choose_patient = Button(text ="Vælg patient")
        write_notes = Button(text ="Skriv note")
        see_notes = Button(text ="Se noter")
        logout_button = Button(text ="Log ud")
        events_button = Button(text ="Events")

        self.top_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.05))



        """ self.stop_reload_events = Button(text="Stop reload")
        self.stop_reload_events.bind(on_press=lambda instance: stopReloads())
        self.top_bar.add_widget(self.stop_reload_events) """

        #Adds the buttons to the topbar
        self.top_bar.add_widget(events_button)
        self.top_bar.add_widget(choose_patient)
        self.top_bar.add_widget(see_notes)
        self.top_bar.add_widget(write_notes)
        self.top_bar.add_widget(logout_button)
        #Binds the buttons to the functions that they should run when they are pressed
        see_notes.bind(on_press=self.showNotesScreen)
        write_notes.bind(on_press=self.writeNotesScreen)
        choose_patient.bind(on_press=self.choosePatientScreen)
        choose_patient.bind(on_press=self.hideTopBar)
        logout_button.bind(on_press=self.loginScreen)
        events_button.bind(on_press=self.eventsScreen)

        self.hideTopBar(self)

        return self.top_bar
    
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
        if role != "Select Role":
            if dbQuery(f"SELECT COUNT(*) FROM dcrusers WHERE Email = '{hashData(email)}';", "one") == False:
                dbQuery(f"INSERT INTO dcrusers (Email, Role) VALUES ('{hashData(email)}', '{hashData(role)}');")
        return True

    def login(self, instance):
        req = requests.Session()
        req.auth = (self.username.text, self.password.text)
        login_check = req.get("https://repository.dcrgraphs.net/api/graphs/")

        if login_check.status_code == 200:
            if dbQuery(f"SELECT COUNT(*) > 0 FROM dcrusers WHERE Email = '{hashData(self.username.text)}';", "one") == True:
                if dbQuery(f"SELECT Email FROM dcrusers WHERE Role = '{hashData('Admin')}';","one") == hashData(self.username.text):
                    self.adminScreen(self)
                else:
                    self.choosePatientScreen(self)


    #Function to hide the topbar    
    def hideTopBar(self, instance):
        self.top_bar.disabled = True
        self.top_bar.opacity = 0
    
    #Function to show the topbar
    def showTopBar(self, instance):
        self.top_bar.disabled = False
        self.top_bar.opacity = 1

    #Function to create and show the events screen
    def eventsScreen(self, instance):
        self.cleanScreen(self)

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
        button = Button(text=string, disabled_color=(0, 0, 0, 1), height=800)  # Adjust height as needed
        button.bind(width=lambda instance, value: setattr(instance, 'text_size', (value - 20, None)))  # Adjust text_size
        button.padding = 20  # Add padding on the left side
        if button_num % 2 == 0:
            button.background_disabled_normal = 'images/lightGrey.png'  # Set background color
        else:
            button.background_disabled_normal = 'images/darkGrey.png'
        button.disabled = True  # Disable the button
        button.opacity = 1  # Adjust opacity to visually indicate disabled state
        return button

    #Function to create the layout for the notes
    def showNotesLayout(self, strings):
        string_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        string_layout.bind(minimum_height=string_layout.setter('height'))  # Set minimum height based on content

        for i in range(len(strings)):
            button = self.createNotesFields(strings[i], i)
            button.size_hint_y = None  # Disable size hint along the y-axis
            num_lines = strings[i].count('\n') + 1
            line_height = button.font_size + 5  # Change this line or num_lines + number to change how big a note button can be
            button.height = max(100, num_lines * line_height + 50)
            string_layout.add_widget(button)

        # Wrap the GridLayout in a ScrollView
        scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        scroll_view.add_widget(string_layout)
        return scroll_view

    #Function that shows which patients are available to choose from
    def choosePatientScreen(self, instance):
        cleanScreen(self)
        choosePatientScreen(self)

    def getGraphTitle(self, graph_id):
        req = requests.Session()
        req.auth = (self.username.text, self.password.text)
        response = req.get("https://repository.dcrgraphs.net/api/graphs/" + str(graph_id))
        data = response.text
        match = re.search(r'dcrgraph title="([^"]+)"', data)  # Match the pattern 'data="<looked for text>"'
        return(match.group(1).encode('latin1').decode('utf-8'))


    #Shows the screen where you can write notes
    def writeNotesScreen(self, instance):
        cleanScreen(self)
        writeNotesScreen(self)


    #This function is used to add a dropdown menu to the writeNotesScreen function, so that you can choose which activity you want to write notes for
    def addActivityToNotes(self, instance):
        drop_down = DropDown()

        req = requests.Session()
        req.auth = (self.username.text, self.password.text)
        next_activities_response = req.get("https://repository.dcrgraphs.net/api/graphs/" + 
                                        str(self.graph_id) + "/sims/" + self.simulation_id + "/events")

        events_xml = next_activities_response.text
        events_xml_no_quotes = events_xml[1:len(events_xml)-1]
        events_xml_clean = events_xml_no_quotes.replace('\\\"', "\"")
        events_json = xmltodict.parse(events_xml_clean)

        global userRole
        events = []
        # distinguish between one and multiple events
        if not isinstance(events_json['events']['event'], list):
            events = [events_json['events']['event']]
        else:
            events = events_json['events']['event']

        layout = GridLayout(cols=1, spacing=0, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        for e in events:
            if hashData(e['@roles']) == userRole:
                btn = Button(text=e['@label'], size_hint_y=None, height=44) # change to change the height of each button in the dropdown
                btn.bind(on_release=lambda btn: drop_down.select(btn.text))
                layout.add_widget(btn)

        scroll_view = ScrollView(size_hint=(1, None), height=800)
        scroll_view.add_widget(layout)

        drop_down.add_widget(scroll_view)

        self.selected_activity_notes = Button(text='Generelt')        
        self.selected_activity_notes.bind(on_release=drop_down.open)

        drop_down.bind(on_select=lambda instance, x: setattr(self.selected_activity_notes, 'text', x))

        return self.selected_activity_notes

    #Function to start the simulation
    def startSim(self, instance):
        current_auth = (self.username.text, self.password.text)

        url=f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims"
        auth=current_auth
        req = requests.Session()
        req.auth = auth
        resp = req.post(url)
        resp_headers = resp.headers
        if resp_headers:
            self.simulation_id = resp_headers['simulationID']

        global userRole
        userRole = self.role()

        #Inserts the simulation into the database if it is not already there
        if dbQuery(f"SELECT COUNT(*) FROM dcrprocesses WHERE GraphID = {self.graph_id} AND IsTerminated = 0;", "one") == False:
            today = date.today().strftime('%Y-%m-%d')
            dbQuery(f"INSERT INTO DCRProcesses (GraphID, SimulationID, CreatedDate, IsTerminated) VALUES ('{self.graph_id}' , '{self.simulation_id}', '{today}', 0);")

    #Starts a new simulation or continues one if it is already running
    def createInstance(self, instance):
        self.graph_id = instance.choosePatient(instance)
        #Checks if there is already a simulation running
        if dbQuery(f"SELECT COUNT(*) > 0 FROM dcrprocesses WHERE GraphID = {self.graph_id} AND IsTerminated = 0;", "one") == True:
            simID = dbQuery(f"SELECT SimulationID FROM dcrprocesses WHERE IsTerminated = 0 AND GraphId = {self.graph_id};", "one")
            self.simulation_id = str(simID)
            global userRole
            userRole = self.role()
            #createButtonsOfEnabledEvents(self.graph_id, self.simulation_id, (self.username.text, self.password.text), self.b_right)
        else:
            self.startSim(instance)


    #Terminates the simulation
    def terminate(self, instance):
        pendingEvents = 0
        events_json = getEnabledEvents(self.graph_id, self.simulation_id, (self.username.text, self.password.text))

        events = []
        # distinguish between one and multiple events
        if not isinstance(events_json['events']['event'], list):
            events = [events_json['events']['event']]
        else:
            events = events_json['events']['event']
            
        for e in events:
            if e.get('@pending') == 'true':
                pendingEvents += 1     

        if pendingEvents == 0:
            dbQuery(f"UPDATE DCRprocesses SET IsTerminated = true WHERE SimulationID = {self.simulation_id};")
            self.cleanScreen(self)


    def forceTerminateAdmin(self, instance):
        dbQuery("UPDATE DCRprocesses SET IsTerminated = true WHERE IsTerminated = false;")
    

        
    #Uploads the notes to the api, by sending a post request
    def uploadNote(self, instance):
        #lav et if statement der tjekker om der er skrevet noget i notesBox
        url = (f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims/{self.simulation_id}/events/textbox")
        auth=(self.username.text, self.password.text)
        req = requests.Session()
        req.auth = auth
        json = {"dataXML": f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')} \nAktivitet: {self.selected_activity_notes.text} \n{self.notes_box.text}"}

        req.post(url, json = json)

    #Gets the notes from the api
    def getNotes(self, instance):
        url = (f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims/{self.simulation_id}/")
        auth=(self.username.text, self.password.text)
        req = requests.Session()
        req.auth = auth
        response = req.get(url)
        
        splitEvents = response.text.split("<event ")
        allNotes = []
        for item in splitEvents:
            match = re.search(r'data="([^"]+)"', item)  # Match the pattern 'data="<looked for text>"'
            if match:
                allNotes.append(match.group(1).encode('latin1').decode('utf-8'))  # Ensure proper encoding/decoding
        
        allNotes = [string.replace("&#xA;", "\n") for string in allNotes]

        return allNotes

    #Clears the notes box
    def clearNotesBox(self, instance):
        self.notes_box.text = ""

    #Gets the role of the user
    def role(self):
        return dbQuery(f"SELECT Role FROM dcrusers WHERE Email = '{hashData(self.username.text)}';", "one")


def stopReloads():
    global scheduledReloads
    for reload in scheduledReloads:
        Clock.unschedule(reload)
    scheduledReloads = []

def cleanScreen(app):
    stopReloads()
    app.box_lower.clear_widgets()

if __name__ == '__main__':
    mainApp = MainApp()
    MainApp().run()