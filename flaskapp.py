# Created by Aditya

# Importing the needed modules
import os
from flask import Flask, session, redirect, url_for, render_template, request, flash
from markupsafe import Markup
from passlib.hash import sha256_crypt

# Creating an application using flask
app = Flask(__name__, static_folder='templates/static/', template_folder='templates/')
app.secret_key = 'WelcomeToTaskApp'

# Creating global variables
username = ""
user_file = ""
email = ""
user_mode = ""

# Opening the app
@app.route('/')
def welcome():
    return redirect(url_for('log_in_page'))

#Login page
@app.route('/log_in_page', methods=['POST','GET'])
def log_in_page():
    session.pop('username', None)
    session.pop('email', None)
    session.pop('password', None)
    # Function of the login button
    if request.method=='POST':
        if request.form['username']=="":
            flash('User name not entered')
            return render_template('log_in_page.html')
        if request.form['password']=="":
            flash('Password not entered')
            return render_template('log_in_page.html')
        flash('')
        filename="./users.txt"
        #Loginning in after checking the username and password
        if os.path.isfile(filename):
            #Comparing details of all users with the entered details
            with open(filename, "r") as fr:
                for line in fr.readlines():
                    if line.strip()=="":
                        continue
                    login_info = line.split('####')
                    if request.form['username']==login_info[0] and sha256_crypt.verify(request.form['password'],login_info[1]):
                        session['username']= request.form['username']
                        with open("users.txt","r") as fr:
                            lines = fr.readlines()
                            fr.close()
                        for line in lines:
                            user = line.split("####")
                            if user[0] == request.form["username"]:
                                session['email'] = user[2]
                                session['password'] = user[1]
                        # Calling global variables
                        global username
                        global user_file
                        global user_mode
                        global email
                        # Updating global variables
                        username = request.form['username']
                        user_file = username + "_tasks.txt"
                        user_mode = username + "_mode.txt"
                        with open(user_mode, "r") as fr:
                             session['mode'] = fr.readline()
                             fr.close()
                        with open("previous_user.txt", "w") as fo:
                            fo.write(username)
                            fo.close()
                        with open("users.txt", "r") as fr:
                            lines = fr.readlines()
                            fr.close()
                        for line in lines:
                            y = line.split("####")
                            if y[0] == username:
                                email = y[2]
                                break
                        # Moving to the main page
                        return redirect(url_for('tasks_page'))
                flash('Username or Password does not match')
                fr.close()
        else:
            flash('No user exist. Create at least one user')
    return render_template('log_in_page.html')

# security page
@app.route('/security_page', methods=['POST','GET'])
def security_page():
    session.pop('username', None)
    session.pop('email', None)
    session.pop('SQ', None)
    session.pop('AK', None)
    # Security check before forgot password page
    if request.method=='POST':
        if request.form['username']=="" and request.form['email']=="":
            flash('Please enter at least 1 User detail')
            return render_template('security.html')
        flash('')
        filename="./users.txt"
        # Checking the Answer Key
        if os.path.isfile(filename):
            # Calling global variables
            global username
            with open(filename, "r") as fr:
                for line in fr.readlines():
                    if line.strip()=="":
                        continue
                    login_info = line.split('####')
                    if request.form['username']==login_info[0] or request.form['email'] == login_info[2]:
                        session['username'] = login_info[0]
                        session['email'] = login_info[2]
                        session['SQ'] = login_info[3]
                        session['AK'] = login_info[4]
                        username = session['username']
                        return redirect(url_for('forgot_password_page'))
                fr.close()
        else:
            flash('No user exist. Create at least one user')
    return render_template('security.html')

