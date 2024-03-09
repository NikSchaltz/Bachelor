from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
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
    def __init__(self):
        App.__init__(self)
        self.password = TextInput(hint_text="Enter password", password=True, text = "cloud123")
        self.username = TextInput(hint_text="Enter username", text = "bxz911@alumni.ku.dk")
        self.layout_box = BoxLayout(orientation='vertical')
        self.graph_id = TextInput(hint_text="Enter graph id", text = "1702929")
        self.run_sim = Button(text="Create Instance")
        self.terminate_sim = Button(text="Terminate")
        self.passwordLabel = Label(text="Password")
        self.usernameLabel = Label(text="Username")
        self.graph_idLabel = Label(text="Graph ID")
        self.upload_notes = Button(text="Upload notes")
        self.notesBox = TextInput(hint_text="Enter notes")

    def build(self):
        self.b_outer = BoxLayout()
        self.b_upperLeft = BoxLayout()
        self.b_lowerLeft = BoxLayout(orientation='vertical')
        self.b_upperLeftLeft = BoxLayout(orientation='vertical')
        self.b_upperLeftRight = BoxLayout(orientation='vertical')
        self.b_right = BoxLayout(orientation='vertical')
        self.b_left = BoxLayout(orientation='vertical')
        self.b_lowerLeft.add_widget(self.run_sim)
        self.b_lowerLeft.add_widget(self.terminate_sim)
        self.b_lowerLeft.add_widget(self.upload_notes)
        self.b_lowerLeft.add_widget(self.notesBox)
        self.b_upperLeftRight.add_widget(self.username)
        self.b_upperLeftRight.add_widget(self.password)
        self.b_upperLeftRight.add_widget(self.graph_id)
        self.b_upperLeftLeft.add_widget(self.usernameLabel)
        self.b_upperLeftLeft.add_widget(self.passwordLabel)
        self.b_upperLeftLeft.add_widget(self.graph_idLabel)
        self.b_upperLeft.add_widget(self.b_upperLeftLeft)
        self.b_upperLeft.add_widget(self.b_upperLeftRight)
        self.b_left.add_widget(self.b_upperLeft)
        self.b_left.add_widget(self.b_lowerLeft)
        self.b_outer.add_widget(self.b_left)
        self.b_outer.add_widget(self.b_right)
        self.run_sim.bind(on_press=self.b_create_instance)
        #self.run_sim.bind(on_press=self.remove_widgets)
        self.terminate_sim.bind(on_press=self.b_terminate)
        self.upload_notes.bind(on_press=self.clearNotesBox)
        self.upload_notes.bind(on_press=self.readNotes)
        self.upload_notes.bind(on_press=self.uploadNotes)

        return self.b_outer
    
    def remove_widgets(self, instance):
        self.b_left.clear_widgets()


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
            dbQuery(f"INSERT INTO DCRUsers (Email, Role) VALUES ('{self.username.text}' , 'home care worker');")
        
        if dbQuery(f"SELECT COUNT(*) FROM dcrprocesses WHERE GraphID = {self.graph_id.text} AND IsTerminated = 0;", "one") == False:
            today = date.today().strftime('%Y-%m-%d')
            dbQuery(f"INSERT INTO DCRProcesses (GraphID, SimulationID, ProcessName, CreatedDate, IsTerminated) VALUES ('{self.graph_id.text}' , '{self.simulation_id}', 'Task List', '{today}', 0);")

        create_buttons_of_enabled_events(self.graph_id.text, self.simulation_id, (self.username.text, self.password.text), self.b_right)


    def b_create_instance(self, instance):
        if dbQuery(f"SELECT COUNT(*) > 0 FROM dcrprocesses WHERE GraphID = {self.graph_id.text} AND IsTerminated = 0;", "one") == True:
            simID = dbQuery(f"SELECT SimulationID FROM dcrprocesses WHERE IsTerminated = 0 AND GraphId = {self.graph_id.text};", "one")
            
            self.simulation_id = str(simID)
            global userRole
            userRole = self.role()
            create_buttons_of_enabled_events(self.graph_id.text, self.simulation_id, (self.username.text, self.password.text), self.b_right)
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
        json = {"dataXML": f"{datetime.now().strftime('%Y-%m-%d %H:%M')}: {self.notesBox.text}"}

        req.post(url, json = json)

    def readNotes(self, instance):
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

        print(allNotes)

    def clearNotesBox(self, instance):
        self.notesBox.text = ""



    def role(self):
        return dbQuery(f"SELECT Role FROM dcrusers WHERE Email = '{self.username.text}';", "one")
        

if __name__ == '__main__':
    mainApp = MainApp()
    MainApp().run()
