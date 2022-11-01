from multiprocessing import connection
from sqlite3 import Cursor
from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import mysql.connector
import re 
import datetime as dt
import yaml

#cursor = connection.cursor()
app = Flask(__name__,static_folder='./static',static_url_path='/static')
#Set secret key for the session
app.secret_key = "123kfdd12"

#Configure my sql db details
db = yaml.full_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

# Instantiation of MySQL Object
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('auth/login.html')

# http://localhost:5000/hrmslogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/hrmslogin', methods=['GET', 'POST'])
def login():
# Output message if something goes wrong...
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM hrmsdb.accounts WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
                # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            flash("Incorrect username/password!", "danger")
    return render_template('auth/login.html',title="Login")

# http://localhost:5000/pythinlogin/register 
# This will be the registration page, we need to use both GET and POST requests
@app.route('/hrmslogin/register', methods=['GET', 'POST'])
def register():
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'id' in request.form and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        id = request.form['id']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
                # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
        cursor.execute( "SELECT * FROM accounts WHERE username LIKE %s", [username] )
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            flash("Account already exists!", "danger")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Invalid email address!", "danger")
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash("Username must contain only characters and numbers!", "danger")
        elif not username or not password or not email:
            flash("Incorrect username/password!", "danger")
        elif not username or not password or not email or not id:
            flash("ID already exists","danger")
        else:
        # Account doesnt exists and the form data is valid, now insert new account into accounts table
            #cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username,email, password))
            cursor.execute('INSERT INTO accounts VALUES (%s, %s, %s, %s)', (id, username, password, email))
            mysql.connection.commit()
            flash("You have successfully registered!", "success")
            return redirect(url_for('login'))

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash("Please fill out the form!", "danger")
    # Show registration form with message (if any)
    return render_template('auth/register.html',title="Register")


#End Point - Logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('/'))
    #return render_template('auth/login.html',title="Login")

# http://localhost:5000/pythinlogin/home 
# This will be the home page, only accessible for loggedin users


@app.route('/hrmslogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home/home.html', username=session['username'],title="Home")
    # User is not loggedin redirect to login page
    return redirect(url_for('login')) 