# Main page
@app.route('/tasks_page')
def tasks_page():
    # Calling global variables
    global username
    filename= username+"_tasks.txt"
    html_string='<table border=1 style="width:100%;border:1px solid;"><th width="15%">Task</th><th width="75%">Description</th><th width="10%">Progress</th>'
    if os.path.isfile(filename):
        with open(filename, "r") as fr:
            for line in fr.readlines():
                if line.strip()=="":
                    continue
                line_info = line.split('####')
                html_string+='<tr><td width="25%">'+line_info[0]+'</td><td width="15%">'+line_info[1]+'</td><td width="10%">'+line_info[2]+'</td></tr>'
            html_string+='</table>'
            flash(Markup(html_string))
    return render_template('tasks_page.html')

# Forgot password page
@app.route('/forgot_password_page', methods=['POST','GET'])
def forgot_password_page():
    # calling global variables
    global username
    global user_file
    # Changing the Password
    if request.method=='POST':
        flash('')
        if request.form['password']=="" or request.form['con_password']=="":
            flash('Password not confirmed')
            return render_template('forgot_password.html')
        else:
            if request.form['password'] == request.form['con_password']:
                x = []
                with open("users.txt", "r") as fr:
                    lines = fr.readlines()
                    fr.close()
                for line in lines:
                    if line == "" or line == "\n":
                        continue
                    x.append(line)
                with open("users.txt", "w") as fo:
                    for i in range(len(x)):
                        y = x[i].split("####")
                        if y[0] == username:
                            fo.write("\n" + y[0]+ "####" + sha256_crypt.hash(request.form['password']) + "####" + y[2] + "####" +y[3] + "####" + y[4])
                            continue
                        fo.write(x[i])
                flash('Password changed successfully')
            else:
                flash('Passwords do not match')

    return render_template('forgot_password.html')

# settings page
@app.route('/settings_page', methods=['POST','GET'])
def settings_page():
    # calling global variables
    global username
    global user_mode
    global email
    with open(user_mode,'r') as fr:
        mode = fr.readline()
        fr.close()
    # Changing the theme, password and e-mail ID
    if request.method=='POST':
        session.pop('mode', None)
        flash('')
        if request.form['mode']== mode and (request.form['password']=="" and request.form['email']== email):
            flash('No settings have been changed')
            with open(user_mode,'r') as fr:
                session['mode'] = fr.readline()
                fr.close()
            return render_template('settings.html')
        elif request.form['mode']!= mode and (request.form['password']=="" and request.form['email']== email):
            with open(user_mode, "w") as fo:
                fo.write(request.form['mode'])
                session['mode'] = request.form['mode']
                fo.close()
        elif request.form['mode']== mode and (request.form['password']!="" or request.form['email']!= email):
            users = []
            with open('users.txt', "r") as fr:
                temp_users = fr.readlines()
                fr.close()
            for user in temp_users:
                x = user.split("####")
                if user == "":
                    continue
                users.append(user)
            if request.form['password'] != "" and request.form['email'] == email:
                with open('users.txt', "w") as fo:
                    for user in users:
                        current_user =  user.split("####")
                        if current_user[0] == username:
                            fo.write("\n" + current_user[0] + "####" + sha256_crypt.hash(request.form['password']) + "####" + current_user[2] + "####" + current_user[3] + "####" + current_user[4])
                        else:
                            fo.write(user)
                    fo.close()
            elif request.form['password'] == "" and request.form['email'] != email:
                with open('users.txt', "w") as fo:
                    for user in users:
                        current_user =  user.split("####")
                        if current_user[0] == username:
                            fo.write("\n" + current_user[0] + "####" + current_user[1] + "####" + request.form['email'] + "####" + current_user[3] + "####" + current_user[4])
                        else:
                            fo.write(user)
                    fo.close()
            elif request.form['password'] != "" and request.form['email'] != email:
                with open('users.txt', "w") as fo:
                    for user in users:
                        current_user =  user.split("####")
                        if current_user[0] == username:
                            fo.write("\n" + current_user[0] + "####" + sha256_crypt.hash(request.form['password']) + "####" + request.form['email'] + "####" + current_user[3] + "####" + current_user[4])
                        else:
                            fo.write(user)
                    fo.close()
                    email = request.form['email']
        elif request.form['mode']!= mode and (request.form['password']!="" or request.form['email']!= email):
            with open(user_mode, "w") as fo:
                fo.write(request.form['mode'])
                session['mode'] = request.form['mode']
                fo.close()
            users = []
            with open('users.txt', "r") as fr:
                temp_users = fr.readlines()
                fr.close()
            for user in temp_users:
                x = user.split("####")
                if user == "":
                    continue
                users.append(user)
            if request.form['password'] != "" and request.form['email'] == email:
                with open('users.txt', "w") as fo:
                    for user in users:
                        current_user = user.split("####")
                        if current_user[0] == username:
                            fo.write("\n" + current_user[0] + "####" + sha256_crypt.hash(request.form['password']) + "####" + current_user[2] + "####" + current_user[3] + "####" + current_user[4])
                        else:
                            fo.write("\n" + user)
                    fo.close()
            elif request.form['password'] == "" and request.form['email'] != email:
                with open('users.txt', "w") as fo:
                    for user in users:
                        current_user = user.split("####")
                        if current_user[0] == username:
                            fo.write("\n" + current_user[0] + "####" + current_user[1] + "####" + request.form['email'] + "####" + current_user[3] + "####" + current_user[4])
                        else:
                            fo.write(user)
                    fo.close()
            elif request.form['password'] != "" and request.form['email'] != email:
                with open('users.txt', "w") as fo:
                    for user in users:
                        current_user = user.split("####")
                        if current_user[0] == username:
                            fo.write("\n" + current_user[0] + "####" + sha256_crypt.hash(request.form['password']) + "####" +  request.form['email'] + "####" + current_user[3] + "####" + current_user[4])
                        else:
                            fo.write("\n" + user)
                    fo.close()
                    email = request.form['email']
        flash('Settings changed successfully')

    return render_template('settings.html')

