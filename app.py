import psycopg2
from database.DBConnection import *
from database.User import *
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
app.secret_key = 'gpd'
conn = None

@app.before_request
def before_request():
    #setup db connection
    db = DBConnection('studyspacesboss', 'IPRO497gpd!!', 'studyspacesdbserver.postgres.database.azure.com', 5432, 'postgres')
    conn = db.connect()
    cursor = conn.cursor()
    
    #check if user is in session and put it in 'g'
    g.user = None
    query = 'select email from Users'
    cursor.execute(query)
    conn.commit()
    result_users = cursor.fetchall()
    
    users_logged_in = [usr for usr in result_users if usr[1] == session['email']]
    if users_logged_in:
        logged_in_user = users_logged_in[0]
        g.user = User(logged_in_user[0], logged_in_user[1], logged_in_user[2], logged_in_user[3], logged_in_user[5], logged_in_user[4])

@app.teardown_request
def after_request(error=None):
    conn.close()
    if error:
        print(str(error))


@app.route('/')
def test():
    return render_template('index.html')

if __name__ == "__main__":
    app.static_folder='resources'
    app.run(debug=True)