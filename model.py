import mysql.connector
from config import Config
import bcrypt
from datetime import datetime, timedelta

def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='9922',
        database='emp_db'
    )
    return conn

#store register data
def create_user(username, password, role, name, gender, dob, phone, email, address, joining_date):
    # Hash the password using bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password, role, name, gender, dob, phone, email, address, joining_date) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (username, hashed_password, role, name, gender, dob, phone, email, address, joining_date)
    )
    conn.commit()
    cursor.close()
    conn.close()

# Function to check the username and password
def check_employee(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, password, role FROM users WHERE username = %s", (username,))
    employee = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if employee:  # If employee is found
        stored_password_hash = employee[1]  # Assuming password is in the second column
        # Check the password using bcrypt
        if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):  # Encode both to bytes
            return employee  # Return the whole row for HR employee
    return None  # If password doesn't match or user not found

def get_user_by_email(email):
    # Establish a database connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query to fetch the user by email
    cursor.execute("SELECT username, password FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user

#forgot password=================================================================================
def change_password(username, new_password):
    # Hash the new password
    hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = %s WHERE username = %s", (hashed_new_password, username))
    conn.commit()
    cursor.close()
    conn.close()

# Get all employee
def get_all_employees(start_date=None, end_date=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Adjust the query to filter based on joining_date or another date column
    if start_date and end_date:
        query = "SELECT * FROM users WHERE joining_date BETWEEN %s AND %s"
        cursor.execute(query, (start_date, end_date))
    else:
        query = "SELECT * FROM users"
        cursor.execute(query)
    
    employees = cursor.fetchall()
    cursor.close()
    conn.close()
    return employees

# Delete employee by ID
def delete_employee(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # SQL query to delete the employee from the 'users' table
    cursor.execute("DELETE FROM users WHERE id = %s", (employee_id,))
    
    conn.commit()  # Commit the deletion to the database
    cursor.close()
    conn.close()

#get info for employee
def get_employee_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    employee = cursor.fetchone()  # Use fetchone() for a single record
    cursor.close()
    conn.close()
    return employee

#id for delete the employee==========================================
def get_employee_by_id(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (employee_id,))
    employee = cursor.fetchone()
    cursor.close()
    conn.close()
    return employee 

#eidit the employee info========================================================================
def update_employee(employee_id, name, gender, dob, phone, email, address, username, role, joining_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE users
        SET name = %s, gender = %s, dob = %s, phone = %s, email = %s, address = %s, username = %s, role = %s, joining_date = %s
        WHERE id = %s
    """, (name, gender, dob, phone, email, address, username, role, joining_date, employee_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
# Create department
def create_department( name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO departments (name) VALUES (%s)", (name,))
    conn.commit()
    cursor.close()    
    conn.close()

# Get all department
def get_all_department():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM departments")
    departments = cursor.fetchall()
    cursor.close()
    conn.close()
    return departments

def delete__departments(departments_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # SQL query to delete the employee from the 'users' table
    cursor.execute("DELETE FROM departments WHERE id = %s", (departments_id,))
    
    conn.commit()  # Commit the deletion to the database
    cursor.close()
    conn.close()

def get_all_employee_ids():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    employees = cursor.fetchall()
    cursor.close()
    conn.close()
    return employees

# Mark attendance
def get_last_attendance_time(username):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT date FROM attendance WHERE username = %s ORDER BY date DESC LIMIT 1", (username,))
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if result:
        # Return the last attendance date
        return result[0]
    return None

def submit_attendance(username, date, status,employee_id,employee_name):
    # Check if 12 hours have passed since the last attendance
    last_attendance_time = get_last_attendance_time(username)
    
    if last_attendance_time:
        # Calculate the time difference between now and the last attendance
        time_diff = datetime.now() - last_attendance_time
        
        # If less than 12 hours have passed, don't allow attendance submission
        if time_diff < timedelta(hours=12):
            return "You can only mark attendance once every 12 hours. Try again later."

    # If more than 12 hours have passed, proceed with marking attendance
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO attendance (username, date, status,employee_id,employee_name) VALUES (%s, %s, %s, %s, %s)", (username, date, status,employee_id,employee_name))
    conn.commit()
    cursor.close()
    conn.close()

    return "Attendance marked successfully!"

# Get attendance by employee
def get_attendance_by_employee(start_date=None, end_date=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Modify query to use date range if provided
    if start_date and end_date:
        cursor.execute("SELECT * FROM attendance WHERE date BETWEEN %s AND %s", (start_date, end_date))
    else:
        cursor.execute("SELECT * FROM attendance")

    attendance = cursor.fetchall()
    cursor.close()
    conn.close()
    
    print(f"Fetched Attendance Records: {attendance}")  # Debug: Print the fetched records
    
    return attendance


# Get employee by employee
def get_all_employee_salary():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    employees = cursor.fetchall()
    cursor.close()
    conn.close()
    return employees

def get_department_salary():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM departments")
    departments = cursor.fetchall()
    cursor.close()
    conn.close()
    return departments

def save_salary(employee_id,department,emp_name,base_salary, bonus, medical, conveyance, tax,pf, net_salary,date,username,totalday,Absent,per_day):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(" INSERT INTO payroll (employee_id,department,emp_name,base_salary, bonus, medical, conveyance, tax,pf, net_salary,date,username,totalday,Absent,per_day)VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(employee_id,department,emp_name,base_salary, bonus, medical, conveyance, tax,pf, net_salary,date,username,totalday,Absent,per_day))
    conn.commit()
    cursor.close()
    conn.close()

def get_all_salary_info():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM payroll")
    salary = cursor.fetchall()
    cursor.close()
    conn.close()
    return salary

def get_salary_info_by_id(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM payroll WHERE employee_id = %s", (employee_id,))
    salary = cursor.fetchone()  # Fetch one record as a dictionary
    cursor.close()
    conn.close()
    return salary

def update_salary_info(employee_id, department, emp_name, base_salary, bonus, medical, conveyance, tax, pf, net_salary, date, username, totalday, Absent, per_day):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update salary data for the given employee_id
    query = """
    UPDATE payroll
    SET department = %s, emp_name = %s, base_salary = %s, bonus = %s, medical = %s, conveyance = %s, 
        tax = %s, pf = %s, net_salary = %s, date = %s, username = %s, totalday = %s, Absent = %s, per_day = %s
    WHERE employee_id = %s
    """
    cursor.execute(query, (department, emp_name, base_salary, bonus, medical, conveyance, tax, pf, net_salary, date, username, totalday, Absent, per_day, employee_id))
    conn.commit()
    cursor.close()
    conn.close()


def delete_salary_info(employee_id):
    # Get database connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Delete the record matching the employee_id
    cursor.execute("DELETE FROM payroll WHERE employee_id = %s", (employee_id,))
    
    # Commit the change and close connection
    conn.commit()
    cursor.close()
    conn.close()

def get_employee_for_payroll(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM payroll WHERE employee_id = %s", (employee_id,))
    employee = cursor.fetchone()
    cursor.close()
    conn.close()
    return employee

def get_employee_for_slip(username):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM payroll WHERE username = %s", (username,))
    employee = cursor.fetchone()
    cursor.close()
    conn.close()
    return employee

def save_feedback(username, email, message):
    # Get the current date
    created_at = datetime.now().strftime('%Y-%m-%d')  # Format the date and time
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Updated query assuming the column is now 'created_at'
    cursor.execute("""
        INSERT INTO feedback (username, email, message, created_at) 
        VALUES (%s, %s, %s, %s)
    """, (username, email, message, created_at))
    
    conn.commit()
    cursor.close()
    conn.close()


def get_Feedback():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM feedback")
    feedback = cursor.fetchall()
    cursor.close()
    conn.close()
    return feedback

def get_Feedback_by_date_range(start_date, end_date):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM feedback
        WHERE current_date BETWEEN %s AND %s
    """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    feedback = cursor.fetchall()
    cursor.close()
    conn.close()
    return feedback