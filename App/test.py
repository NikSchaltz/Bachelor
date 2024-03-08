from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout


class ScrollableGridApp(App):
    def build(self):
        # Set the size of the window (optional)
        Window.size = (500, 500)
        
        # Create the ScrollView
        self.scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        
        # Create the GridLayout with custom settings
        self.grid_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        # Make sure the height is such that there is something to scroll
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))
        
        self.seeNotesScreen(self)
        
        # Add GridLayout to ScrollView
        self.scroll_view.add_widget(self.grid_layout)
        
        return self.scroll_view

    def seeNotesScreen(self, instance):
        # Clean the existing screen        
        # Get notes and create string layout
        notes = ["Note 1", "Note 2", "Note 3", "Note 4"]  # Replace this with your own notes
        
        # Create buttons using createNotesFields method and add them to grid layout
        for i, note in enumerate(notes):
            button = self.createNotesFields(note, i)
            self.grid_layout.add_widget(button)

    def createNotesFields(self, string, button_num):
        button = Button(text=string, disabled_color=(0, 0, 0, 1))
        button.bind(width=lambda instance, value: setattr(instance, 'text_size', (value - 20, None)))  # Adjust text_size
        button.padding = 20  # Add padding on the left side
        if button_num % 2 == 0:
            button.background_disabled_normal = 'images/lightGrey.png'  # Set background color
        else:
            button.background_disabled_normal = 'images/darkGrey.png'
        button.disabled = True  # Disable the button
        button.opacity = 1  # Adjust opacity to visually indicate disabled state
        return button

if __name__ == '__main__':
    ScrollableGridApp().run()
