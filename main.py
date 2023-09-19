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
def get_current_user():
    if 'logged_in' in session and 'id' in session:
        current_user_id = session['id']
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (current_user_id,))
                user = cursor.fetchone()
                return user
    else:
        return None
    
def get_userpw_by_email(email):
    if 'logged_in' in session:
        return
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
            password = cursor.fetchone()
            return password
    
def is_admin():
    user = get_current_user()   # getting the current user data
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
        
def get_user_posts(id):
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM posts JOIN users ON posts.user_id = users.id WHERE id = %s", (id,))
            userposts = cursor.fetchall()
            return userposts

def get_post_byid(id):
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM posts JOIN users ON posts.user_id = users.id WHERE post_id = %s", (id,))
            post = cursor.fetchone()
            return post


def get_public_details():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            sql = """SELECT 
            username, acc_creation, pro_game, ingame_rank, esport_team, esport_org, profile_pic
            FROM users WHERE id = %s"""
            values = (request.args['id'])
            cursor.execute(sql, values)
            result = cursor.fetchone()
            return result
        

# Likes handling
@app.route('/like_handling', methods = ['POST', 'GET'])
def like_handling():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            sql = """SELECT * FROM likes
            WHERE post_id = %s AND user_id = %s"""
            values = (
                request.form['post_id'],
                get_current_user()['id']
            )
            cursor.execute(sql, values)
            result = cursor.fetchall()
            if result:
                return redirect('/unlike?post_id='+request.form['post_id'])
            
            return redirect('/like?post_id='+request.form['post_id'])

@app.route('/like')
def like():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            sql = """INSERT INTO likes
            (post_id, user_id)
            VALUES (%s, %s)"""
            values = (
                request.args['post_id'],
                get_current_user()['id']
            )
            cursor.execute(sql, values)
            connection.commit()
            return redirect('/update_likes?post_id='+request.args['post_id'])

@app.route('/unlike')   
def unlike():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            sql = """DELETE FROM likes
            WHERE post_id = %s AND user_id = %s"""
            values = (
                request.args['post_id'],
                get_current_user()['id']
            )
            cursor.execute(sql, values)
            connection.commit()
            return redirect('/update_likes?post_id='+request.args['post_id'])
        
@app.route('/update_likes')
def update_likes():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            sql_select = """SELECT post_id, likes FROM post_likes_view WHERE post_id = %s"""
            values = (int(request.args['post_id']),)
            cursor.execute(sql_select, values)
            row = cursor.fetchone()

            if row:
                sql_update = """UPDATE posts SET likes = %s WHERE post_id = %s"""
                update_values = (
                    row['likes'], 
                    row['post_id']
                    )
                cursor.execute(sql_update, update_values)
                connection.commit()
                # Redirect back to the previous page
                referer = request.headers.get('Referer')
                return redirect(referer)
            else:
                # Redirect back to the previous page
                referer = request.headers.get('Referer')
                return redirect(referer)




@app.template_filter('format_datetime')
def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    return value.strftime(format)


@app.route('/', methods = ['POST', 'GET'] )
def main_page():
    if 'logged_in' in session:
        if request.method == 'POST':
            with create_connection() as connection:
                with connection.cursor() as cursor:
                    sql = "INSERT INTO posts (user_id, content, post_time, likes) VALUES (%s, %s, %s, %s)"
                    values = (
                        session['id'],
                        request.form["content"],
                        datetime.now(),
                        int(0)
                    )
                    cursor.execute(sql, values)
                    result = connection.commit()
                    return redirect('/')
                    
        else:
            result = get_current_user()
            return render_template('home_page.html', result = result, allposts = getall_posts(), allusers = getall_users())
                
    else:
        return render_template('home_page.html')
    


@app.route('/signup', methods = ['POST', 'GET'] )
def signup():
    if 'logged_in' in session:
        return redirect('/')
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
            flash('Insecure Password! (ex: Aa3)')
            return redirect('/signup')  
          
    else:
        return render_template('signup.html')

@app.route('/login', methods = ["POST", "GET"])
def login():
    if 'logged_in' in session:
        return redirect('/')
    session['activity'] = ''
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

# FORGET PASSWORD AUTHENTICATION
@app.route('/req_forget_password', methods = ["POST", "GET"])
def req_forget_password():
    if 'logged_in' in session:
        return redirect('/')
    return render_template('req_forget_password.html')

@app.route('/forget_password_send_email', methods = ["POST", "GET"])
def send_email():
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
                # send confirmation email
                return redirect('/ver_forget_password?email='+request.form['email'])
            else:
                flash('email not found!')
                return redirect('/req_forget_password')

@app.route('/ver_forget_password', methods = ["POST", "GET"])
def ver_forget_password():
    if 'logged_in' in session:
        return redirect('/')
    else:
        if request.method == "POST" and request.form['ver_code'] == '12345':
            session['activity'] = 'resetting password'
            return redirect('/forget_password?email='+request.args['email'])

        else:
            return render_template('ver_forget_password.html')

