from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
import xmltodict
import requests
import mysql.connector
from mysql.connector import errorcode
from datetime import date, datetime
import re
import hashlib

from kivy.graphics import Color, Rectangle


userRole = ""

scheduledReloads = []



login = {
    'host': "bachelor-adit-nikolaj.mysql.database.azure.com",
    'user': "bachelorprojekt",
    'password': "Adit&nikolaj",
    'port': 3306,
    'ssl_ca': "DigiCertGlobalRootCA.crt.pem",
    'database': "bachelorprojekt"
    }



#Hashes a string
def hashData(data: str):
    hash_object = hashlib.sha256()
    data_bytes = data.encode()
    hash_object.update(data_bytes)
    hashed_data = hash_object.hexdigest()

    return hashed_data


#gets the tasks that are able to be done in the task list at this moment
def getEnabledEvents(graph_id: str, sim_id: str, auth: (str, str)):
    
    #Connects to the api
    req = requests.Session()
    req.auth = auth
    next_activities_response = req.get("https://repository.dcrgraphs.net/api/graphs/" + 
                                    str(graph_id) + "/sims/" + sim_id + "/events?filter=only-enabled")

    #Reformats the xml to json  
    events_xml = next_activities_response.text
    events_xml_no_quotes = events_xml[1:len(events_xml)-1]
    events_xml_clean = events_xml_no_quotes.replace('\\\"', "\"")
    events_json = xmltodict.parse(events_xml_clean)
    return events_json


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



def stopReloads():
    global scheduledReloads
    for reload in scheduledReloads:
        Clock.unschedule(reload)
    scheduledReloads = []

