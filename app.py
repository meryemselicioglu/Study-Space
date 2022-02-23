import time
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
#conn, cursor = None
#setup db connection
db = DBConnection('studyspacesboss', 'IPRO497gpd!!', 'studyspacesdbserver.postgres.database.azure.com', 5432, 'postgres')
conn = db.connect()
cursor = conn.cursor()
conn.autocommit = True

def add_reservation(user_id, room_id, group_size, start_time, end_time):
    query = f"insert into reservations values (3, {user_id}, {room_id}, 3, 'reserved', {group_size}, {time.time()}, {start_time}, {end_time})"
    cursor.execute(query)
    conn.commit()

# @app.before_request
# def before_request():
    
    
    # #check if user is in session and put it in 'g'
    # g.user = None
    # query = ''
    # cursor.execute(query)
    # conn.commit()
    # result_users = cursor.fetchall()
    
    # users_logged_in = [usr for usr in result_users if usr[1] == session['email']]
    # if users_logged_in:
    #     logged_in_user = users_logged_in[0]
    #     g.user = User(logged_in_user[0], logged_in_user[1], logged_in_user[2], logged_in_user[3], logged_in_user[5], logged_in_user[4])

# @app.teardown_request
# def after_request(error=None):
#     conn.close()
#     if error:
#         print(str(error))


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/room_info.html', )
def rooms():
    return render_template('room_info.html')

@app.route('/confirmation.html', methods=['POST', 'GET'])
def confirm():
    x = request.args.get("name")
    y = request.args.get("start")
    z = request.args.get("end")

    if request.method == 'GET':
        print("here")
        add_reservation(3, 3, 6, "5", "7")
    return render_template('confirmation.html', x=x, y=y, z=z)    

if __name__ == "__main__":
    app.static_folder='resources'
    app.run(debug=True)