@app.route('/forget_password', methods = ["POST", "GET"])
def forgot_password():
    if 'logged_in' in session:
        return redirect('/')
    if request.method == 'POST' and 'resetting password' in session['activity']:
        with create_connection() as connection:
            with connection.cursor() as cursor:
                if request.form['new_password'] == request.form['new_conf_password']:
                    if secure_password(request.form['new_password']):
                        sql = """UPDATE users SET password = %s 
                        WHERE email = %s"""
                        values = (request.form['new_password'], request.args['email'])
                        cursor.execute(sql, values)
                        connection.commit()
                        return redirect('/')
                    else:
                        flash('Insecure Password!')
                        return redirect('/forget_password?email='+request.args['email'])
                flash('Passwords not matching!')
                return redirect('/forget_password?email='+request.args['email'])
    elif 'resetting password' in session['activity']:
        return render_template('forget_password.html')
    else:
        return redirect('/')


@app.route('/contact', methods = ["GET", "POST"] )
def contact():
    if 'logged_in' in session:
        result = get_current_user()
        return render_template('/contact.html', result=result)
    else:
        return render_template('/contact.html')

@app.route('/settings', methods = ["POST", "GET"])
def settings():
    if 'logged_in' in session:
        result = get_current_user()
        return render_template('/settings.html', result=result)
    else:
        return redirect('/')
    
# SETTINGS FORM ACTIONS
@app.route('/update_personal_information', methods = ["GET", "POST"])
def update_personal_information():
    if request.form['fname'] and request.form['lname'] and request.form['email'] and request.form['phonenumber']:
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
        return redirect('/settings')

@app.route('/update_password', methods = ["GET", "POST"])
def update_security():
    if request.form['new_password'] and secure_password(request.form['new_password']):
        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = """UPDATE users SET
                password = %s
                WHERE id = %s
                """
                values = (
                    hash_password(request.form['new_password']),
                    session['id']
                )
                cursor.execute(sql, values)
                connection.commit()
                return redirect('/')
    else:
        return redirect('/settings')

@app.route('/update_appearance')
def update_appearance():
    return redirect('/')

@app.route('/update_language')
def update_language():
    return redirect('/')

@app.route('/update_post', methods = ["GET", "POST"])
def update_post():
    if 'logged_in' in session:
        result = get_current_user()
        post_id = request.form['post_id']
        post_user_id = request.form['user_id']
        if int(result['id']) == int(post_user_id):
            try:
                with create_connection() as connection:
                    with connection.cursor() as cursor:
                        sql = """UPDATE posts SET content = %s 
                        WHERE post_id = %s"""
                        values = (
                            request.form['content'],
                            post_id
                        )
                        
                        cursor.execute(sql, values)
                        connection.commit()
                        return redirect('/')
                    
            except:
                return render_template('update_post.html', post=get_post_byid(post_id), result=get_current_user())

@app.route('/delete_post', methods = ["GET", "POST"])
def delete_post():
    if 'logged_in' in session:
        result = get_current_user()
        post_user_id = request.form['user_id']
        if int(result['id']) == int(post_user_id):
            with create_connection() as connection:
                with connection.cursor() as cursor:
                    sql = """DELETE FROM posts WHERE user_id = %s 
                    AND post_id = %s"""
                    values = (
                        request.form['user_id'],
                        request.form['post_id']
                    )
                    cursor.execute(sql, values)
                    connection.commit()
                    return redirect('/')

        return redirect('/')

@app.route('/post_view')
def post_view():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM posts WHERE post_id = %s", (request.args['post_id']))
            result = cursor.fetchone()
        if 'logged_in' in session and result:
            post = get_post_byid(request.args['post_id'])
            return render_template('post_view.html', result=get_current_user(), post=post)
        else:
            return redirect('/')

@app.route('/profile')
def account_details():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE id = %s", (request.args['id']))
            result = cursor.fetchone()
    if 'logged_in' in session and result:
        userposts = get_user_posts(request.args['id'])
        if userposts:
            userposts = reversed(userposts)
        return render_template('/profile.html', result=get_current_user(), viewuser=get_public_details(), userposts=userposts)
    else:
        return redirect('/')


@app.route('/edit_profile', methods = ["POST", "GET"])
def edit_profile():
    if 'logged_in' in session and int(request.args['id']) == int(session['id']):
        if request.method == "POST":
            with create_connection() as connection:
                with connection.cursor() as cursor:
                    sql = """UPDATE users SET
                    username = %s,
                    pro_game = %s,
                    ingame_rank = %s,
                    esport_team = %s,
                    esport_org = %s
                    WHERE id = %s
                    """
                    values = (
                        request.form['username'],
                        request.form['pro_game'],
                        request.form['ingame_rank'],
                        request.form['esport_team'],
                        request.form['esport_org'],
                        session['id']
                    )
                    cursor.execute(sql, values)
                    connection.commit()
            return redirect('/')

        else:
            result = get_current_user()
            public_details = get_public_details()
            return render_template('/edit_profile.html', result=result, public_details=public_details)
    else:
        return redirect('/')
    

@app.route('/admin_panel')
def admin_panel():
    if is_admin():
        allusers = getall_users()
        result = get_current_user()
        return render_template('/admin_panel.html', result=result, allusers=allusers)
    else:
        return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)