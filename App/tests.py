import pytest
from main import *
import main
from kivy.clock import Clock

from main import MainApp

""" 
def test_hashData():
    input_1 = "Hello World"
    input_2 = "Hello World"
    assert hashData(input_1) == hashData(input_2), "Hashing the same thing twice should return the same hash."

    input_3 = "Hello World"
    input_4 = "hello world"
    assert hashData(input_3) != hashData(input_4), "Hashing the same thing with different casing should return different hashes."

    input_5 = "Hello World"
    input_6 = hashData(input_5)
    assert input_5 != input_6, "Hashing a string should return a different string."

    input_7 = "bxz911@alumni.ku.dk"
    input_8 = "bxz911@alumni.ku.dk"
    assert hashData(input_7) == hashData(input_8), "Hashing special characters should return the same hash."



def test_getEnabledEvents():
    #kan ikke laves før alle grafer er færdige
    return True


def add_one(dt):
    global counter
    counter += 1

def test_stopReloads_Clock():
    main.scheduledReloads = []
    global counter
    counter = 0

    add_one(None)
    assert counter == 1

    Clock.schedule_once(add_one, 0.1)

    Clock.tick()
    
    assert counter == 2

    Clock.schedule_once(add_one, 0.1)
    main.scheduledReloads.append(add_one)
    stopReloads()
    for i in range(99):
        Clock.tick()
    assert counter == 2, "stopReloads should stop scheduled reloads."
    
def test_stopReloads_clear_list():
    main.scheduledReloads = []
    main.scheduledReloads.append(1)
    assert main.scheduledReloads == [1], "scheduledReloads should contain 1."

    stopReloads()
    assert main.scheduledReloads == [], "stopReloads should clear the scheduledReloads list."



def test_dbQuery():
    #Insert test
    dbQuery("Truncate tests;")
    dbQuery("INSERT INTO tests (Email, Role) VALUES ('HCW1', 'dagsholdet')")

    assert dbQuery("SELECT * FROM tests WHERE Email = 'HCW1'", "all") == [('HCW1', 'dagsholdet')], "Insert query should return [('HCW1', 'dagsholdet')]."

    #Update test
    dbQuery("UPDATE tests SET Role = 'aftenholdet' WHERE Email = 'HCW1'")
    result = dbQuery("SELECT * FROM tests WHERE Email = 'HCW1'", "all")
    assert result == [('HCW1', 'aftenholdet')], "Update query should return [('HCW1', 'aftenholdet')]."
    assert result != [('HCW1', 'dagsholdet')], "Update query should change it such that it does not return [('HCW1', 'dagsholdet')]."

    #Delete test
    dbQuery("DELETE FROM tests WHERE Email = 'HCW1'")
    assert dbQuery("SELECT * FROM tests WHERE Email = 'HCW1'", "all") == [], "Delete query should return []."

    #Truncate test
    dbQuery("INSERT INTO tests (Email, Role) VALUES ('HCW1', 'natholdet')")
    assert dbQuery("SELECT * FROM tests WHERE Email = 'HCW1'", "all") == [('HCW1', 'natholdet')], "Insert query should return [('HCW1', 'natholdet')]."

    dbQuery("Truncate tests;")
    assert dbQuery("SELECT * FROM tests", "all") == [], "Truncate query should return []."


def test_init_SimulationButton_true():
    button = SimulationButton("E_ID", 123, 456, "lorem", "ipsum", "B_Label")

    assert button.event_id == "E_ID", "event_id should be 'E_ID'."
    assert button.graph_id == 123, "graph_id should be 123."
    assert button.simulation_id == 456, "simulation_id should be 456."
    assert button.username == "lorem", "username should be 'lorem'."
    assert button.password == "ipsum", "password should be 'ipsum'."
    assert button.text == "B_Label", "text should be 'B_Label'."

def test_init_SimulationButton_false():
    button = SimulationButton("E_ID", 123, 456, "lorem", "ipsum", "B_Label")

    assert button.event_id != "event_id", "event_id should not be 'button.event_id'."
    assert button.graph_id != "graph_id", "graph_id should not be 'button.graph_id'."
    assert button.simulation_id != "simulation_id", "simulation_id should not be 'button.simulation_id'."
    assert button.username != "username", "username should not be 'button.username'."
    assert button.password != "password", "password should not be 'button.password'."
    assert button.text != "text", "text should not be 'button.text'."


def test_init_PatientButton_true():
    button = PatientButton(123, "Lorem ipsum")

    assert button.graph_id == 123, "graph_id should be '123'."
    assert button.text == "Lorem ipsum", "text should be 'Lorem ipsum'."

def test_init_PatientButton_false():
    button = PatientButton(123, "Lorem ipsum")

    assert button.graph_id != "graph_id", "graph_id should not be 'button.graph_id'."
    assert button.text != "text", "text should not be 'button.text'."


def test_choosePatient_PatientButton():
    button = PatientButton(123, "Lorem ipsum")
    graph_id = button.choosePatient(button)

    assert graph_id == 123, "graph_id should be 123."

    assert graph_id != 111, "graph_id should not be 111."


def test_addUser():
    mainApp = MainApp()
    #Resetting dcrUsers for this test
    dbQuery(f"DELETE FROM dcrusers WHERE Role != '{hashData('Admin')}'")

    #Adding a user
    mainApp.addUser("HCW1", "dagsholdet")

    result = dbQuery(f"SELECT * FROM dcrusers WHERE Role != '{hashData('Admin')}'", "all")
    
    expected_result = (hashData('HCW1'), hashData('dagsholdet'))

    assert result == [expected_result], "Adding a user should add a user to the database."

    
    #Adding the same user again but with a different role
    mainApp.addUser("HCW1", "natholdet")

    result = dbQuery(f"SELECT * FROM dcrusers WHERE Role <> '{hashData('Admin')}'", "all")

    expected_result = (hashData('HCW1'), hashData('dagsholdet'))

    assert result == [expected_result], "Trying to add the same user again shouldn't add the user again."


def test_deleteAllUsers():
    mainApp = MainApp()
    #adding a user
    mainApp.addUser("deleteUserTest", "dagsholdet")

    result = dbQuery(f"SELECT Count(*) FROM dcrusers WHERE Role = '{hashData('dagsholdet')}'", "one")

    assert result >= 1, "There should be 1 user in the database."

    mainApp.deleteAllUsers()

    assert dbQuery(f"SELECT Count(*) FROM dcrusers WHERE Role != '{hashData('Admin')}'", "one") == 0, "There should be 0 users in the database."
     """

