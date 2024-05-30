from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.dropdown import DropDown
import requests
import xmltodict
import re

from utilities import hashData
from datetime import datetime
from config import login, userRole, scheduledReloads

# Configure logging
import logging
logging.basicConfig(level=logging.DEBUG)


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

def showNotesLayout(self, strings):
    string_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
    string_layout.bind(minimum_height=string_layout.setter('height'))  # Set minimum height based on content

    for i in range(len(strings)):
        button = createNotesFields(self, strings[i], i)
        button.size_hint_y = None  # Disable size hint along the y-axis
        num_lines = strings[i].count('\n') + 1
        line_height = button.font_size + 5  # Change this line or num_lines + number to change how big a note button can be
        button.height = max(100, num_lines * line_height + 50)
        string_layout.add_widget(button)

    # Wrap the GridLayout in a ScrollView
    scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
    scroll_view.add_widget(string_layout)
    return scroll_view

def getNotes(self):
    url = (f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims/{self.simulation_id}/")
    auth = (self.username.text, self.password.text)
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

    return allNotes if allNotes else []

def uploadNote(self, instance=None):
    url = (f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims/{self.simulation_id}/events/textbox")
    auth = (self.username.text, self.password.text)
    req = requests.Session()
    req.auth = auth
    json = {"dataXML": f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')} \nAktivitet: {self.selected_activity_notes.text} \n{self.notes_box.text}"}

    req.post(url, json=json)

def clearNotesBox(self):
    self.notes_box.text = ""

def addActivityToNotes(self):

    req = requests.Session()
    req.auth = (self.username.text, self.password.text)
    next_activities_response = req.get("https://repository.dcrgraphs.net/api/graphs/" + 
                                    str(self.graph_id) + "/sims/" + self.simulation_id + "/events")

    events_xml = next_activities_response.text
    events_xml_no_quotes = events_xml[1:len(events_xml)-1]
    events_xml_clean = events_xml_no_quotes.replace('\\\"', "\"")
    events_json = xmltodict.parse(events_xml_clean)

    events = []
    # distinguish between one and multiple events
    if not isinstance(events_json['events']['event'], list):
        events = [events_json['events']['event']]
    else:
        events = events_json['events']['event']

    return events