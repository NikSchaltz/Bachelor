from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

def topBar(app):
    app.top_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.05))
    choose_patient = Button(text="Vælg patient")
    write_notes = Button(text="Skriv note")
    see_notes = Button(text="Se noter")
    logout_button = Button(text="Log ud")
    events_button = Button(text="Events")

    app.top_bar.add_widget(events_button)
    app.top_bar.add_widget(choose_patient)
    app.top_bar.add_widget(see_notes)
    app.top_bar.add_widget(write_notes)
    app.top_bar.add_widget(logout_button)

    see_notes.bind(on_press=app.showNotesScreen)
    write_notes.bind(on_press=app.writeNotesScreen)
    choose_patient.bind(on_press=app.choosePatientScreen)
    choose_patient.bind(on_press=lambda instance: hideTopBar(app))
    logout_button.bind(on_press=app.loginScreen)
    events_button.bind(on_press=app.eventsScreen)

    hideTopBar(app)
    return app.top_bar

def hideTopBar(app):
    app.top_bar.disabled = True
    app.top_bar.opacity = 0

def showTopBar(app):
    app.top_bar.disabled = False
    app.top_bar.opacity = 1
