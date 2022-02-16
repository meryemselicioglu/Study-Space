import psycopg2
from DBConnection import *
from User import *
from flask import (
    Flask,
    g,
    render_template,
    url_for, 
    flash, 
    redirect, 
    request, 
    session, 
    abort
)

app = Flask(__name__)
app.secret_key = 'asd'

@app.before_request
def before_request():
    db = DBConnection('studyspacesboss', 'IPRO497gpd!!', 'studyspacesdbserver.postgres.database.azure.com', 5432, 'postgres')
    conn = db.connect()
    cursor = conn.cursor()
    
    query = 'select email from Users'
    cursor.execute(query)
    conn.commit()
    result_users = cursor.fetchall()
    
    for usr in result_users:
        if usr[1] == session['email']:
            temp_user = User(usr[0], usr[3], usr[4])
            g.user = temp_user
        else:
            g.user = None

