from flask import Flask, render_template, request, redirect, session, flash
from datetime import datetime, date, timedelta
import pymysql
import bcrypt
import re

app = Flask(__name__)
app.secret_key = '!SeCrEt__KeY.mERLIN13542!'

DEFAULTIMG = 'static/images/style-images/avatar.png'



def create_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="MER!13062006Iby.nz!LIN",
        db="users",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

# Default profile Image
def set_default_profilepic():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            sql = "UPDATE users SET profile_pic = %s WHERE email = %s"
            values = (
                DEFAULTIMG,
                request.form["email"]
            )
            cursor.execute(sql, values)
            connection.commit()
            return

# Password Security      
def hash_password(password):
    salt = bcrypt.gensalt(rounds=12)

    # Hash the password using the salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    # Return the hashed password as a utf-8 encoded string
    return hashed_password.decode('utf-8')
        
def verify_password(try_password, hashed_password):
    # Verify if the provided password matches the hashed password
    return bcrypt.checkpw(try_password.encode('utf-8'), hashed_password.encode('utf-8'))



# Signup Checks
def is_phone_number(input_string):
    # Remove spaces and non-digit characters from the input string
    input_string = input_string.replace(" ", "").replace("-", "")

    # Check if the modified string starts with a plus sign and has at least 9 digits
    if input_string.startswith("+") and len(input_string) >= 10:
        return True
    else:
        return False
    
def email_already_exists(email):
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()
            return result is not None
        
def is_valid_age(birthday):
    # Do not need to check if Date is valid, because 10 years old is 
    # always a valid date and 80 years ago is also always a valid date, 
    # rest is done automatically
    try:
        birth_date = datetime.strptime(birthday, '%Y-%m-%d').date()
        today = date.today()
        max_age = today - timedelta(days=80*365)  # max 80 years old
        min_age = today - timedelta(days=10*365)  # At least 10 years old
        return max_age <= birth_date <= min_age
    except ValueError:
        return False
        
def secure_password(password):
    lower_case = re.search('[a-z]', password)
    upper_case = re.search('[A-Z]', password)
    number = re.search('[0-9]', password)

    if lower_case and upper_case and number:
        return True
    else:
        return False
    


# USER AUTHENTICATION & DATA
def current_user():
    if 'logged_in' in session and 'id' in session:
        current_user_id = session['id']
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (current_user_id,))
                user = cursor.fetchone()
                return user
    else:
        return None
    
def is_admin():
    user = current_user()   # getting the current user data
    if user and 'role' in session and user['role'] == 'Admin' and 'Admin' in session['role']:
        return True
    else:
        return False
    
def getall_users():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            result = cursor.fetchall()
            return result

def getall_posts():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM posts JOIN users ON posts.user_id = users.id")
            allposts = cursor.fetchall()
            allposts = reversed(allposts)
            return allposts
    
def get_public_details():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            sql = """SELECT 
            username, acc_creation, pro_game, esport_team, esport_org, profile_pic
            FROM users WHERE id = %s"""
            values = (request.args['id'])
            cursor.execute(sql, values)
            result = cursor.fetchone()
            return result



@app.template_filter('format_datetime')
def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    return value.strftime(format)


@app.route('/', methods = ['POST', 'GET'] )
def main_page():
    if 'logged_in' in session:
        if request.method == 'POST':
            with create_connection() as connection:
                with connection.cursor() as cursor:
                    sql = "INSERT INTO posts (user_id, content, post_time) VALUES (%s, %s, %s)"
                    values = (
                        session['id'],
                        request.form["content"],
                        datetime.now()
                    )
                    cursor.execute(sql, values)
                    result = connection.commit()
                    return redirect('/')
                    
        else:
            result = current_user()
            allposts = getall_posts()
            allusers = getall_users()
            return render_template('home_page.html', result=result ,allposts=allposts, allusers=allusers)
                
    else:
        return render_template('home_page.html')
    