def test_createNotesFields():
    mainApp = MainApp()
    
    button = mainApp.createNotesFields("hej", 1)

    assert button.text == "hej", "button.text should be 'hej'."

    button = mainApp.createNotesFields("Β, β", 1)

    assert button.text != "Β, β"

""" 
def test_getGraphTitle():
    mainApp = MainApp()

    
    auth = ("bxz911@alumni.ku.dk", "cloud123")

    title = mainApp.getGraphTitle(1706803, auth)

    assert title == "Borger A", "title should be 'Borger A'."

    assert title != "Borger B", "title should not be 'Borger B'."



def test_forceTerminateAdmin():
    mainApp = MainApp()

    dbQuery("Truncate dcrprocesses;")

    dbQuery("INSERT INTO dcrprocesses (GraphID, SimulationID, CreatedDate, IsTerminated) VALUES (123, 456, '2024-05-23', 0)")
    dbQuery("INSERT INTO dcrprocesses (GraphID, SimulationID, CreatedDate, IsTerminated) VALUES (111, 222, '2024-05-23', 0)")

    result = dbQuery("SELECT GraphID FROM dcrprocesses WHERE IsTerminated = 0", "all")

    expected_result = [(111,), (123,)]
    print(result)

    assert result == expected_result, "The 2 inserted processes should not be terminated."

    mainApp.forceTerminateAdmin(mainApp)

    result = dbQuery("SELECT GraphID FROM dcrprocesses WHERE IsTerminated = 0", "all")

    assert result == [], "All processes should be terminated."

    dbQuery("Truncate dcrprocesses;")



def test_getRole():
    mainApp = MainApp()
    mainApp.deleteAllUsers()
    #dbQuery(f"DELETE FROM dcrusers WHERE Role != '{hashData('Admin')}'")
    dbQuery(f"INSERT INTO dcrusers (Email, Role) VALUES ('{hashData('HCW1')}', '{hashData('dagsholdet')}')")

    assert mainApp.getRole("HCW1") == hashData('dagsholdet'), "Role should be 'dagsholdet'."
    dbQuery(f"DELETE FROM dcrusers WHERE Role != '{hashData('Admin')}'")




 """
