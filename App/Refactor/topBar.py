from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

def topBar(self):
    self.top_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.05))
    choose_patient = Button(text="Vælg patient")
    write_notes = Button(text="Skriv note")
    see_notes = Button(text="Se noter")
    logout_button = Button(text="Log ud")
    events_button = Button(text="Events")

    self.top_bar.add_widget(events_button)
    self.top_bar.add_widget(choose_patient)
    self.top_bar.add_widget(see_notes)
    self.top_bar.add_widget(write_notes)
    self.top_bar.add_widget(logout_button)

    see_notes.bind(on_press=self.showNotesScreen)
    write_notes.bind(on_press=self.writeNotesScreen)
    choose_patient.bind(on_press=self.choosePatientScreen)
    choose_patient.bind(on_press=lambda instance: hideTopBar(self))
    logout_button.bind(on_press=self.loginScreen)
    events_button.bind(on_press=self.eventsScreen)

    hideTopBar(self)
    return self.top_bar

def hideTopBar(self):
    self.top_bar.disabled = True
    self.top_bar.opacity = 0

def showTopBar(self):
    self.top_bar.disabled = False
    self.top_bar.opacity = 1
