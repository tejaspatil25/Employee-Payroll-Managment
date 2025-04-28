from flask import Flask, render_template, request, redirect, url_for, session, flash
from model import get_user_by_email,check_employee,delete__departments,delete_employee,get_last_attendance_time,get_employee_by_username,create_department,create_user, get_Feedback, get_all_department, get_all_employee_ids, get_all_employee_salary, get_all_employees, get_all_salary_info, get_attendance_by_employee, get_department_salary, get_employee_by_id, get_employee_for_payroll, get_employee_for_slip, save_feedback, save_salary, submit_attendance,get_salary_info_by_id,delete_salary_info,update_employee,update_salary_info
from datetime import datetime,timedelta
from model import get_db_connection 
import random
import string
from flask_mail import Mail,Message

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'apexicu2015@gmail.com'
app.config['MAIL_PASSWORD'] = 'yeem aaxc clev lxei'
app.config['MAIL_USE_TLS'] = True  # Use TLS for encryption
app.config['MAIL_USE_SSL'] = False  # Don't use SSL, as it's for SSL-only ports

mail = Mail(app)

@app.route('/')
def index():
    return render_template('login.html')

#Registration form
@app.route('/Registration', methods =["GET","POST"])
def Registration():

    if request.method == 'POST':
        # Capture form data
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        name = request.form['name']
        gender = request.form['gender']
        dob = request.form.get('dob')
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']

        # Get the current date and format it correctly (YYYY-MM-DD)
        current_date = datetime.now().strftime("%Y-%m-%d")  # Correct format for MySQL

        joining_date = request.form.get('joining_date', current_date)  # Use current_date if not provided

        # Convert joining_date to datetime object to ensure it's in the correct format
        try:
            joining_date = datetime.strptime(joining_date, "%Y-%m-%d")  # Ensure it's in YYYY-MM-DD format
        except ValueError:
            flash("Invalid date format.", "danger")
            return redirect(url_for('register'))

        # Call the function to save the user data
        create_user(username, password, role, name, gender, dob, phone, email, address, joining_date)

        flash("Employee registered successfully!", "success")
        return redirect(url_for('login'))

    # Display the current date (correct format) to the user in the template
    departments=get_department_salary()
    current_date = datetime.now().strftime("%Y-%m-%d")  # Correct format
    return render_template('Registration.html', date=current_date,departments=departments)