#Connects to the database and runs a query
def dbQuery(query, statement=None):
    try: #Tries to connect to the database
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
    #If you can connect to the database, it will run the query
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

    #When the button is pressed, it will execute the event, which means accessing the api to execute the event
    def execute_event(self, instance):
        url = (f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims/{self.simulation_id}/events/{self.event_id}")
        auth=(self.username, self.password)
        req = requests.Session()
        req.auth = auth
        req.post(url)

        #Creates the new buttons for the tasks that are able to be done in the task list at this moment
        createButtonsOfEnabledEvents(self.graph_id, self.simulation_id, auth, self.manipulate_box_layout)


#this class is used to make the buttons that are used to choose a patient/resident
class PatientButton(Button):
    def __init__ (self, graph_id: int, text: str):
        Button.__init__(self)
        self.graph_id = graph_id
        self.text = text
        self.bind(on_press=self.choosePatient)

    def choosePatient(self, instance):
        return self.graph_id



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

        
        self.terminate_sim = Button(text="Force terminate")
        self.terminate_sim.bind(on_press=self.forceTerminate)
        self.top_bar.add_widget(self.terminate_sim)

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
        self.cleanScreen(self)
        self.password = TextInput(hint_text="Enter password", password=True, text = "cloud123")
        self.username = TextInput(hint_text="Enter username", text = "bxz911@alumni.ku.dk")
        password_label = Label(text="Password")
        username_label = Label(text="Username")
        login_screen_layout = BoxLayout(orientation='vertical')
        login_boxes = BoxLayout(orientation='horizontal')
        left = BoxLayout(orientation='vertical')
        right = BoxLayout(orientation='vertical')
        bottom = BoxLayout(orientation='horizontal')
        run_sim = Button(text="Create Instance")

        bottom.add_widget(run_sim)

        right.add_widget(self.username)
        right.add_widget(self.password)
        left.add_widget(username_label)
        left.add_widget(password_label)

        login_boxes.add_widget(left)
        login_boxes.add_widget(right)
        login_screen_layout.add_widget(login_boxes)
        login_screen_layout.add_widget(bottom)

        #run_sim.bind(on_press=self.choosePatientScreen)
        run_sim.bind(on_press=self.login)

        self.hideTopBar(self)

        self.box_lower.add_widget(login_screen_layout)

    def adminScreen(self, instance):
        self.cleanScreen(self)
        #banner = Label(text="Add a new user")
        username_label = Label(text="Email")
        role_label = Label(text="Select Role")
        username = TextInput(hint_text="Enter email")
        drop_down_button = Button(text="Select Role")
        logout_button = Button(text="Log out as admin")
        add_user_button = Button(text="Add user")
        terminate_all_sims = Button(text="Terminate all graphs")
        remove_all_users_button = Button(text="Remove all users")

        logout_button.bind(on_press=self.loginScreen)
        terminate_all_sims.bind(on_press=self.forceTerminateAdmin)
        remove_all_users_button.bind(on_press=lambda instance: dbQuery(f"DELETE FROM dcrusers WHERE Role != '{hashData('Admin')}'"))
        add_user_button.bind(on_press=lambda instance: self.addUser(instance, username.text, drop_down_button.text))


        #Allows changing the background color of the banner
        """ banner = Button(text="Add a new user", disabled_color=(0, 0, 0, 1), height=800)  # Adjust height as needed
        #banner.bind(width=lambda instance, value: setattr(instance, 'text_size', (value - 20, None)))  # Adjust text_size
        banner.background_disabled_normal = 'images/lightGrey.png'  # Set background color
        banner.disabled = True  # Disable the button
        banner.opacity = 1  # Adjust opacity to visually indicate disabled state """


        # Add the dropdown roles to the dropdown menu
        drop_down = DropDown()
        roles = ['Dagholdet', 'Aftenholdet', 'Natholdet', 'Admin']
        for role in roles:
            btn = Button(text=role, size_hint_y=None, height=100)
            btn.bind(on_release=lambda btn: drop_down.select(btn.text))
            drop_down.add_widget(btn)

        # Bind the selected option to the dropdown button text
        drop_down.bind(on_select=lambda instance, x: setattr(drop_down_button, 'text', x))
        drop_down_button.bind(on_release=drop_down.open)
        
        admin_screen_layout = BoxLayout(orientation='vertical')
        #add_user_layout = BoxLayout(orientation='vertical')
        add_user_layout_top = BoxLayout(orientation='horizontal')
        add_user_layout_bottom = BoxLayout(orientation='horizontal')
        terminate_remove_all_users_layout = BoxLayout(orientation='horizontal')

        #Creates the layout for the add user part
        add_user_layout_top.add_widget(username_label)
        add_user_layout_top.add_widget(username)
        add_user_layout_bottom.add_widget(role_label)
        add_user_layout_bottom.add_widget(drop_down_button)
        
        #Creates the layout for the terminate and remove all users buttons
        terminate_remove_all_users_layout.add_widget(terminate_all_sims)
        terminate_remove_all_users_layout.add_widget(remove_all_users_button)

        #Creates the layout for the admin screen
        admin_screen_layout.add_widget(logout_button)
        #admin_screen_layout.add_widget(banner)
        admin_screen_layout.add_widget(add_user_layout_top)
        admin_screen_layout.add_widget(add_user_layout_bottom)
        #admin_screen_layout.add_widget(add_user_layout)
        admin_screen_layout.add_widget(add_user_button)
        admin_screen_layout.add_widget(terminate_remove_all_users_layout)

        #Adds it to the app layout
        self.box_lower.add_widget(admin_screen_layout)

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
        self.cleanScreen(self)
        notes = self.getNotes(instance)
        see_notes_layout = ScrollView()
        string_layout = self.showNotesLayout(notes)
        see_notes_layout.add_widget(string_layout)
        self.box_lower.add_widget(see_notes_layout)


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
        self.cleanScreen(self)
        patient_buttons = BoxLayout(orientation='vertical')

        patients = dbQuery("SELECT * FROM DCRGraphs;", "all")
        for patient in patients:
            pButton = PatientButton(patient[0], patient[1])
            pButton.bind(on_press=self.eventsScreen)
            pButton.bind(on_press=self.createInstance)
            pButton.bind(on_press=self.showTopBar)
            patient_buttons.add_widget(pButton)
        
        self.box_lower.add_widget(patient_buttons)

    #Shows the screen where you can write notes
    def writeNotesScreen(self, instance):
        self.cleanScreen(self)
        self.notes_box = TextInput(hint_text="Enter notes")
        drop_down_label = Label(text="Vælg aktivitet")

        upload_notes_layout = BoxLayout(orientation='vertical')
        upload_notes_layout_drop_down = BoxLayout(orientation='vertical')
        upload_notes_layout_buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=200)
        upload_notes = Button(text="Upload notes")

        
        upload_notes.bind(on_press=self.clearNotesBox)
        upload_notes.bind(on_press=self.uploadNote)

        upload_notes_layout.add_widget(self.notes_box)

        upload_notes_layout_drop_down.add_widget(drop_down_label)
        upload_notes_layout_drop_down.add_widget(self.addActivityToNotes(instance))
        upload_notes_layout_buttons.add_widget(upload_notes)
        upload_notes_layout_buttons.add_widget(upload_notes_layout_drop_down)
        upload_notes_layout.add_widget(upload_notes_layout_buttons)

        self.box_lower.add_widget(upload_notes_layout)


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


    #Function to clear the screen of widgets
    def cleanScreen(self, instance):
        stopReloads()
        self.box_lower.clear_widgets()

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
            dbQuery(f"INSERT INTO DCRProcesses (GraphID, SimulationID, ProcessName, CreatedDate, IsTerminated) VALUES ('{self.graph_id}' , '{self.simulation_id}', 'Task List', '{today}', 0);")

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

    def forceTerminate(self, instance):          
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
            match = re.search(r'data="([^"]+)"', item)  # Match the pattern 'data="some_value"'
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
    
    

if __name__ == '__main__':
    mainApp = MainApp()
    MainApp().run()
