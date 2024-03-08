from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle

class GreyLabelApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')

        notes = ["Hello, Kivy!", "This is a grey label.", "It's created by changing the background color."]

        # Create a label
        for note in notes:
            label = Label(text=note, size_hint=(1.0, None), height=100)

        # Change background color to grey
            with label.canvas.before:
                Color(0.7, 0.7, 0.7, 1)  # Grey color
                rect = Rectangle(size=label.size, pos=label.pos)
            # Bind the rectangle's size and position to the label's properties
            label.bind(size=self._update_rect(rect), pos=self._update_rect(rect))
            layout.add_widget(label)
            
        return layout

    def _update_rect(self, instance):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

if __name__ == '__main__':
    GreyLabelApp().run()
