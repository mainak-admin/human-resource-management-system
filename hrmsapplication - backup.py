#from crypt import methods
#from urllib import request
from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
import mysql.connector
import MySQLdb.cursors
import re 
import yaml

app = Flask(__name__,static_folder='./static',static_url_path='/static')

#Set secret key for the session
app.secret_key = "super secret key"


#Configure my sql db details
db = yaml.full_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

# Instantiation of MySQL Object
mysql = MySQL(app)

#End Point -
@app.route('/')
def index():
    return render_template('index.html')

#End Point - Login Page
@app.route('/login', methods=['GET','POST'])
def login():
    #
    msg = "Something Wrong"  
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST': 
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        #cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur = mysql.connection.cursor()  
        cur.execute("select * from accounts where username = %s AND password = %s", (username, password,))
        # Fetch one record and return result
        account = cur.fetchone()
        # If account exists in accounts table in our database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['username'] = account[1]
            # Redirect to home page
            #return 'Login Suceess'
            return redirect(url_for('home'))
        else:
            # If Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!. Try again'
            # Show the login form with Error message (if any)
    return render_template('index.html', msg = msg)


#End Point - Home Page
@app.route('/home')
def home():
    return render_template('home.html', username = session['username'])


#End Point - Update the Course table in MySQL Database
@app.route('/update_course', methods=['GET','POST'])
def update_course():
    if request.method == 'POST':
    # Fetch form data
        updateCourseDetails = request.form
        course_id = updateCourseDetails['course_id']
        credit_hours = updateCourseDetails['credit_hours']
        course_name = updateCourseDetails['course_name']
        cur = mysql.connection.cursor()      
        cur.execute("INSERT INTO course (course_id, credit_hours, course_name) VALUES (%s, %s, %s)",(course_id, credit_hours, course_name))
        mysql.connection.commit()
        cur.close()
        return redirect('/course_list')
    return render_template('update_course.html')

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
        cur.execute("UPDATE hrmsdb.employee"+
" SET hrmsdb.employee.FIRST_NAME = %s, hrmsdb.employee.LAST_NAME= %s"+
" WHERE hrmsdb.employee.EMP_ID = %s",(employee_id,first_name,last_name))
        mysql.connection.commit()
        cur.close()
        return redirect('/employee_list')
    else:
        return render_template('update_employee.html')
    
#End Point - Select the Course table from  MySQL Database
#End Point - Insert data into Employee table
#End Point - Insert data in Course table in MySQL Database
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
  
#End Point - Select the Course table from  MySQL Database
#End Point - To display all the Course Details
@app.route('/course_list')
def course_list():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("select * from course")
    if resultValue > 0:
        courseSelectDetails = cur.fetchall()
        return render_template('course_list.html',courseSelectDetails=courseSelectDetails)

#End Point - Select the Employee table from  MySQL Database
#End Point - To display all the Course Details
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
    

#End Point - Select the Dependent table from  MySQL Database
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

#End Point - Select the Performance Ratings table from MySQL Database
#End Point - To display all the Performance Details
@app.route('/performance_ratings')
def performance_ratings():
    cur = mysql.connection.cursor()
    ratingsValue = cur.execute("select * from performance_review")
    if ratingsValue > 0:
        ratingSelectDetails = cur.fetchall()
        return render_template('performance.html',ratingSelectDetails=ratingSelectDetails)

#End Point - Select the Job details table from MySQL Database
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
        return render_template('job.html',jobSelectDetails=jobSelectDetails)

#This will ensure that any changes made updated immediately on the web browser
if __name__ == '__main__':
  app.run(debug=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0')