@app.route('/Hr_login', methods=['GET', 'POST'])
def Hr_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Call the modified check_employee function that uses bcrypt
        employee = check_employee(username, password)
        
        if employee:
            session['username'] = username
            session['role'] = employee[2]  # Assuming role is in the 3rd column (index 2)
            if employee[2] == 'HR':
                return redirect(url_for('admin'))
            else:
                flash('Invalid username or password. Please try again.', 'error')
        else:
            flash('Invalid credentials, please try again.', 'error')

    return render_template('Hr_login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Call the modified check_employee function that uses bcrypt
        employee = check_employee(username, password)

        if employee:
            session['username'] = username
            session['role'] = employee[2]  # Assuming role is in the 3rd column (index 2)
            return redirect(url_for('emp_dashboard'))  # HR user redirected to the admin page
        else:
            flash("invalid username or password")
    return render_template('login.html')

#forgot password========================
@app.route('/forget_password',methods=['GET', 'POST'])
def forget_password():
    if request.method == 'POST':
        email = request.form['email']
        user = get_user_by_email(email)

        if user:
            otp = generate_otp()
            session['otp'] = otp  # Store OTP in session
            session['email'] = email  # Store email in session
            
            # Send OTP email
            send_otp_email(email, otp)
            
            return redirect(url_for('verify'))
        else:
            flash("Email not found in our records."), 404  # Email not found in DB
    
    return render_template('forget_password.html')

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

# Send OTP email
def send_otp_email(to_email, otp):
    msg = Message("Your OTP for Email Verification", sender='your_email@gmail.com', recipients=[to_email])
    msg.body = f"Your OTP is {otp}. It will expire in 10 minutes."
    mail.send(msg)

@app.route('/verify',methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        
        if entered_otp == session.get('otp'):
            return redirect(url_for('change_pass'))
        else:
            return "Invalid OTP. Please try again."

    return render_template('verify.html')


@app.route('/change_pass', methods=['GET', 'POST'])
def change_pass():
    if request.method == 'POST':
        # Get the new password from the form
        username = request.form['username']
        new_password = request.form['new_password']
        
        # Call the change_password function from models.py to handle the database update
        change_password(username, new_password)

        # Redirect to login or another page after successful password change
        return redirect(url_for('login'))  # Replace 'login' with your actual endpoint

    return render_template('change_pass.html')

# Home page (After successful login)
@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/emp_dashboard')
def emp_dashboard():
    # Check if the user is logged in
    if 'username' in session:
        username = session['username']
        
        # Get employee data based on the logged-in username
        employee_data = get_employee_by_username(username)
        
        # If employee data is found, render the dashboard page with employee data
        if employee_data:
            return render_template('emp_dashboard.html', employee=employee_data)
        else:
            flash('No employee data found.')
            return redirect(url_for('login'))
    else:
        flash('Please log in to access the dashboard.')
        return redirect(url_for('login'))


@app.route('/all_employee', methods=['GET', 'POST'])
def all_employee():
    employees = None
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    if request.method == "POST":
        # Get the start and end dates from the form
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        # Ensure that the dates are valid
        if start_date and end_date:
            employees = get_all_employees(start_date, end_date)
            
            if not employees:
                flash('No employees found for the selected date range.', 'info')
        else:
            flash('Please select both start and end dates.', 'danger')
    
    else:
        # Default to showing all employees if no filtering is applied
        employees = get_all_employees()

    return render_template("all_employee.html", employees=employees, current_date=current_date)

@app.route('/employee/details/<int:employee_id>', methods=['GET'])
def view(employee_id):
    # Query the database for the employee's details
    employee = get_employee_by_id(employee_id)
    
    # Return a template with employee details
    return render_template('view.html', employee=employee)

@app.route('/employee/edit/<int:employee_id>', methods=['GET', 'POST'])
def edit(employee_id):
    # Get the employee details
    employee = get_employee_by_id(employee_id)
    
    if request.method == 'POST':
        # Get the form data
        name = request.form['name']
        gender = request.form['gender']
        dob = request.form['dob']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        username = request.form['username']
        role = request.form['role']
        joining_date = request.form['joining_date']

        # Update the employee details in the database
        update_employee(employee_id, name, gender, dob, phone, email, address, username, role, joining_date)
        
        # Redirect to the employee details page after the update
        return redirect(url_for('view', employee_id=employee_id))
    
    return render_template('edit.html', employee=employee)

@app.route('/delete_employee/<int:employee_id>', methods=['POST'])
def delete_employee_route(employee_id):
    delete_employee(employee_id)  # Call the function to delete the employee from the database
    return redirect(url_for('all_employee'))  # Redirect back to the list of employees after deletion


# Attendance form
@app.route('/add_attendance', methods=['GET', 'POST'])
def add_attendance():
    if 'username' in session:
        username = session['username']
        
        # Get employee data based on username
        employee_data = get_employee_by_username(username)
        
        if not employee_data:
            flash('No employee data found. Please contact admin.')
            return redirect(url_for('login'))  # Redirect to login if no employee data found
        
        # Check if the employee has already marked attendance in the last 12 hours
        last_attendance_time = get_last_attendance_time(username)
        
        if last_attendance_time:
            time_diff = datetime.now() - last_attendance_time
            if time_diff < timedelta(hours=10):
                # If the employee marked attendance in the last 12 hours, prevent further access
                flash('You have already marked your attendance. You can only mark attendance once every 10 hours.⏰')
                return redirect(url_for('emp_dashboard'))  # Redirect to employee dashboard or another page

        # If it's a POST request, process attendance submission
        if request.method == 'POST':
            date = request.form.get('date')
            status = request.form.get('status')
            employee_id = employee_data['id']  # Employee ID
            employee_name = employee_data['name']  # Employee Name

            submit_attendance(username, date, status, employee_id, employee_name)
            flash('Attendance marked successfully!✨')
            return render_template('add_attendance.html', employee=employee_data, date=datetime.now().strftime("%Y-%m-%d"))

        # If it's a GET request, render the attendance form
        else:
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return render_template('add_attendance.html', employee=employee_data, date=current_date)
    
    # If the user is not logged in, redirect to login page
    flash('You need to log in to mark attendance.')
    return redirect(url_for('login'))  # Redirect to login if not logged in

@app.route('/attendance_table', methods=['GET', 'POST'])
def attendance_table():
    month = datetime.now().month
    year = datetime.now().year
    start_date = None
    end_date = None
    attendance = []
    total_attendance = {}

    # Handling the change of month if the user selects it
    if request.method == 'POST':
        month = int(request.form.get('month'))
        year = int(request.form.get('year'))

    # Get the start and end dates for the selected month
    start_date = datetime(year, month, 1)
    # Determine the last day of the selected month
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)

    # Get all attendance records for the selected month
    attendance_records = get_attendance_by_employee(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    print(f"Attendance Records for the Month: {attendance_records}")  # Debug: print attendance records

    # Process the attendance records
    employee_attendance = {}

    for record in attendance_records:
        employee_name = record['employee_name']
        date = record['date']  # Ensure this is a datetime object
        status = record['status']

        # Initialize the employee data if not already
        if employee_name not in employee_attendance:
            employee_attendance[employee_name] = {day: 'None.' for day in range(1, end_date.day + 1)}

        day_of_month = date.day  # Get the day of the month correctly
        employee_attendance[employee_name][day_of_month] = status

        # Count total attendance for present days
        if status == "Present":
            if employee_name not in total_attendance:
                total_attendance[employee_name] = 0
            total_attendance[employee_name] += 1

    print(f"Processed Employee Attendance: {employee_attendance}")  # Debug: Check how the data is processed per employee

    # Prepare the table data
    table_data = []
    for employee, days in employee_attendance.items():
        row = {'employee_name': employee}
        for day in range(1, end_date.day + 1):
            row[day] = days.get(day, 'Absent')  # Default to 'Absent' if no record for the day
        row['total'] = total_attendance.get(employee, 0)  # Total attendance count
        table_data.append(row)

    print(f"Final Table Data: {table_data}")  # Debug: print final table data

    # Render the attendance table view
    return render_template("attendance_table.html", 
                           attendance=table_data, 
                           month=month, 
                           year=year, 
                           start_date=start_date,  # Pass as datetime object
                           end_date=end_date)

# Department registration form
@app.route('/department_register', methods=['GET', 'POST'])
def department_register():
    if request.method == 'POST':
        name = request.form['name']
        create_department(name)
        return redirect(url_for('admin'))
    return render_template('department_register.html')

@app.route('/delete_departments/<int:departments_id>', methods=['POST'])
def delete_departments_route(departments_id):
    delete__departments(departments_id)  # Call the function to delete the department from the database
    return redirect(url_for('department_List'))

@app.route('/department_List', methods=['GET'])
def department_List():
    departments =  get_all_department()
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template("department_List.html",departments =departments,current_date=current_date)

@app.route('/payroll', methods=['GET', 'POST'])
def payroll():
    if request.method == 'POST':
        # Extract data from form
        username = request.form['username']
        employee_id = request.form['employee_id']
        department = request.form['department']
        emp_name = request.form['emp_name']
        base_salary = float(request.form["base_salary"])
        bonus = float(request.form["bonus"])
        medical = float(request.form["medical"])
        conveyance = float(request.form["conveyance"])
        tax = float(request.form["tax"])
        pf = float(request.form["pf"])
        date = request.form.get('date')
        totalday = int(request.form["totalday"])
        Absent = int(request.form["Absent"])

         # Calculate net salary
        work_day = totalday - Absent
        per_day = base_salary/totalday
        sal=per_day*work_day
        net_salary = sal + bonus + medical + conveyance - tax - pf

        # Flash the net_salary to be displayed in the template
        flash(f'Net Salary: {net_salary}')
        
        save_salary(employee_id,department,emp_name,base_salary, bonus, medical, conveyance, tax,pf, net_salary,date,username,totalday,Absent,per_day)
        
        
        return redirect(url_for('salary_list'))
    
    employees =get_all_employee_salary()
    departments=get_department_salary()
    current_date = datetime.now().strftime("%Y-%m-%d")

    return render_template('payroll.html',employees=employees,departments=departments,date=current_date)

@app.route('/salary_list', methods=['GET'])
def salary_list():
    salary = get_all_salary_info()  # Retrieve salary data from the database
    return render_template("salary_list.html", salary=salary)

@app.route('/delete_salary/<int:employee_id>', methods=['POST'])
def delete_salary(employee_id):
    delete_salary_info(employee_id)  # Call the function to delete the salary record
    return redirect(url_for('salary_list'))  # Redirect to the salary list page after deletion

@app.route('/edit_salary/<int:employee_id>', methods=['GET', 'POST'])
def edit_salary(employee_id):
    # Fetch the current salary information using the employee_id
    salary = get_salary_info_by_id(employee_id)  # Fetch current salary info using employee_id

    if not salary:  # Check if the salary data was not found
        return "Salary data not found", 404

    if request.method == 'POST':
        # Get updated salary details from the form
        username = request.form['username']
        employee_id = request.form['employee_id']
        department = request.form['department']
        emp_name = request.form['emp_name']
        base_salary = float(request.form["base_salary"])
        bonus = float(request.form["bonus"])
        medical = float(request.form["medical"])
        conveyance = float(request.form["conveyance"])
        tax = float(request.form["tax"])
        pf = float(request.form["pf"])
        date = request.form.get('date')
        totalday = int(request.form["totalday"])
        Absent = int(request.form["Absent"])

         # Calculate net salary
        work_day = totalday - Absent
        per_day = base_salary/totalday
        sal=per_day*work_day
        net_salary = sal + bonus + medical + conveyance - tax - pf

        # Call update function with the new data, including the calculated values
        update_salary_info(employee_id,department,emp_name,base_salary, bonus, medical, conveyance, tax,pf, net_salary,date,username,totalday,Absent,per_day)

        return redirect(url_for('salary_list'))

    # If the request is GET, render the form to edit salary with current data
    return render_template('edit_salary.html', salary=salary)


@app.route('/search', methods=['GET','POST'])
def search():
    if request.method =='POST':

        employee = request.form['employee_id']
        
        employee = get_employee_for_payroll(employee)
    
        if employee:
            data = {
            "employee_id": employee['employee_id'],
            "name": employee['emp_name'],
            "designation": employee['department'],
            "date" : employee['date'],
            "base_salary": employee['base_salary'],
            "bonus" : employee['bonus'],
            "medical" : employee['medical'],
            "conveyance" : employee['conveyance'],
            "deductions": employee['tax'],
            "pf" : employee['pf'],
            "net_salary": employee['net_salary'],
            "totalday" : employee['totalday'],
            "Absent": employee['Absent'],
            "per_day": employee['per_day'],
            "username": employee['username'],
            }

            return render_template('salary_slip.html', data=data, employee=employee)
        else :   
                flash("Employee not found.")
      
    return render_template('search.html')
        
@app.route('/salary_slip',methods=['GET','POST'])
def salary_slip():
    return render_template('salary_slip.html')    

@app.route('/employee_slip', methods=['GET', 'POST'])
def employee_slip():
    if 'username' in session:
        username = session['username']
        
        # Get employee data from the model
        slip = get_employee_for_slip(username)
        
        # If data is found, render the dashboard page with employee data
        if slip:        
            return render_template('employee_slip.html', data=slip)
        else:
            flash('Payslip not Update or Calculated yet. Please contact HR.')
            return redirect(url_for('emp_dashboard'))
    else:
        flash('Please log in to access the dashboard.')
        return redirect(url_for('emp_dashboard'))

@app.route('/Feedback', methods=["GET", "POST"])
def Feedback():
    if 'username' in session:
        username = session['username']

        # Check if the form is being submitted (POST request)
        if request.method == 'POST':
            message = request.form.get('message')

            # Get employee data from the model
            employee_data = get_employee_by_username(username)

            # If employee data is found, save the feedback
            if employee_data:
                email = employee_data['email']
                
                save_feedback(username, email, message)
                flash('Thank you for your feedback! We appreciate your input.', 'success')
                return redirect(url_for('Feedback'))  # Redirect to avoid resubmission on refresh

        # For GET request, render the feedback page
        employee_data = get_employee_by_username(username)
        return render_template('Feedback.html', employee=employee_data)
    
    # If username not found in session, redirect to login page
    return redirect(url_for('login'))

@app.route('/feedback_tabel', methods=['GET', 'POST'])
def feedback_tabel():
    start_date = None
    end_date = None

    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        # Check if the dates are provided and in correct format
        try:
            if start_date and end_date:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

                # Check if start date is earlier than or equal to end date
                if start_date_obj > end_date_obj:
                    flash("Start date must be earlier than or equal to end date", 'error')
                else:
                    # Get feedback records between the two dates
                    feedback = get_Feedback_by_date_range(start_date_obj, end_date_obj)
                    return render_template("feedback_tabel.html", feedback=feedback, 
                                           current_date=datetime.now().strftime('%Y-%m-%d'), 
                                           start_date=start_date, end_date=end_date)
            else:
                flash("Both start date and end date are required", 'error')
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD format.", 'error')

    # Default view when no filter is applied
    feedback = get_Feedback()
    return render_template("feedback_tabel.html", feedback=feedback, 
                           current_date=datetime.now().strftime('%Y-%m-%d'),
                           start_date=start_date, end_date=end_date)

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/back')
def back():
    session.clear()
    return redirect(url_for('admin'))

@app.route('/close')
def close():
    session.clear()
    return redirect(url_for('reports'))

@app.route('/Close')
def Close():
    session.clear()
    return redirect(url_for('emp_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
