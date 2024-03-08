from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex
import xmltodict
import requests
import mysql.connector
from mysql.connector import errorcode
from datetime import date, datetime
import re

global userRole
userRole = ""

login = {
    'host': "bachelor-adit-nikolaj.mysql.database.azure.com",
    'user': "bachelorprojekt",
    'password': "Adit&nikolaj",
    'port': 3306,
    'ssl_ca': "DigiCertGlobalRootCA.crt.pem",
    'database': "bachelorprojekt"
    }


def get_enabled_events(graph_id: str, sim_id: str, auth: (str, str)):
        
    req = requests.Session()
    req.auth = auth
    next_activities_response = req.get("https://repository.dcrgraphs.net/api/graphs/" + 
                                    graph_id + "/sims/" + sim_id + "/events?filter=only-enabled")

    events_xml = next_activities_response.text
    events_xml_no_quotes = events_xml[1:len(events_xml)-1]
    events_xml_clean = events_xml_no_quotes.replace('\\\"', "\"")
    events_json = xmltodict.parse(events_xml_clean)
    return events_json


def create_buttons_of_enabled_events(
    graph_id: str,
    sim_id: str,
    auth: (str, str),
    button_layout: BoxLayout):
    events_json = get_enabled_events(graph_id, sim_id,auth)
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
        if e['@roles'] == userRole:
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

                #add a line of code that colors pending events
                #to distinguish them from non pending events
                button_layout.add_widget(s)


