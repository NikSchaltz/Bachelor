from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

from api import dbQuery
from utilities import hashData
from buttons import PatientButton
from config import login, userRole, scheduledReloads


def loginScreen(app):
    app.box_lower.clear_widgets()
    app.password = TextInput(hint_text="Enter password", password=True, text="cloud123")
    app.username = TextInput(hint_text="Enter username", text="bxz911@alumni.ku.dk")
    password_label = Label(text="Password")
    username_label = Label(text="Username")
    login_screen_layout = BoxLayout(orientation='vertical')
    login_boxes = BoxLayout(orientation='horizontal')
    left = BoxLayout(orientation='vertical')
    right = BoxLayout(orientation='vertical')
    bottom = BoxLayout(orientation='horizontal')
    run_sim = Button(text="Login to user")

    bottom.add_widget(run_sim)

    right.add_widget(app.username)
    right.add_widget(app.password)
    left.add_widget(username_label)
    left.add_widget(password_label)

    login_boxes.add_widget(left)
    login_boxes.add_widget(right)
    login_screen_layout.add_widget(login_boxes)
    login_screen_layout.add_widget(bottom)

    run_sim.bind(on_press=app.login)

    app.hideTopBar(app)

    app.box_lower.add_widget(login_screen_layout)

# def cleanScreen(app):
#     stopReloads()
#     app.box_lower.clear_widgets()

def adminScreen(app):
    username_label = Label(text="Email")
    role_label = Label(text="Select Role")
    username = TextInput(hint_text="Enter username", text="@alumni.ku.dk")
    drop_down_button = Button(text="Select Role")
    logout_button = Button(text="Log out as admin")
    add_user_button = Button(text="Add user")
    terminate_all_sims = Button(text="Terminate all graphs")
    remove_all_users_button = Button(text="Remove all users")

    logout_button.bind(on_press=app.loginScreen)
    terminate_all_sims.bind(on_press=app.forceTerminateAdmin)
    remove_all_users_button.bind(on_press=lambda instance: dbQuery(f"DELETE FROM dcrusers WHERE Role != '{hashData('Admin')}'"))
    add_user_button.bind(on_press=lambda instance: app.addUser(instance, username.text, drop_down_button.text))

    drop_down = DropDown()
    roles = ['Dagholdet', 'Aftenholdet', 'Natholdet', 'Admin']
    for role in roles:
        btn = Button(text=role, size_hint_y=None, height=100)
        btn.bind(on_release=lambda btn: drop_down.select(btn.text))
        drop_down.add_widget(btn)

    drop_down.bind(on_select=lambda instance, x: setattr(drop_down_button, 'text', x))
    drop_down_button.bind(on_release=drop_down.open)
    
    admin_screen_layout = BoxLayout(orientation='vertical')
    add_user_layout_top = BoxLayout(orientation='horizontal')
    add_user_layout_bottom = BoxLayout(orientation='horizontal')
    terminate_remove_all_users_layout = BoxLayout(orientation='horizontal')

    add_user_layout_top.add_widget(username_label)
    add_user_layout_top.add_widget(username)
    add_user_layout_bottom.add_widget(role_label)
    add_user_layout_bottom.add_widget(drop_down_button)
    
    terminate_remove_all_users_layout.add_widget(terminate_all_sims)
    terminate_remove_all_users_layout.add_widget(remove_all_users_button)

    admin_screen_layout.add_widget(logout_button)
    admin_screen_layout.add_widget(add_user_layout_top)
    admin_screen_layout.add_widget(add_user_layout_bottom)
    admin_screen_layout.add_widget(add_user_button)
    admin_screen_layout.add_widget(terminate_remove_all_users_layout)

    app.box_lower.add_widget(admin_screen_layout)

def choosePatientScreen(app):
    patient_buttons = BoxLayout(orientation='vertical')

    patients = dbQuery("SELECT * FROM DCRGraphs;", "all")
    for id in patients:
        pButton = PatientButton(id[0], app.getGraphTitle(id[0]))
        pButton.bind(on_press=app.eventsScreen)
        pButton.bind(on_press=app.createInstance)
        pButton.bind(on_press=app.showTopBar)
        patient_buttons.add_widget(pButton)
    
    app.box_lower.add_widget(patient_buttons)

def writeNotesScreen(app):
    app.notes_box = TextInput(hint_text="Enter notes")
    drop_down_label = Label(text="Vælg aktivitet")

    upload_notes_layout = BoxLayout(orientation='vertical')
    upload_notes_layout_drop_down = BoxLayout(orientation='vertical')
    upload_notes_layout_buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=200)
    upload_notes = Button(text="Upload notes")

    upload_notes.bind(on_press=app.clearNotesBox)
    upload_notes.bind(on_press=app.uploadNote)

    upload_notes_layout.add_widget(app.notes_box)

    upload_notes_layout_drop_down.add_widget(drop_down_label)
    upload_notes_layout_drop_down.add_widget(app.addActivityToNotes(None))
    upload_notes_layout_buttons.add_widget(upload_notes)
    upload_notes_layout_buttons.add_widget(upload_notes_layout_drop_down)
    upload_notes_layout.add_widget(upload_notes_layout_buttons)

    app.box_lower.add_widget(upload_notes_layout)

def showNotesScreen(app):
    notes = app.getNotes(app)
    see_notes_layout = ScrollView()
    string_layout = app.showNotesLayout(notes)
    see_notes_layout.add_widget(string_layout)
    app.box_lower.add_widget(see_notes_layout)