# add task page
@app.route('/add_task_page', methods=['POST','GET'])
def add_task_page():
    # calling global variables
    global username
    global user_file
    # Add a task using the append method of a text file
    if request.method=='POST':
        flash('')
        if request.form['description']=="":
            flash('Task Description not entered')
            return render_template('add_task.html')
        with open(user_file, "a") as fo:
            fo.write("\n"+request.form['task']+"####"+ request.form['description']+"####"+request.form['progress'])
        flash('Task added successfully')
        fo.close()
    return render_template('add_task.html')

# delete task page
@app.route('/delete_task_page', methods=['POST','GET'])
def delete_task_page():
    # calling global variables
    global username
    global user_file
    # Displaying all tasks in a table
    html_string = '<table border=1 style="width:100%;border:1px solid;"><th width="10%">Task No.</th><th width="15%">Task</th><th width="65%">Description</th><th width="10%">Progress</th>'
    if os.path.isfile(user_file):
        row = 0
        with open(user_file, "r") as fr:
            lines = fr.readlines()
            for i in range(len(lines)):
                if lines[i].strip() == "":
                    continue
                else:
                    row += 1
                    line_info = lines[i].split('####')
                    html_string += '<tr><td width="10">' + str(row) + '</td><td width="15%">' + line_info[0] + '</td><td width="15%">' + line_info[1] + '</td><td width="10%">' + line_info[2] + '</td></tr>'
            html_string += '</table>'
            flash(Markup(html_string))
    # Overwriting the entire task file after deleting the chosen task
    if request.method=='POST':
        flash('')
        if request.form['task_number']=="":
            flash('Task No. not entered')
            return render_template('delete_task.html')
        x = []
        with open(user_file, "r") as fr:
            lines = fr.readlines()
            fr.close()
            for line in lines:
                if line == "" or line == "\n":
                    continue
                x.append(line)
        x.pop(int(request.form['task_number']) - 1)
        with open(user_file, "w") as fo:
            for i in range(len(x)):
                    fo.write(x[i] + "\n")
        fo.close()
        flash('Task Deleted successfully')
    return render_template('delete_task.html')

