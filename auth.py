import json

def load_users():
    with open("users.json") as f:
        return json.load(f)

def authenticate(username, password):

    users = load_users()

    if username in users:

        if users[username]["password"] == password:
            return users[username]["role"]

    return None