def dbQuery(query, statement=None):
    try: 
        db = mysql.connector.connect(**login)
        print("Connected to the database")
        print("Query:", query)  # Print the query being executed
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else: 
            print(err)
    else:
        if query.startswith("SELECT"):
            cursor = db.cursor()
            cursor.execute(query)
            if statement == "one":
                result = cursor.fetchone()[0]
            if statement == "all":
                result = cursor.fetchall()
            cursor.close()
            db.close()
            return result
        if query.startswith("INSERT") or query.startswith("DELETE") or query.startswith("UPDATE"):
            cursor = db.cursor()
            cursor.execute(query)
            db.commit()
            cursor.close()
            db.close()
            if query.startswith("INSERT"):
                print("Inserted into the database")
            elif query.startswith("UPDATE"):
                print("Updated the database")
            else:
                print("Deleted from the database")



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


    def execute_event(self, instance):
        url = (f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims/{self.simulation_id}/events/{self.event_id}")
        auth=(self.username, self.password)
        req = requests.Session()
        req.auth = auth
        req.post(url)


        """ data = {
            "test": "tester",
            "comment": "json+headers"
            }
        req.post("https://repository.dcrgraphs.net/api/graphs/1702929/comments/", json=data, headers={"Content-Type": "application/json"})
    """
        create_buttons_of_enabled_events(self.graph_id, self.simulation_id, auth, self.manipulate_box_layout)



class MainApp(App):
    def build(self):
        self.box = BoxLayout(orientation='vertical')
        self.box_lower = BoxLayout(orientation='vertical')
        self.box.add_widget(self.topBar(self))
        self.loginScreen(self)
        self.box.add_widget(self.box_lower)
        self.terminate_sim = Button(text="Terminate")

        #self.terminate_sim.bind(on_press=self.b_terminate)
        """ self.choose_patient = Button(text ="Vælg patient")
        self.check_notes = Button(text ="Se noter")
        self.logout = Button(text ="Log ud") """
        #self.top_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.05))
        #self.b_upperLeft = BoxLayout()
        #self.b_lowerLeft = BoxLayout(orientation='vertical')
        #self.b_upperLeftLeft = BoxLayout(orientation='vertical')
        #self.b_upperLeftRight = BoxLayout(orientation='vertical')
        #self.b_right = BoxLayout(orientation='vertical')
        #self.b_left = BoxLayout(orientation='vertical')
        #self.top_bar.add_widget(self.choose_patient)
        #self.top_bar.add_widget(self.check_notes)
        #self.top_bar.add_widget(self.logout)
        #self.b_lowerLeft.add_widget(self.run_sim)
        #self.b_lowerLeft.add_widget(self.terminate_sim)
        #self.b_lowerLeft.add_widget(self.upload_notes)
        #self.b_lowerLeft.add_widget(self.notesBox)
        #self.b_upperLeftRight.add_widget(self.username)
        #self.b_upperLeftRight.add_widget(self.password)
        #self.b_upperLeftRight.add_widget(self.graph_id)
        #self.b_upperLeftLeft.add_widget(self.usernameLabel)
        #self.b_upperLeftLeft.add_widget(self.passwordLabel)
        #self.b_upperLeftLeft.add_widget(self.graph_idLabel)
        #self.b_upperLeft.add_widget(self.b_upperLeftLeft)
        #self.b_upperLeft.add_widget(self.b_upperLeftRight)
        #self.b_left.add_widget(self.b_upperLeft)
        #self.b_left.add_widget(self.b_lowerLeft)
        #self.b_outer.add_widget(self.b_left)
        #self.b_outer.add_widget(self.b_right)
        #self.run_sim.bind(on_press=self.b_create_instance)
        #self.run_sim.bind(on_press=self.remove_widgets)
        #self.upload_notes.bind(on_press=self.clearNotesBox)
        #self.upload_notes.bind(on_press=self.getNotes)
        #self.upload_notes.bind(on_press=self.uploadNotes)

        return self.box
    
    def topBar(self, instance):
        self.choose_patient = Button(text ="Vælg patient")
        self.write_notes = Button(text ="Skriv note")
        self.see_notes = Button(text ="Se noter")
        self.login = Button(text ="Log ud")
        self.events = Button(text ="Events")

        self.top_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.05))

        self.top_bar.add_widget(self.events)
        self.top_bar.add_widget(self.choose_patient)
        self.top_bar.add_widget(self.see_notes)
        self.top_bar.add_widget(self.write_notes)
        self.top_bar.add_widget(self.login)
        self.see_notes.bind(on_press=self.seeNotesScreen)
        self.write_notes.bind(on_press=self.writeNotesScreen)
        self.choose_patient.bind(on_press=self.choosePatientScreen)
        self.login.bind(on_press=self.loginScreen)
        self.events.bind(on_press=self.eventsScreen)
        #self.events.bind(on_press=self.b_create_instance)

        self.hideTopBar(self)

        return self.top_bar
    
    def loginScreen(self, instance):
        self.cleanScreen(self)
        self.password = TextInput(hint_text="Enter password", password=True, text = "cloud123")
        self.username = TextInput(hint_text="Enter username", text = "bxz911@alumni.ku.dk")
        self.graph_id = TextInput(hint_text="Enter graph id", text = "1702929")
        self.passwordLabel = Label(text="Password")
        self.usernameLabel = Label(text="Username")
        self.graph_idLabel = Label(text="Graph ID")
        self.login_screen_layout = BoxLayout(orientation='vertical')
        self.login_boxes = BoxLayout(orientation='horizontal')
        self.left = BoxLayout(orientation='vertical')
        self.right = BoxLayout(orientation='vertical')
        self.bottom = BoxLayout(orientation='horizontal')
        self.run_sim = Button(text="Create Instance")

        self.bottom.add_widget(self.run_sim)
        #self.bottom.add_widget(self.terminate_sim)

        self.right.add_widget(self.username)
        self.right.add_widget(self.password)
        self.right.add_widget(self.graph_id)
        self.left.add_widget(self.usernameLabel)
        self.left.add_widget(self.passwordLabel)
        self.left.add_widget(self.graph_idLabel)

        self.login_boxes.add_widget(self.left)
        self.login_boxes.add_widget(self.right)
        self.login_screen_layout.add_widget(self.login_boxes)
        self.login_screen_layout.add_widget(self.bottom)

        self.run_sim.bind(on_press=self.b_create_instance)
        self.run_sim.bind(on_press=self.choosePatientScreen)
        self.run_sim.bind(on_press=self.showTopBar)

        self.hideTopBar(self)

        self.box_lower.add_widget(self.login_screen_layout)
        
    def hideTopBar(self, instance):
        self.top_bar.disabled = True
        self.top_bar.opacity = 0
    
    def showTopBar(self, instance):
        self.top_bar.disabled = False
        self.top_bar.opacity = 1

    def eventsScreen(self, instance):
        self.cleanScreen(self)

        create_buttons_of_enabled_events(self.graph_id.text, self.simulation_id, (self.username.text, self.password.text), self.box_lower)

    def seeNotesScreen(self, instance):
        self.cleanScreen(self)
        notes = self.getNotes(instance)
        self.see_notes_layout = ScrollView()
        string_layout = self.create_string_layout(notes)
        self.see_notes_layout.add_widget(string_layout)
        self.box_lower.add_widget(self.see_notes_layout)

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

    def create_string_layout(self, strings):
        string_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        string_layout.bind(minimum_height=string_layout.setter('height'))  # Set minimum height based on content

        for i in range(len(strings)):
            button = self.createNotesFields(strings[i], i)
            button.size_hint_y = None  # Disable size hint along the y-axis
            num_lines = strings[i].count('\n') + 1
            line_height = button.font_size + 5  # Change here to change how big a note button can be
            button.height = max(100, num_lines * line_height + 50)
            string_layout.add_widget(button)

        # Wrap the GridLayout in a ScrollView
        scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        scroll_view.add_widget(string_layout)
        return scroll_view

    def choosePatientScreen(self, instance):
        self.cleanScreen(self)



    def writeNotesScreen(self, instance):
        self.cleanScreen(self)
        self.notesBox = TextInput(hint_text="Enter notes")

        self.upload_notes_layout = BoxLayout(orientation='vertical')
        self.upload_notes = Button(text="Upload notes")

        self.upload_notes.bind(on_press=self.clearNotesBox)
        self.upload_notes.bind(on_press=self.uploadNotes)

        self.upload_notes_layout.add_widget(self.notesBox)
        self.upload_notes_layout.add_widget(self.upload_notes)

        # Add upload_notes_layout to box_lower
        self.box_lower.add_widget(self.upload_notes_layout)
    
    def cleanScreen(self, instance):
        self.box_lower.clear_widgets()

    def start_sim(self, instance):
        self.current_auth = (self.username.text, self.password.text)

        url=f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id.text}/sims"
        auth=self.current_auth
        req = requests.Session()
        req.auth = auth
        resp = req.post(url)
        resp_headers = resp.headers
        if resp_headers:
            self.simulation_id = resp_headers['simulationID']

        global userRole
        userRole = self.role()

        if dbQuery(f"SELECT COUNT(*) FROM dcrusers WHERE Email = '{self.username.text}';","one") == False:
            dbQuery(f"INSERT INTO DCRUsers (Email, Role) VALUES ('{self.username.text}' , 'Personale');")
        
        if dbQuery(f"SELECT COUNT(*) FROM dcrprocesses WHERE GraphID = {self.graph_id.text} AND IsTerminated = 0;", "one") == False:
            today = date.today().strftime('%Y-%m-%d')
            dbQuery(f"INSERT INTO DCRProcesses (GraphID, SimulationID, ProcessName, CreatedDate, IsTerminated) VALUES ('{self.graph_id.text}' , '{self.simulation_id}', 'Task List', '{today}', 0);")

        #create_buttons_of_enabled_events(self.graph_id.text, self.simulation_id, (self.username.text, self.password.text), self.b_right)


    def b_create_instance(self, instance):
        if dbQuery(f"SELECT COUNT(*) > 0 FROM dcrprocesses WHERE GraphID = {self.graph_id.text} AND IsTerminated = 0;", "one") == True:
            
            if dbQuery(f"SELECT COUNT(*) FROM dcrusers WHERE Email = '{self.username.text}';","one") == False:
                dbQuery(f"INSERT INTO DCRUsers (Email, Role) VALUES ('{self.username.text}' , 'Personale');")
            
            simID = dbQuery(f"SELECT SimulationID FROM dcrprocesses WHERE IsTerminated = 0 AND GraphId = {self.graph_id.text};", "one")
            self.simulation_id = str(simID)
            global userRole
            userRole = self.role()
            #create_buttons_of_enabled_events(self.graph_id.text, self.simulation_id, (self.username.text, self.password.text), self.b_right)
        else:
            self.start_sim(instance)


    
    def b_terminate(self, instance):
        self.terminate(instance)

    def terminate(self, instance):
        pendingEvents = 0
        events_json = get_enabled_events(self.graph_id.text, self.simulation_id, (self.username.text, self.password.text))

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
            self.b_right.clear_widgets()
        

    def uploadNotes(self, instance):
        #lav et if statement der tjekker om der er skrevet noget i notesBox
        url = (f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id.text}/sims/{self.simulation_id}/events/textbox")
        auth=(self.username.text, self.password.text)
        req = requests.Session()
        req.auth = auth
        json = {"dataXML": f"{datetime.now().strftime('%Y-%m-%d %H:%M')}: \n{self.notesBox.text}"}

        req.post(url, json = json)

    def getNotes(self, instance):
        url = (f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id.text}/sims/{self.simulation_id}/")
        auth=(self.username.text, self.password.text)
        req = requests.Session()
        req.auth = auth
        response = req.get(url)
        
        splitEvents = response.text.split("<event ")
        allNotes = []
        for item in splitEvents:
            match = re.search(r'data="([^"]+)"', item)  # Match the pattern 'data="some_value"'
            if match:
                allNotes.append(match.group(1).encode('latin1').decode('utf-8'))  # Ensure proper encoding/decoding
        
        allNotes = [string.replace("&#xA;", "\n") for string in allNotes]

        return allNotes

    def clearNotesBox(self, instance):
        self.notesBox.text = ""


    def role(self):
        return dbQuery(f"SELECT Role FROM dcrusers WHERE Email = '{self.username.text}';", "one")
        

if __name__ == '__main__':
    mainApp = MainApp()
    MainApp().run()
