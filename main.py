from flask import Flask, render_template, request, redirect, session, flash
import pymysql
import datetime
import os
import uuid
import datetime

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

def getall_users():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users"
            cursor.execute(sql)
            result = cursor.fetchall()
    return result

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
                        datetime.datetime.now()
                    )
                    cursor.execute(sql, values)
                    result = connection.commit()
                    return redirect('/')
                    
        else:
            with create_connection() as connection:
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM users WHERE id = %s" 
                    values = ( 
                        session['id']
                    )
                    cursor.execute(sql, values)
                    result = cursor.fetchone()

                with connection.cursor() as cursor:
                    sql = "SELECT * FROM posts JOIN users ON posts.user_id = users.id"
                    cursor.execute(sql)
                    allposts = cursor.fetchall()

                allusers = getall_users()
                return render_template('home_page.html', result=result ,allposts=allposts, allusers=allusers)
                
    else:
        return render_template('home_page.html')
    
@app.template_filter('format_datetime')
def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    return value.strftime(format)


@app.route('/signup', methods = ['POST', 'GET'] )
def signup():
    if request.method == 'POST':
        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = """INSERT INTO users
                    (fname, lname, email, password, birthday, acc_creation)
                    VALUES (%s, %s, %s, %s, %s, %s) """
                values = (
                    request.form["fname"],
                    request.form["lname"],
                    request.form["email"],
                    request.form["password"],
                    request.form["birthday"],
                    datetime.date.today()
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
        return render_template('signup.html')

@app.route('/login', methods = ["POST", "GET"])
def login():
    if request.method == "POST":
        with create_connection() as connection:
            with connection.cursor() as cursor:

                sql = """ SELECT * FROM users WHERE 
                email = %s AND password = %s """
                values = (
                    request.form["email"],
                    request.form["password"]
                )
                cursor.execute(sql, values)
                result = cursor.fetchone()
        if result:
            session['logged_in'] = True
            session['id'] = result['id']
            session['password'] = result['password']
            session['email'] = result['email']
            session['fname'] = result['fname']
            session['lname'] = result['lname']
            session['birthday'] = result['birthday']
            session['role'] = result['role'],
            session['profile_pic'] = result['profile_pic']
            
            return redirect('/')
        else:
            flash('Incorrect login information!')
            return redirect('/login')
    else:
        return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/settings', methods = ["POST", "GET"])
def settings():
    if request.method == 'POST':
        with create_connection() as connection:
            with connection.cursor() as cursor:
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
        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE id = %s"
                values = (
                    session['id']
                )
                cursor.execute(sql, values)
                result = cursor.fetchone()
        return render_template('/settings.html', result=result)



@app.route('/profile_self')
def account_details():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE id = %s"
            values = (
                request.args['id']
                )
            cursor.execute(sql, values)
            result = cursor.fetchone()
    return render_template('/profile_self.html', result=result)

@app.route('/edit_profile', methods = ["POST", "GET"])
def edit_profile():
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
        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE id = %s"
                values = (request.args['id'])
                cursor.execute(sql, values)
                result = cursor.fetchone()
        return render_template('/edit_profile.html', result=result)



if __name__ == "__main__":
    app.run(debug=True)

print('this is a test')