@app.route('/signup', methods = ['POST', 'GET'] )
def signup():
    if request.method == 'POST':
        if email_already_exists(request.form['email']):
            flash('Email already in use!')
            return redirect('/signup') 
        if secure_password(request.form['password']):
            if is_valid_age(request.form['birthday']):
                with create_connection() as connection:
                    with connection.cursor() as cursor:
                        sql = """INSERT INTO users
                            (fname, lname, email, password, birthday, acc_creation)
                            VALUES (%s, %s, %s, %s, %s, %s) """
                        values = (
                            request.form["fname"],
                            request.form["lname"],
                            request.form["email"],
                            hash_password(request.form["password"]),
                            request.form["birthday"],
                            date.today()
                        )

                        if request.form["password"] == request.form["conf_password"]:
                            cursor.execute(sql, values)
                            connection.commit()
                            set_default_profilepic()   #set default profile picture
                            return redirect('/')
                        else:
                            flash('Passwords not matching!')
                            return redirect('/signup') 
            else:
                flash('Too young or too old!')
                return redirect('/signup')   
        else:
            flash('Insecure Password!')
            return redirect('/signup')  
          
    else:
        return render_template('signup.html')

@app.route('/login', methods = ["POST", "GET"])
def login():
    if request.method == "POST":
        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = """ SELECT * FROM users WHERE 
                email = %s """
                values = (
                    request.form["email"]
                )
                cursor.execute(sql, values)
                result = cursor.fetchone()

                if result:
                    stored_password = result['password']

                    if verify_password(request.form['password'], stored_password):
                        session['logged_in'] = True
                        session['id'] = result['id']
                        session['email'] = result['email']
                        session['fname'] = result['fname']
                        session['lname'] = result['lname']
                        session['birthday'] = result['birthday']
                        session['role'] = result['role']
                        return redirect('/')
                
                flash('Incorrect login information!')
        return redirect('/login')
    else:
        return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')

@app.route('/forgot_password')
def forgot_password():
    if 'logged_in' in session:
        return redirect('/')
    if request.method == 'POST':
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute('UPDATE users SET password = %s WHERE email = %s', (request.form['password'], request.form['email']) )
                connection.commit()
                return redirect('/login')
    else:
        return render_template('forgot_password.html')


@app.route('/contact')
def contact():
    if 'logged_in' in session:
        result = current_user()
        return render_template('/contact.html', result=result)
    else:
        return render_template('/contact.html')


@app.route('/settings', methods = ["POST", "GET"])
def settings():
    if 'logged_in' in session:
        if request.method == 'POST':
            with create_connection() as connection:
                with connection.cursor() as cursor:

                    if is_phone_number(request.form['phonenumber']):
                        sql = """UPDATE users SET
                        fname = %s,
                        lname = %s,
                        email = %s,
                        phonenumber = %s
                        WHERE id = %s
                        """
                        values = (
                            request.form['fname'],
                            request.form['lname'],
                            request.form['email'],
                            request.form['phonenumber'],
                            session['id']
                        )
                        cursor.execute(sql, values)
                        connection.commit()
                        return redirect('/')
                    else:
                        return redirect('/settings')
        else:
            result = current_user()
            return render_template('/settings.html', result=result)
        
    else:
        return redirect('/')


@app.route('/profile')
def account_details():
    if 'logged_in' in session:
        result = get_public_details()
        
        return render_template('/profile.html', result=result)
    

    else:
        return redirect('/')


@app.route('/edit_profile', methods = ["POST", "GET"])
def edit_profile():
    if 'logged_in' in session:
        if request.method == "POST":
            with create_connection() as connection:
                with connection.cursor() as cursor:
                    sql = """UPDATE users SET
                    fname = %s,
                    lname = %s,
                    password = %s,
                    email = %s,
                    username = %s,
                    birthday = %s
                    WHERE id = %s
                    """
                    values = (
                        request.form['fname'],
                        request.form['lname'],
                        request.form['password'],
                        request.form['email'],
                        request.form['username'],
                        request.form['birthday'],
                        session['id']
                    )
                    cursor.execute(sql, values)
                    connection.commit()
            return redirect('/')

        else:
            result = current_user()
            return render_template('/edit_profile.html', result=result)
    else:
        return redirect('/')
    

@app.route('/admin_panel')
def admin_panel():
    if is_admin():
        allusers = getall_users()
        result = current_user()
        return render_template('/admin_panel.html', result=result, allusers=allusers)
    else:
        return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)