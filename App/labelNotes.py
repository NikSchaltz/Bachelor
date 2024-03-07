from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Line


def build_layout():
    layout = BoxLayout(orientation='vertical', spacing=10)

    texts = [
        "This is a long text that will wrap around to fit the label width",
        "Another long text that should wrap around properly in the label",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed eget elit eget nibh accumsan placerat.",
        "Short text",
        "A longer text to demonstrate text wrapping functionality in Kivy labels",
        "A longer text to demonstrate text wrapping functionality in Kivy labels",
        "A longer text to demonstrate text wrapping functionality in Kivy labels",
        "A longer text to demonstrate text wrapping functionality in Kivy labels",
        "A longer text to demonstrate text wrapping functionality in Kivy labels",
        "A longer text to demonstrate text wrapping functionality in Kivy labels",
        "A longer text to demonstrate text wrapping functionality in Kivy labels"
    ]

    max_label_height = max(len(text.split('\n')) * 20 for text in texts)

    for text in texts:
        label = create_label(text, max_label_height)
        layout.add_widget(label)
        add_separator_line(layout)

    return layout


def create_label(text, max_height):
    label = Label(text=text, size_hint_y=None, height=max_height, halign='left', valign='top', padding=(10, 20, 0, 0))
    label.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
    label.texture_update()
    return label


def add_separator_line(layout):
    separator_line = Label()
    separator_line.bind(size=update_line)
    layout.add_widget(separator_line)

def update_line(instance, value):
    instance.canvas.before.clear()
    with instance.canvas.before:
        Color(1, 1, 1, 1)  # White color
        Line(points=[instance.x, instance.y, instance.x + instance.width, instance.y], width=1)


class WrappedLabelsApp(App):
    def build(self):
        return build_layout()


if __name__ == "__main__":
    WrappedLabelsApp().run()