@app.route('/hrmslogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('auth/profile.html', username=session['username'],title="Profile")
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

#End Point - To display all the Course Details
@app.route('/course_list')
def course_list():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("select * from course")
    if resultValue > 0:
        courseSelectDetails = cur.fetchall()
        return render_template('course_list.html',courseSelectDetails=courseSelectDetails)
    
#End Point - To display all the Employee Details
@app.route('/employee_list')
def employee_list():
    cur = mysql.connection.cursor()
    employeeResultValue = cur.execute("SELECT hrmsdb.employee.EMP_ID, hrmsdb.employee.FIRST_NAME, hrmsdb.employee.LAST_NAME,"+ 
" hrmsdb.employee_contact_details.EMAIL, hrmsdb.employee_contact_details.PHONE_NUMBER, hrmsdb.employee.DEPT_ID, "+
" hrmsdb.employee.JOB_ID, hrmsdb.employee.MANAGER_ID, hrmsdb.employee.DATE_OF_JOINING"+
" FROM hrmsdb.employee INNER JOIN hrmsdb.employee_contact_details ON"+
" hrmsdb.employee.EMP_ID = hrmsdb.employee_contact_details.EMP_ID")
    if employeeResultValue > 0:
        employeeSelectDetails = cur.fetchall()
        return render_template('employee_list.html',employeeSelectDetails=employeeSelectDetails)

#End Point - To display all the Dependent Details
@app.route('/dependent_list')
def dependent_list():
    cur = mysql.connection.cursor()
    dependentResultValue = cur.execute("SELECT hrmsdb.dependent.DEPENDENT_ID, hrmsdb.dependent.EMP_ID, hrmsdb.dependent.FIRST_NAME,"+
" hrmsdb.dependent.LAST_NAME, hrmsdb.dependent.RELATION, hrmsdb.dependent.PHONE_NUMBER,"+
" hrmsdb.dependent.EMAIL, hrmsdb.dependent_address.HOUSE_NO, hrmsdb.dependent_address.ADDRESS_LINE,"+
" hrmsdb.dependent_address.CITY, hrmsdb.dependent_address.STATE, hrmsdb.dependent_address.PINCODE," +
" hrmsdb.dependent_address.COUNTRY FROM hrmsdb.dependent JOIN hrmsdb.dependent_address ON" +
" hrmsdb.dependent.DEPENDENT_ID = hrmsdb.dependent_address.DEPENDENT_ID")
    if dependentResultValue > 0:
        dependentSelectDetails = cur.fetchall()
        return render_template('dependent_list.html',dependentSelectDetails=dependentSelectDetails)
    
#End Point - To display all the Dependent Details from view
@app.route('/dependent_view')
def dependent_view():
    cur = mysql.connection.cursor()
    dependentResultValue = cur.execute("SELECT * FROM hrmsdb.dependent_details_table")
    if dependentResultValue > 0:
        dependentViewDetails = cur.fetchall()
        return render_template('dependent_view.html',dependentViewDetails=dependentViewDetails)
    

#End Point - To display all the Performance and Ratings Details
@app.route('/performance_ratings')
def performance_ratings():
    cur = mysql.connection.cursor()
    ratingsValue = cur.execute("select * from performance_review")
    if ratingsValue > 0:
        ratingSelectDetails = cur.fetchall()
        return render_template('performance.html',ratingSelectDetails=ratingSelectDetails)
    
#End Point - To display all the Job Details
@app.route('/job_details')
def job_details():
    cur = mysql.connection.cursor()
    jobValue = cur.execute("SELECT hrmsdb.employee.EMP_ID, hrmsdb.employee.FIRST_NAME, hrmsdb.employee.LAST_NAME,"+
" hrmsdb.job.JOB_ID, hrmsdb.job.DEPT_ID, hrmsdb.job.JOB_TITLE, hrmsdb.job.MIN_SALARY," +
" hrmsdb.job.MAX_SALARY FROM hrmsdb.employee JOIN hrmsdb.job ON" +
" hrmsdb.employee.JOB_ID = hrmsdb.job.JOB_ID")
    if jobValue > 0:
        jobSelectDetails = cur.fetchall()
        return render_template('job_list.html',jobSelectDetails=jobSelectDetails)
    
#End Point - To display list of Job Details
@app.route('/job')
def job():
    cur = mysql.connection.cursor()
    jobValue = cur.execute("SELECT * FROM hrmsdb.job")
    if jobValue > 0:
        jobDisplayDetails = cur.fetchall()
        return render_template('job.html',jobDisplayDetails=jobDisplayDetails)

#End Point - Update the Course table in MySQL Database
@app.route('/insert_course', methods=['GET','POST'])
def insert_course():
    if request.method == 'POST':
    # Fetch form data
        insertCourseDetails = request.form
        course_id = insertCourseDetails['course_id']
        credit_hours = insertCourseDetails['credit_hours']
        course_name = insertCourseDetails['course_name']
        cur = mysql.connection.cursor()      
        cur.execute("INSERT INTO hrmsdb.course (course_id, credit_hours, course_name) VALUES (%s, %s, %s)",(course_id, credit_hours, course_name))
        mysql.connection.commit()
        cur.close()
        msg = "Successfully Added a new Course"
        return redirect('/course_list')

    else:
        return render_template('insert_course.html')
    
#End Point - Insert data in Employee table in MySQL Database
@app.route('/insert_employee', methods=['GET','POST'])
def insert_employee():
    if request.method == 'POST':
    # Fetch form data
        insertEmployeeDetails = request.form
        employee_id = insertEmployeeDetails['employee_id']
        first_name = insertEmployeeDetails['first_name']
        last_name = insertEmployeeDetails['last_name']
        department_id = insertEmployeeDetails['department_id']
        job_id = insertEmployeeDetails['job_id']
        manager_id = insertEmployeeDetails['manager_id']
        date_of_joining = insertEmployeeDetails['date_of_joining']
        cur = mysql.connection.cursor()      
        sql_query = "INSERT INTO hrmsdb.employee (EMP_ID, FIRST_NAME, LAST_NAME, DEPT_ID, JOB_ID, MANAGER_ID, DATE_OF_JOINING) VALUES (%s, %s, %s,%s, %s, %s, %s)"
        values = (employee_id, first_name, last_name, department_id, job_id, manager_id, date_of_joining)
        cur.execute(sql_query,values)
        mysql.connection.commit()
        cur.close()
        return redirect('/employee_list')
    else:
        return render_template('insert_employee.html')
    
#End Point - Update the Employee table in MySQL Database
@app.route('/update_employee', methods=['GET','POST'])
def update_employee():
    if request.method == 'POST':
    # Fetch form data
        updateEmployeeDetails = request.form
        employee_id = updateEmployeeDetails['employee_id']
        first_name = updateEmployeeDetails['first_name']
        last_name = updateEmployeeDetails['last_name']
        cur = mysql.connection.cursor()      
        sql_query = "UPDATE hrmsdb.employee"+" SET hrmsdb.employee.FIRST_NAME = %s, hrmsdb.employee.LAST_NAME= %s"+" WHERE hrmsdb.employee.EMP_ID = %s"
        values = (first_name, last_name, employee_id)
        cur.execute(sql_query,values)
        mysql.connection.commit()
        cur.close()
        return redirect('/employee_list')
    else:
        return render_template('update_employee.html')
    
#End Point - Update the Job table - Employee Designation in MySQL Database
@app.route('/update_jobTitle', methods=['GET','POST'])
def update_jobTitle():
    if request.method == 'POST':
    # Fetch form data
        updateJobTitleDetails = request.form
        job_title = updateJobTitleDetails['job_title']
        job_id = updateJobTitleDetails['job_id']
        cur = mysql.connection.cursor()      
        sql_query = "UPDATE hrmsdb.job SET hrmsdb.job.JOB_TITLE = %s WHERE hrmsdb.job.JOB_ID = %s"
        values = (job_title, job_id)
        cur.execute(sql_query,values)
        mysql.connection.commit()
        cur.close()
        return redirect('/job')
    else:
        return render_template('update_jobTitle.html')
    
#End Point - Update the Job table - Employee Maximum salary in MySQL Database
@app.route('/update_jobSalary', methods=['GET','POST'])
def update_jobSalary():
    if request.method == 'POST':
    # Fetch form data
        updateJobSalaryDetails = request.form
        max_salary = updateJobSalaryDetails['max_salary']
        job_id = updateJobSalaryDetails['job_id']
        cur = mysql.connection.cursor()      
        sql_query = "UPDATE hrmsdb.job SET MAX_SALARY = %s WHERE JOB_ID = %s"
        values = (max_salary, job_id)
        cur.execute(sql_query,values)
        mysql.connection.commit()
        cur.close()
        return redirect('/job')
    else:
        return render_template('update_jobSalary.html')
    
#End Point - Update the Dependent view in MySQL Database
@app.route('/update_dependent', methods=['GET','POST'])
def update_dependent():
    if request.method == 'POST':
    # Fetch form data
        updateDependentDetails = request.form
        first_name = updateDependentDetails['first_name']
        last_name = updateDependentDetails['last_name']
        relation = updateDependentDetails['relation']
        email = updateDependentDetails['email']
        dependent_id = updateDependentDetails['dependent_id']
        cur = mysql.connection.cursor()      
        sql_query = "UPDATE hrmsdb.dependent_details_table SET hrmsdb.dependent_details_table.FIRST_NAME = %s,"+" hrmsdb.dependent_details_table.LAST_NAME = %s, hrmsdb.dependent_details_table.RELATION = %s,"+" hrmsdb.dependent_details_table.EMAIL = %s WHERE hrmsdb.dependent_details_table.DEPENDENT_ID = %s"
        values = (first_name, last_name, relation,email,dependent_id)
        cur.execute(sql_query,values)
        mysql.connection.commit()
        cur.close()
        return redirect('/dependent_view')
    else:
        return render_template('update_dependent.html')

#End Point - Delete the record from Dependent view in MySQL Database
@app.route('/delete_dependent', methods=['GET','POST'])
def delete_dependent():
    if request.method == 'POST':
    # Fetch form data
        deleteDependentDetails = request.form
        dependent_id = deleteDependentDetails['dependent_id']  
        first_name = deleteDependentDetails['first_name']       
        cur = mysql.connection.cursor()      
        sql_query = "DELETE hrmsdb.dependent,hrmsdb.dependent_address FROM hrmsdb.dependent INNER JOIN hrmsdb.dependent_address WHERE hrmsdb.dependent.DEPENDENT_ID = hrmsdb.dependent_address.DEPENDENT_ID AND hrmsdb.dependent.DEPENDENT_ID = %s AND hrmsdb.dependent.FIRST_NAME = %s"
        value = (dependent_id, first_name)
        cur.execute(sql_query, value)
        mysql.connection.commit()
        cur.close()
        return redirect('/dependent_view')
    else:
        return render_template('delete_dependent.html')
    
#End Point - Delete the record from Employee table in MySQL Database
@app.route('/delete_employee', methods=['GET','POST'])
def delete_employee():
    if request.method == 'POST':
    # Fetch form data
        deleteEmployeeDetails = request.form
        employee_id = deleteEmployeeDetails['employee_id']  
        first_name = deleteEmployeeDetails['first_name']       
        cur = mysql.connection.cursor()      
        sql_query = "DELETE FROM hrmsdb.employee WHERE EMP_ID = %s AND FIRST_NAME = %s;"
        value = (employee_id, first_name)
        cur.execute(sql_query, value)
        mysql.connection.commit()
        cur.close()
        return redirect('/employee_list')
    else:
        return render_template('delete_employee.html')

#End Point - Delete the Course table in MySQL Database
@app.route('/delete_course', methods=['GET','POST'])
def delete_course():
    if request.method == 'POST':
    # Fetch form data
        deleteCourseDetails = request.form
        course_id = deleteCourseDetails['course_id']
        credit_hours = deleteCourseDetails['credit_hours']
        course_name = deleteCourseDetails['course_name']        
        cur = mysql.connection.cursor()      
        cur.execute("DELETE FROM hrmsdb.course WHERE course_id = %s AND credit_hours = %s AND course_name = %s", (course_id,credit_hours,course_name))
        mysql.connection.commit()
        cur.close()
        return redirect('/course_list')
    else:
        return render_template('delete_course.html')
    
#End Point - Update a Course table in MySQL Database
@app.route('/update_course',methods=['GET','POST'])
def update_course():
    if request.method == 'POST':
    # Fetch form data
        updateCourseDetails = request.form
        course_id = updateCourseDetails['course_id']
        credit_hours = updateCourseDetails['credit_hours']
        course_name = updateCourseDetails['course_name']
        cur = mysql.connection.cursor()      
        updateResult = cur.execute("UPDATE hrmsdb.course SET credit_hours = %s, course_name = %s WHERE course_id = %s", (credit_hours, course_name, course_id))
        if updateResult > 0:
            updateCourseDetails = cur.fetchall()
            #return render_template('update_details.html',updateCourseDetails=updateCourseDetails )
            print(updateCourseDetails)
            flash("Data Updated Sucessfully")
        mysql.connection.commit()
        cur.close()
        #return redirect('/course_list')
        return redirect(url_for('course_list'))
    else:
        return render_template('update_course.html')
    
#End Point for Training Programs Module
@app.route('/training_programs')
def training_programs():
    #return render_template('home.html', username = session['username'])
    return render_template('training_programs.html') 

#End Point - To display all the Completed trainings
@app.route('/completed_trainings')
def completed_trainings():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("select * from hrmsdb.training")
    if resultValue > 0:
        trainingSelectDetails = cur.fetchall()
        return render_template('completed_trainings.html',trainingSelectDetails=trainingSelectDetails)


#End Point - Add a new course details in MySQL Database of course table
@app.route('/insert_training', methods=['GET','POST'])
def insert_training():
    if request.method == 'POST':
    # Fetch form data
        insertTrainingDetails = request.form
        training_id = insertTrainingDetails['training_id']
        emp_id = insertTrainingDetails['emp_id']
        platform = insertTrainingDetails['platform']
        doc = dt.datetime.strptime(request.form['doc'], '%Y-%m-%d')
        cur = mysql.connection.cursor()      
        cur.execute("INSERT INTO hrmsdb.training (training_id, emp_id, platform, date_of_completion) VALUES (%s, %s, %s, %s)",(training_id, emp_id, platform, doc))
        mysql.connection.commit()
        cur.close()
        return redirect('/completed_trainings')
    else:
        return render_template('insert_training.html')

#End Point - Delete a Course record from course table in MySQL Database
@app.route('/delete_training', methods=['GET','POST'])
def delete_training():
    if request.method == 'POST':
    # Fetch form data
        deleteTrainingDetails = request.form
        training_id = deleteTrainingDetails['training_id']
        emp_id = deleteTrainingDetails['emp_id']
        cur = mysql.connection.cursor()      
        cur.execute("DELETE FROM hrmsdb.training WHERE training_id = %s AND emp_id = %s", (training_id, emp_id))
        mysql.connection.commit()
        cur.close()
        return redirect('/completed_trainings')
    else:
        return render_template('delete_training.html')

#End Point - Update a training record in MySQL Database for training table
@app.route('/update_training',methods=['GET','POST'])
def update_training():
    if request.method == 'POST':
        training_id = request.form['training_id']
        emp_id = request.form['emp_id']
        platform = request.form['platform']
        date_of_completion = request.form['date_of_completion']
        date_of_completion = dt.datetime.strptime(request.form['date_of_completion'],'%Y-%m-%d')
        #date_of_completion = updateTrainingDetails[datetime.strptime(request.form['date_of_completion'], '%Y-%m-%d')]
        #doc = dt.datetime.strptime(request.form['doc'], '%Y-%m-%d')
        cur = mysql.connection.cursor()      
        #cur.execute("UPDATE training_table SET emp_id = %s, platform = %s, date_of_completion = %s WHERE training_id = %s", (emp_id, platform, doc, training_id))
        cur.execute("UPDATE hrmsdb.training SET emp_id = %s, platform = %s, date_of_completion = %s WHERE training_id = %s", (emp_id, platform, date_of_completion, training_id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('/completed_trainings'))
    else:
        return render_template('update_training.html')

# End Point - To get a list of Course Completed from a particular training Program from MySQL Database - Join Operation
# 
@app.route('/employee_trainings', methods=['GET','POST'])
def employee_trainings():
    if request.method == 'POST':
    # Fetch form data
        #employeeTrainingDetails = request.form
        #training_id = employeeTrainingDetails['training_id']
        training_id = request.form['training_id']
        cur = mysql.connection.cursor() 
        try:     
            cur.execute("SELECT * FROM hrmsdb.training_record WHERE TRAINING_ID = %s")(training_id)
            for row in cur:
                print("%s %s %s"%(row[0],row[1],row[2]))
        except:        
        #mysql.connection.commit()
            cur.connection.rollback()
            flash("Operation Completed")
        cur.close()
        return redirect('/training_record')
    else:
        return render_template('employee_trainings.html')
  
    
#End Point - To display all the training records
@app.route('/training_record')
def training_record():
    cur = mysql.connection.cursor()
    resultValue = cur.execute(("SELECT * FROM hrmsdb.training_record"))
    if resultValue > 0:
        trainingCompletedDetails = cur.fetchall()
        return render_template('training_record.html',trainingCompletedDetails=trainingCompletedDetails)

#This will ensure that any changes made updated immediately on the web browser
if __name__ == '__main__':
  app.run(debug=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0')    