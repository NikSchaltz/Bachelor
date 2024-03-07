from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button

class StringBoxLayout(BoxLayout):
    def __init__(self, strings, **kwargs):
        super(StringBoxLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'
        buttonNum = 0
        for string in strings:
            button = Button(text=string, disabled_color=(0, 0, 0, 1))
            button.bind(width=lambda instance, value: setattr(instance, 'text_size', (value - 20, None)))  # Adjust text_size
            button.padding_x = 20  # Add padding on the left side
            if buttonNum % 2 == 0:
                button.background_disabled_normal = 'images/lightGrey.png'  # Set background color
            else:
                button.background_disabled_normal = 'images/darkGrey.png'
            button.disabled = True  # Disable the button
            button.opacity = 1  # Adjust opacity to visually indicate disabled state
            self.add_widget(button)
            buttonNum += 1


class StringApp(App):
    def build(self):
        strings = [
            "This is a long string that should wrap to a new line if it is too long to fit in its box.",
            "Another long string to demonstrate wrapping.",
            "Yet another long string to show wrapping in action.",
            "Short string."
        ]
        scroll_view = ScrollView()
        string_layout = StringBoxLayout(strings)
        scroll_view.add_widget(string_layout)
        return scroll_view

if __name__ == '__main__':
    StringApp().run()
