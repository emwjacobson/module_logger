from flask import Flask, request, g
import sqlite3


app = Flask(__name__)

DATABASE = "modules.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.cursor().execute("CREATE TABLE IF NOT EXISTS module_loads (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, module TEXT, jid INTEGER);")
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
    jid = content['jid']

    data = {
        "username": username,
        "module": module,
        "jid": jid
    }

    get_cursor().execute("INSERT INTO module_loads (username, module, jid) VALUES (:username, :module, :jid)", data)
    get_db().commit()

    return F"{username} is loading {module} from job {jid}\n"
