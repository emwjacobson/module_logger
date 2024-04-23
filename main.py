from flask import Flask, request, g
from datetime import datetime
import sqlite3


app = Flask(__name__)

DATABASE = "modules.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.cursor().execute("CREATE TABLE IF NOT EXISTS module_loads (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, module TEXT, datetime DATETIME);")
        db.commit()
    return db

def get_cursor():
    return get_db().cursor()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.commit()
        db.close()

@app.route("/log", methods = ["POST"])
def log():
    content = request.json
    print(content)
    username = content['username']
    module = content['module']
    dt = datetime.now()

    data = {
        "username": username,
        "module": module,
        "dt": dt
    }

    get_cursor().execute("INSERT INTO module_loads (username, module, datetime) VALUES (:username, :module, :dt)", data)
    get_db().commit()

    return F"{username} is loading {module} at {dt}\n"
