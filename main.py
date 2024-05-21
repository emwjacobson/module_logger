from flask import Flask, request, g
from datetime import datetime
import logging
import psycopg

app = Flask(__name__)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


DATABASE = "modules.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db_data = dict()
        with open("variables.env", 'r') as env:
            lines = env.readlines()
            for line in lines:
                line = line.strip()
                key, value = line.split("=")
                db_data[key] = value
        db = g._database = psycopg.connect(F"host={db_data['DB_HOST']} dbname={db_data['DB_NAME']} user={db_data['DB_USER']} password={db_data['DB_PASSWORD']}")
        db.cursor().execute("CREATE TABLE IF NOT EXISTS module_loads (id SERIAL PRIMARY KEY, username TEXT, module TEXT, hostname TEXT, jid INTEGER, datetime TIMESTAMP);")
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
    username = content['username']
    module = content['module']
    dt = datetime.now()
    if content['jid'] == "":
        app.logger.warning(F"Got invalid Slurm Job ID from {username} loading {module} at {dt} \n")
        jid = -1
    else:
        jid = content['jid']
    
    if content['hostname'] == "":
        app.logger.warning(F"Got invalid hostname from {username} loading {module} at {dt} \n")
        hostname = ""
    else:
        hostname = content['hostname']

    data = {
        "username": username,
        "module": module,
        "jid": jid,
        "dt": dt,
        "hostname": hostname
    }

    get_cursor().execute("INSERT INTO module_loads (username, module, hostname, jid, datetime) VALUES (%(username)s, %(module)s, %(hostname)s, %(jid)s, %(dt)s)", data)
    get_db().commit()

    app.logger.info(F"Got {username} loading {module} from {hostname} (JID: {jid}) at {dt} \n")

    return F"{username} is loading {module} at {dt}\n"

