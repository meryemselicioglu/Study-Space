from datetime import datetime
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
db = DBConnection('studyspacesboss', 'IPRO497gpd!!', 'studyspacesdbserver.postgres.database.azure.com', 5432, 'postgres')
conn = db.connect()
cursor = conn.cursor()
conn.autocommit = True
counter = 3
users=['joe@hawk.iit.edu']

def add_reservation(reserve_id, user_id, room_id, equipment_id, status, group_size, start_time, end_time):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    query = "insert into reservations values ({}, {}, {}, {}, '{}', {}, '{}', '{}', '{}')".format(reserve_id, user_id, room_id, equipment_id, status, group_size, current_time, start_time, end_time)
    cursor.execute(query)
    conn.commit()

def add_user(f_name, l_name, email, phone, password):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    query = "insert into users values ('{}', '{}', '{}', '{}', '{}')".format(f_name, l_name, email, phone, password)
    cursor.execute(query)
    conn.commit()

def get_user(email):
    query = f"select password from users where email='{email}';"
    print(f"select password from users where email='{email}';")
    cursor.execute(query)
    password = cursor.fetchone()
    if(password == None):
        return None
    return password[0]

@app.before_request
def before_request():
    if 'username' in session:
        g.user = session['username']
    else:
        g.user = None
   
    # query = ''
    # cursor.execute(query)
    # conn.commit()
    # result_users = cursor.fetchall()
    
    # users_logged_in = [usr for usr in result_users if usr[1] == session['email']]
    # if users_logged_in:
    #      logged_in_user = users_logged_in[0]
    #      g.user = User(logged_in_user[0], logged_in_user[1], logged_in_user[2], logged_in_user[3], logged_in_user[5], logged_in_user[4])

# @app.teardown_request
# def after_request(error=None):
#     conn.close()
#     if error:
#          print(str(error))


@app.route('/')
def home():

    return render_template('mainpage.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        db_password = get_user(username)

        if session.get('timeout'):
            timestart = session['timeout']
            timenow = time.time()
            if((timenow - timestart) < 300):
                flash(("You are locked out for " + str(int((300 - (timenow - timestart))/60)) +  " minutes."))
                return redirect(url_for('login'))

        if not session.get('attempts'):
            session['attempts'] = 0
        elif session['attempts'] >= 10:
            session['attempts'] = 0
            session['timeout'] = time.time()
            flash("TOO MANY ATTEMPTS, you are now locked out for 5 minutes.")
            return redirect(url_for('login'))

        if db_password is None:
            session['attempts'] += 1
            flash("Invalid username")
            return redirect(url_for('login'))
        elif password != db_password:
            session['attempts'] += 1
            flash("Invalid password")
            return redirect(url_for('login'))
        session['username'] = username
        flash("You have been logged in!")
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/log-out')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/create-account', methods=['POST'])
def create_account():
    if request.method == 'POST':
        uni = request.form.get('University')
        uni_id = request.form.get('University ID')
        email = request.form.get('email')
        f_name = request.form.get('First Name')
        l_name = request.form.get('Last Name')
        password = request.form.get('password')
        password_2 = request.form.get('re-enter password')
        phone = request.form.get('Phone number')

        add_user(f_name, l_name, email, phone, password)
        
        flash("Account created! Please log in!")
        return redirect(url_for('login'))
    return render_template('createAccount.html')

@app.route('/rooms', methods=['POST', 'GET'])
def rooms():
    session.clear()
    if not g.user:
        flash("You must login first")
        return redirect(url_for('login'))
    return render_template('rooms.html')

@app.route('/room_info.html', methods=['POST', 'GET'])
def room():
    if not g.user:
        flash("You must login first")
        return redirect(url_for('login'))
    return render_template('room_info.html')

@app.route('/confirmation.html', methods=['POST', 'GET'])
def confirm():
    if not g.user:
        flash("You must login first")
        return redirect(url_for('login'))
    if request.method == 'POST':
        size = request.form.get("groupsize")
        time = request.form.get("time")

        if size == '' and time == '':
            flash("Cannot leave 'Group Size' and 'Time' blank")
            return redirect(url_for('room'))
        elif size == '':
            flash("Cannot leave 'Group Size' blank")
            return redirect(url_for('room'))
        elif time == '':
            flash("Cannot leave 'Time' blank")
            return redirect(url_for('room'))


        time = time.split("-")
        start = time[0]
        end = time[1]
        add_reservation(3, 3, 3, 3, 'reserved', int(size), start, end)
    return render_template('confirmation.html')    

if __name__ == "__main__":
    app.static_folder='static'
    app.run(debug=True)
