import hashlib
from kivy.clock import Clock
from config import scheduledReloads

def hashData(data: str):
    hash_object = hashlib.sha256()
    data_bytes = data.encode()
    hash_object.update(data_bytes)
    hashed_data = hash_object.hexdigest()
    return hashed_data

# def stopReloads():
#     global scheduledReloads
#     for reload in scheduledReloads:
#         Clock.unschedule(reload)
#     scheduledReloads = []

# def cleanScreen(app):
#     stopReloads()
#     app.box_lower.clear_widgets()