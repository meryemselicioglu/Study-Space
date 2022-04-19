from datetime import datetime
import time
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from flask_jsglue import JSGlue
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
jsglue = JSGlue(app)
app.secret_key = 'gpd'
db = DBConnection('studyspacesboss', 'IPRO497gpd!!', 'studyspacesdbserver.postgres.database.azure.com', 5432, 'postgres')
conn = db.connect()
cursor = conn.cursor()
conn.autocommit = True

def add_reservation(user_id, room_id, group_size, start_time, end_time):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    query = "insert into reservations (user_id, room_id, group_size, reserve_time, start_time, end_time) values ({}, {}, {}, '{}', '{}', '{}')".format(user_id, room_id, group_size, current_time, start_time, end_time)
    cursor.execute(query)

def add_user(f_name, l_name, email, phone, password, uni):
    query = "insert into users (first_name, last_name, email, phone_no, password, isadmin, university) values ('{}', '{}', '{}', '{}', '{}', 'False', '{}')".format(f_name, l_name, email, phone, password, uni)
    cursor.execute(query)

def add_room(address, no_of_people, isAvailable, start, end, building, name, equipment):
    query = "insert into rooms (address, no_of_people, isavailable, start_time, end_time, building_name, name, equipment) values ('{}', {}, '{}', '{}', '{}', '{}', '{}', ARRAY {})".format(address, no_of_people, isAvailable, start, end, building, name, equipment)
    cursor.execute(query)

def get_rooms():
    query = "select * from rooms"
    cursor.execute(query)

    return cursor.fetchall()

def get_room(fullroom):
    query = "select * from rooms where building_name || ' ' || name = '{}'".format(fullroom)
    cursor.execute(query)

    return cursor.fetchall()

def get_room_name(roomid):
    query = "select building_name, name from rooms where room_id = '{}'".format(roomid)
    cursor.execute(query)
    temp = cursor.fetchone()
    return temp[0] + ' ' + temp[1]

def update_room(address, no_of_people, isAvailable, start, end, building, name, equipment, fullroom):
    query = "update rooms set address = '{}', no_of_people = {}, isavailable = '{}', start_time = '{}', end_time = '{}', building_name = '{}', name = '{}', equipment = ARRAY {} where building_name || ' ' || name = '{}'".format(address, no_of_people, isAvailable, start, end, building, name, equipment, fullroom)
    cursor.execute(query)

def delete_room(fullroom):
    query = "delete from rooms where building_name || ' ' || name = '{}'".format(fullroom)
    cursor.execute(query)

def get_users():
    query = "select * from users"
    cursor.execute(query)

    return cursor.fetchall()

def get_user(email):
    query = "select password from users where email='{}'".format(email)
    cursor.execute(query)
    password = cursor.fetchone()
    if(password == None):
        return None
    return password[0]

def get_user_name(email):
    query = "select first_name, last_name from users where email = '{}'".format(email)
    cursor.execute(query)

    return cursor.fetchone()

def get_email(userid):
    query = "select email from users where user_id = {}".format(userid)
    cursor.execute(query)
    return cursor.fetchone()[0]

def set_admin(user):
    query = "update users set isadmin = true where email = '{}'".format(user)
    cursor.execute(query)

def remove_admin(user):
    query = "update users set isadmin = false where email = '{}'".format(user)
    cursor.execute(query)

def is_admin(username):
    query = "select isadmin from users where email = '{}'".format(username)
    cursor.execute(query)
    return cursor.fetchone()[0]

def get_name(username):
    query = "select first_name, last_name from users where email = '{}'".format(username)
    cursor.execute(query)
    names = cursor.fetchone()
    return  names[0] + ' ' + names[1]

def get_room_id(fullroom):
    query = "select room_id from rooms where building_name || ' ' || name = '{}'".format(fullroom)
    cursor.execute(query)
    return  cursor.fetchone()[0]

def get_user_id(user):
    query = "select user_id from users where email = '{}'".format(user)
    cursor.execute(query)
    return  cursor.fetchone()[0]

def get_buildings():
    query = "select distinct building_name from rooms"
    cursor.execute(query)
    return  cursor.fetchall()

def get_equipment(roomid):
    query = "select equipment from rooms where room_id = {}".format(roomid)
    cursor.execute(query)
    return  cursor.fetchone()[0]

def get_reservations_room(fullroom):
    rmid = get_room_id(fullroom)
    query = "select * from reservations where room_id = {}".format(rmid)
    cursor.execute(query)
    return  cursor.fetchall()

def get_reservations_user(user):
    usrid = get_user_id(user)
    query = "select * from reservations where user_id = {}".format(usrid)
    cursor.execute(query)
    return  cursor.fetchall()

