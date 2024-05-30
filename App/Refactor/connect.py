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
from notes import createNotesFields, showNotesLayout, clearNotesBox, getNotes, addActivityToNotes, uploadNote
from topBar import topBar, hideTopBar, showTopBar

def loginUser(self):
    req = requests.Session()
    req.auth = (self.username.text, self.password.text)
    login_check = req.get("https://repository.dcrgraphs.net/api/graphs/")

    if login_check.status_code == 200:
        if dbQuery(f"SELECT COUNT(*) > 0 FROM dcrusers WHERE Email = '{hashData(self.username.text)}';", "one") == True:
            if dbQuery(f"SELECT Email FROM dcrusers WHERE Role = '{hashData('Admin')}';","one") == hashData(self.username.text):
                self.adminScreen(self)
            else:
                self.choosePatientScreen(self)

def addUser(self, email, role):
    if role != "Select Role":
        if dbQuery(f"SELECT COUNT(*) FROM dcrusers WHERE Email = '{hashData(email)}';", "one") == False:
            dbQuery(f"INSERT INTO dcrusers (Email, Role) VALUES ('{hashData(email)}', '{hashData(role)}');")
    return True

def startSim(self):
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

def getGraphTitle(self, graph_id):
    req = requests.Session()
    req.auth = (self.username.text, self.password.text)
    response = req.get("https://repository.dcrgraphs.net/api/graphs/" + str(graph_id))
    data = response.text
    match = re.search(r'dcrgraph title="([^"]+)"', data)  # Match the pattern 'data="<looked for text>"'
    return(match.group(1).encode('latin1').decode('utf-8'))

def createInstance(self, instance):
    self.graph_id = instance.choosePatient(instance)
    #Checks if there is already a simulation running
    if dbQuery(f"SELECT COUNT(*) > 0 FROM dcrprocesses WHERE GraphID = {self.graph_id} AND IsTerminated = 0;", "one") == True:
        simID = dbQuery(f"SELECT SimulationID FROM dcrprocesses WHERE IsTerminated = 0 AND GraphId = {self.graph_id};", "one")
        self.simulation_id = str(simID)
        global userRole
        userRole = self.role()
    else:
        self.startSim(instance)

def role(self):
    return dbQuery(f"SELECT Role FROM dcrusers WHERE Email = '{hashData(self.username.text)}';", "one")

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

def forceTerminateAdmin(self):
    dbQuery("UPDATE DCRprocesses SET IsTerminated = true WHERE IsTerminated = false;")