# update task page
@app.route('/update_task_page', methods=['POST','GET'])
def update_task_page():
    # calling global variables
    global username
    global user_file
    # Displaying all tasks in a table
    html_string = '<table border=1 style="width:100%;border:1px solid;"><th width="10%">Task No.</th><th width="15%">Task</th><th width="65%">Description</th><th width="10%">Progress</th>'
    if os.path.isfile(user_file):
        row = 0
        with open(user_file, "r") as fr:
            lines = fr.readlines()
            for i in range(len(lines)):
                if lines[i].strip() == "":
                    continue
                row += 1
                line_info = lines[i].split('####')
                html_string += '<tr><td width="10">'+ str(row) +'</td><td width="15%">' + line_info[0] + '</td><td width="15%">' + line_info[
                    1] + '</td><td width="10%">' + line_info[2] + '</td></tr>'
            html_string += '</table>'
            flash(Markup(html_string))
    # Overwriting the entire task file after modifying the chosen task
    if request.method=='POST':
        flash('')
        if request.form['task_number']=="":
            flash('Task Description not entered')
            return render_template('update_task.html')
        x = []
        with open(user_file, "r") as fo:
            lines = fo.readlines()
            fo.close()
        for line in lines:
            if line == "" or line == "\n":
                continue
            x.append(line)
        j = (len(x))
        x.pop(int(request.form['task_number']) - 1)
        with open(user_file, "w") as fo:
            for i in range(j):
                if i == int(request.form['task_number']) - 1:
                    fo.write("\n" + request.form['task'] + "####" + request.form['description'] + "####" + request.form['progress'])
                elif i < int(request.form['task_number']) - 1:
                    fo.write("\n" + x[i])
                elif i > int(request.form['task_number']) - 1:
                    fo.write("\n" + x[i-1])
            fo.close()
        flash('Task Updated successfully')
    return render_template('update_task.html')

# About page
@app.route('/about_page')
def about_page():
    return render_template('about_page.html')
# Create account_page
@app.route('/create_account_page', methods=['POST','GET'])
def create_account_page():
    # Checking whether all details are entered and using the append method to add a new user (also checks if user already exists)
    if request.method=='POST':
        flash('')
        if request.form['username']=="":
            flash('User name not entered')
            return render_template('create_account_page.html')
        if request.form['password']=="":
            flash('Password not entered')
            return render_template('create_account_page.html')
        if request.form['con_password']=="":
            flash('Confirm Password not entered')
            return render_template('create_account_page.html')
        if request.form['password']!=request.form['con_password']:
            flash('Password and confirm password did not match')
            return render_template('create_account_page.html')
        if request.form['email']=="":
            flash('Email not entered')
            return render_template('create_account_page.html')
        if request.form['SQ']=="":
            flash('Security not entered')
            return render_template('create_account_page.html')
        if request.form['AK']=="":
            flash('Answer Key not entered')
            return render_template('create_account_page.html')
        filename="./users.txt"
        if os.path.isfile(filename):
            with open(filename, "r") as fr:
                for line in fr.readlines():
                    if line.strip()=="":
                        continue
                    login_info = line.split('####')
                    if request.form['username'] == login_info[0]:
                        flash('Username already exist. Choose another')
                        return render_template('create_account_page.html')
                fr.close()
        with open(filename, "a") as fo:
            fo.write("\n" + request.form['username']+ "####" + sha256_crypt.hash(request.form['password']) + "####" + request.form['email'] + "####" +request.form['SQ'] + "####" + request.form['AK'])
            fo.close()
            # Calling global variables
            global user_file
            global user_mode
            # Updating global variables
            user_file = "./" + request.form['username'] + "_tasks.txt"
            user_mode = "./" + request.form['username'] + "_mode.txt"
            # Creating files for the new user
            with open(user_file, 'w') as fc:
                fc.close()
            with open(user_mode, 'w') as fc:
                fc.close()
            flash('User created successfully')

    return render_template('create_account_page.html')
# Running the Application
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