@app.before_request
def before_request():
    if 'username' in session:
        g.user = session['username']
    else:
        g.user = None

@app.route('/')
def home():

    return render_template('mainpage.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    admin = False
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
        elif not check_password_hash(db_password, password):
            session['attempts'] += 1
            flash("Invalid password")
            return redirect(url_for('login'))

        session['username'] = username
        session['fullname'] = get_name(username)
        flash("You have been logged in!")

        if is_admin(username):
            admin = True
        return redirect(url_for('home', admin=str(admin)))
    return render_template('login.html')

@app.route('/log-out')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/create-account', methods=['POST','GET'])
def create_account():
    if request.method == 'POST':
        uni = request.form.get('University')
        email = request.form.get('email')
        f_name = request.form.get('First Name')
        l_name = request.form.get('Last Name')
        password = request.form.get('password')
        password_2 = request.form.get('re-enter password')
        phone = request.form.get('Phone number')

        if password != password_2:
            flash("not same password")
            return redirect(url_for('create_account'))
        if len(password) < 6:
            flash("password must be at least 6 characters")
            return redirect(url_for('create_account'))
        if "password" in password or "12345678" in password or "qwerty" in password:
            flash("password too common")
            return redirect(url_for('create_account'))
        if uni in password or f_name in password or l_name in password or phone in password:
            flash("password too personal")
            return redirect(url_for('create_account'))

        email_split = email.split('@')

        if len(email_split) != 2:
            flash("bad email format")
            return redirect(url_for('create_account'))
        if get_user(email):
            flash("email alaready exists")
            return redirect(url_for('create_account'))
        elif email_split[1][-3:] != "com" and email_split[1][-3:] != "net" and email_split[1][-3:] != "gov" and email_split[1][-3:] != "edu":
            flash("bad email domain" + " (" + email_split[1] + ")")
            return redirect(url_for('create_account'))
        elif len(phone) != 10:
            flash("bad phone number (no parentheses, dashes, or spaces)")
            return redirect(url_for('create_account'))

        add_user(f_name, l_name, email, phone, generate_password_hash(password), uni)
        
        flash("Account created! Please log in!")
        return redirect(url_for('login'))
    return render_template('createAccount.html')

@app.route('/rooms', methods=['POST', 'GET'])
def rooms():
    if not g.user:
        flash("You must login first")
        return redirect(url_for('login'))

    rooms = get_rooms()
    buildings = get_buildings()

    buildingsNew = []
    for building in buildings:
        for room in rooms:
            if room[3] == True and building[0] == room[6]:
                buildingsNew.append(building)
                break

    return render_template('rooms.html', buildings=buildingsNew, rooms=rooms)

@app.route('/room_info', methods=['POST', 'GET'])
def room():
    if not g.user:
        flash("You must login first")
        return redirect(url_for('login'))
    
    room = request.args.get("room")
    fullroom = room.replace("%20", " ")
    roomid = get_room_id(fullroom)

    if request.method == 'POST':
        size = request.form.get("groupsize")
        start = request.form.get("start")
        end = request.form.get("end")
        userid = get_user_id(g.user)

        add_reservation(userid, roomid, int(size), start, end)
        return redirect(url_for('confirm'))

    equipment = get_equipment(roomid)
    return render_template('room_info.html', equipment=equipment)

@app.route('/confirmation', methods=['POST', 'GET'])
def confirm():
    if not g.user:
        flash("You must login first")
        return redirect(url_for('login'))
        
    return render_template('confirmation.html')    

@app.route('/adminpages')
def adminpages():
    if not g.user:
        flash("You must login first")
        return redirect(url_for('login'))
    if not is_admin(g.user):
        flash("You are not an administrator")
        return redirect(url_for('home'))

    return render_template("adminpages.html")
    
@app.route('/adminrooms')
def adminrooms():
    if not g.user:
        flash("You must login first")
        return redirect(url_for('login'))
    if not is_admin(g.user):
        flash("You are not an administrator")
        return redirect(url_for('home'))

    rooms = get_rooms()
    return render_template('adminrooms.html', rooms=rooms)

@app.route('/adminusers', methods=['POST', 'GET'])
def adminusers():
    if not g.user:
        flash("You must login first")
        return redirect(url_for('login'))
    if not is_admin(g.user):
        flash("You are not an administrator")
        return redirect(url_for('home'))

    if request.args.get("set"):
        set_admin(request.args.get("set"))
        flash(request.args.get("set")+" is now an admin")
    elif request.args.get("remove"):
        remove_admin(request.args.get("remove"))
        flash(request.args.get("remove")+" was removed as an admin")

    users = get_users()
    admins = []
    for user in users:
        if is_admin(user[3]):
            admins.append(user)
    return render_template('adminusers.html', users=users, admins=admins)

@app.route('/createroom', methods=['POST', 'GET'])
def createroom():
    if not g.user:
        flash("You must login first")
        return redirect(url_for('login'))
    if not is_admin(g.user):
        flash("You are not an administrator")
        return redirect(url_for('home'))

    if request.method == 'POST':
        roomName = request.form.get('Room Name')
        buildingName = request.form.get('Building Name')
        buildingAddress = request.form.get('Building Address')
        maxNoPpl = request.form.get('Capacity')
        availabilty = request.form.get('available')
        start = request.form.get('Start-Time')
        end = request.form.get('End-Time')
        equipment = request.form.getlist('Equipment[]')

        if 'none' in equipment and len(equipment) > 1:
            equipment.remove('none')

        add_room(buildingAddress, maxNoPpl, 'True' if availabilty == 'yes' else 'False', start, end, buildingName, roomName, equipment)
        flash('Room Created!')
        return redirect(url_for('adminrooms'))
    return render_template('adminCreateRoom.html')

@app.route('/editroom', methods=['POST', 'GET'])
def editroom():
    if not g.user:
        flash("You must login first")
        return redirect(url_for('login'))
    if not is_admin(g.user):
        flash("You are not an administrator")
        return redirect(url_for('home'))

    if request.method == 'POST':
        if request.args:
            roomname = request.args.get("room")
            fullroom = roomname.replace("%20", " ")

        roomName = request.form.get('Room Name')
        buildingName = request.form.get('Building Name')
        buildingAddress = request.form.get('Building Address')
        maxNoPpl = request.form.get('Capacity')
        availabilty = request.form.get('available')
        start = request.form.get('Start-Time')
        end = request.form.get('End-Time')
        equipment = request.form.getlist('Equipment[]')

        if 'none' in equipment and len(equipment) > 1:
            equipment.remove('none')

        update_room(buildingAddress, maxNoPpl, 'True' if availabilty == 'yes' else 'False', start, end, buildingName, roomName, equipment, fullroom)
        flash('Room Updated!')
        return redirect(url_for('adminrooms'))

    if request.args:
        roomname = request.args.get("room")
        fullroom = roomname.replace("%20", " ")
        room = get_room(fullroom)
        room = room[0]
        avail = "Yes" if room[3] == True else "No"
    else:
        flash("System Error")
        return redirect(url_for('adminrooms'))

    return render_template('adminCreateRoom.html', building=room[6], number=room[7], address=room[1], capacity=room[2], availability=avail, starttime=room[4], endtime=room[5], equipment=room[8])

@app.route('/adminrooms1')
def deleteroom():
    if not g.user:
        flash("You must login first")
        return redirect(url_for('login'))
    if not is_admin(g.user):
        flash("You are not an administrator")
        return redirect(url_for('home'))

    if request.args:
        roomname = request.args.get("room")
        fullroom = roomname.replace("%20", " ")
        delete_room(fullroom)
        flash(fullroom + " was deleted")
        return redirect(url_for('adminrooms'))
    else:
        flash("System Error")
        return redirect(url_for('adminrooms'))

@app.route('/roomreservations')
def roomreservations():
    if not g.user:
        flash("You must login first")
        return redirect(url_for('login'))
    if not is_admin(g.user):
        flash("You are not an administrator")
        return redirect(url_for('home'))

    if request.args:
        roomname = request.args.get("room")
        fullroom = roomname.replace("%20", " ")
        reservations = get_reservations_room(fullroom)
        if reservations:
            reservations = [list(reservation) for reservation in reservations]
            for reservation in reservations:
                reservation.append(get_email(reservation[1]))
            print(reservations)
        return render_template('roomreservations.html', reservations=reservations, room=fullroom)
    else:
        flash("System Error")
        return redirect(url_for('adminrooms'))

@app.route('/userreservations')
def userreservations():
    if not g.user:
        flash("You must login first")
        return redirect(url_for('login'))
    if not is_admin(g.user):
        flash("You are not an administrator")
        return redirect(url_for('home'))

    if request.args:
        user = request.args.get("user")
        reservations = get_reservations_user(user)
        fulluser = get_user_name(user)
        fulluser = fulluser[0] + ' ' + fulluser[1]
        if reservations:
            reservations = [list(reservation) for reservation in reservations]
            for reservation in reservations:
                reservation.append(get_room_name(reservation[2]))
            print(reservations)
        return render_template('roomreservations.html', reservations=reservations, user=fulluser, room="temp")
    else:
        flash("System Error")
        return redirect(url_for('adminrooms'))

if __name__ == "__main__":
    app.static_folder='static'
    app.run(debug=True)
