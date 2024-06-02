import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
import os

# Connect to MySQL Database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="nandhu@171220",
    database="od_management"
)
cursor = db.cursor()

# Tkinter Window Setup 
root = tk.Tk()
root.geometry("800x600")
root.title("OD Management System")

# Login Frame
login_frame = tk.Frame(root)
login_frame.pack()

tk.Label(login_frame, text="Username").grid(row=0, column=0)
tk.Label(login_frame, text="Password").grid(row=1, column=0)
tk.Label(login_frame, text="Department").grid(row=2, column=0)

username_entry = tk.Entry(login_frame)
password_entry = tk.Entry(login_frame, show="*")
department_entry = tk.Entry(login_frame)

username_entry.grid(row=0, column=1)
password_entry.grid(row=1, column=1)
department_entry.grid(row=2, column=1)

def login():
    username = username_entry.get()
    password = password_entry.get()
    department = department_entry.get()
    
    cursor.execute("SELECT user_id, role FROM users WHERE username=%s AND password=%s AND department=%s",
                   (username, password, department))
    result = cursor.fetchone()
    if result:
        user_id, role = result
        login_frame.pack_forget()
        if role == 'student':
            student_dashboard(user_id)
        elif role == 'faculty':
            faculty_dashboard(department)
        elif role == 'hod':
            hod_dashboard(department)
        elif role == 'warden':
            warden_dashboard()
    else:
        messagebox.showerror("Login Failed", "Invalid credentials")

tk.Button(login_frame, text="Login", command=login, bg='yellow').grid(row=3, column=0, columnspan=2)

# Student Dashboard
def student_dashboard(user_id):
    student_frame = tk.Frame(root)
    student_frame.pack()
    
    tk.Label(student_frame, text="Name").grid(row=0, column=0)
    tk.Label(student_frame, text="Department").grid(row=1, column=0)
    tk.Label(student_frame, text="Register No").grid(row=2, column=0)
    tk.Label(student_frame, text="Day Scholar").grid(row=3, column=0)
    tk.Label(student_frame, text="Attendance").grid(row=4, column=0)
    tk.Label(student_frame, text="Reason for OD").grid(row=5, column=0)
    tk.Label(student_frame, text="Upload Proof").grid(row=6, column=0)
    tk.Label(student_frame, text="OD Date").grid(row=7, column=0)
    
    name_entry = tk.Entry(student_frame)
    department_entry = tk.Entry(student_frame)
    register_no_entry = tk.Entry(student_frame)
    day_scholar_var = tk.IntVar()
    day_scholar_check = tk.Checkbutton(student_frame, variable=day_scholar_var)
    attendance_entry = tk.Entry(student_frame)
    reason_text = tk.Text(student_frame, height=1, width=15)
    proof_path_entry = tk.Entry(student_frame, state='readonly')
    od_date_entry = tk.Entry(student_frame)

    name_entry.grid(row=0, column=1)
    department_entry.grid(row=1, column=1)
    register_no_entry.grid(row=2, column=1)
    day_scholar_check.grid(row=3, column=1)
    attendance_entry.grid(row=4, column=1)
    reason_text.grid(row=5, column=1)
    proof_path_entry.grid(row=6, column=1)
    od_date_entry.grid(row=7, column=1)

    def upload_proof():
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            proof_path_entry.config(state='normal')
            proof_path_entry.delete(0, tk.END)
            proof_path_entry.insert(0, file_path)
            proof_path_entry.config(state='readonly')

    tk.Button(student_frame, text="Browse", command=upload_proof).grid(row=6, column=2)
    
    def submit_request():
        name = name_entry.get()
        department = department_entry.get()
        register_no = register_no_entry.get()
        day_scholar = day_scholar_var.get()
        attendance = float(attendance_entry.get())
        reason = reason_text.get("1.0", tk.END).strip()
        proof_path = proof_path_entry.get()
        od_date = od_date_entry.get()

        if not all([name, department, register_no, reason, proof_path, od_date]):
            messagebox.showerror("Error", "All fields are required")
            return

        cursor.execute("INSERT INTO students (user_id, name, department, register_no, day_scholar, attendance) VALUES (%s, %s, %s, %s, %s, %s)",
                       (user_id, name, department, register_no, day_scholar, attendance))
        student_id = cursor.lastrowid
        cursor.execute("INSERT INTO od_requests (student_id, reason, proof_path, od_date) VALUES (%s, %s, %s, %s)", (student_id, reason, proof_path, od_date))
        db.commit()
        messagebox.showinfo("Success", "Request Submitted")

    tk.Button(student_frame, text="Submit", command=submit_request,bg="yellow").grid(row=8, column=0, columnspan=2)

    # Status Check Section
    def check_status():
        cursor.execute("""
            SELECT od_requests.reason, od_requests.status, od_requests.od_date
            FROM od_requests
            JOIN students ON od_requests.student_id = students.student_id
            WHERE students.user_id = %s
        """, (user_id,))
        
        requests = cursor.fetchall()
        
        status_window = tk.Toplevel(student_frame)
        status_window.title("Request Status")
        status_window.geometry("200x200")
        for idx, request in enumerate(requests):
            reason, status, od_date = request
            tk.Label(status_window, text=f"Request: {reason[:50]}...").grid(row=idx, column=0)
            tk.Label(status_window, text=f"Status: {status}").grid(row=idx, column=1)
            tk.Label(status_window, text=f"OD Date: {od_date}").grid(row=idx, column=2)
    
    tk.Button(student_frame, text="Check Request Status", command=check_status,bg="yellow").grid(row=9, column=0, columnspan=2)

# Faculty Dashboard
def faculty_dashboard(department):
    faculty_frame = tk.Frame(root)
    faculty_frame.pack()

    tk.Label(faculty_frame, text="Pending Requests").pack()

    pending_tree = ttk.Treeview(faculty_frame, columns=('Name', 'Department', 'Register No', 'Day Scholar', 'Attendance', 'Reason', 'OD Date', 'Status'))
    pending_tree.heading('#0', text='Request ID')
    pending_tree.heading('Name', text='Name')
    pending_tree.heading('Department', text='Department')
    pending_tree.heading('Register No', text='Register No')
    pending_tree.heading('Day Scholar', text='Day Scholar')
    pending_tree.heading('Attendance', text='Attendance')
    pending_tree.heading('Reason', text='Reason')
    pending_tree.heading('OD Date', text='OD Date')
    pending_tree.heading('Status', text='Status')
    pending_tree.pack(expand=True, fill='both')

    tk.Label(faculty_frame, text="Approved Requests").pack()

    approved_tree = ttk.Treeview(faculty_frame, columns=('Name', 'Department', 'Register No', 'Day Scholar', 'Attendance', 'Reason', 'OD Date', 'Status'))
    approved_tree.heading('#0', text='Request ID')
    approved_tree.heading('Name', text='Name')
    approved_tree.heading('Department', text='Department')
    approved_tree.heading('Register No', text='Register No')
    approved_tree.heading('Day Scholar', text='Day Scholar')
    approved_tree.heading('Attendance', text='Attendance')
    approved_tree.heading('Reason', text='Reason')
    approved_tree.heading('OD Date', text='OD Date')
    approved_tree.heading('Status', text='Status')
    approved_tree.pack(expand=True, fill='both')

    cursor.execute("""
        SELECT od_requests.request_id, students.name, students.department, students.register_no, students.day_scholar, students.attendance, od_requests.reason, od_requests.od_date, od_requests.status
        FROM od_requests
        JOIN students ON od_requests.student_id = students.student_id
        WHERE students.department = %s AND (od_requests.status = 'pending' OR od_requests.status = 'approved_by_faculty')
    """, (department,))
    requests = cursor.fetchall()

    for request in requests:
        if request[-1] == 'pending':
            pending_tree.insert('', 'end', text=request[0], values=request[1:])
        else:
            approved_tree.insert('', 'end', text=request[0], values=request[1:])

    def approve_request():
        selected_item = pending_tree.selection()
        if selected_item:
            request_id = pending_tree.item(selected_item, 'text')
            cursor.execute("UPDATE od_requests SET status='approved_by_faculty' WHERE request_id=%s", (request_id,))
            db.commit()
            messagebox.showinfo("Success", "Request Approved")
            values = pending_tree.item(selected_item, 'values')
            approved_tree.insert('', 'end', text=request_id, values=values)
            pending_tree.delete(selected_item)
        else:
            messagebox.showwarning("No Selection", "Please select a request to approve.")

    def reject_request():
        selected_item = pending_tree.selection()
        if selected_item:
            request_id = pending_tree.item(selected_item, 'text')
            cursor.execute("UPDATE od_requests SET status='rejected' WHERE request_id=%s", (request_id,))
            db.commit()
            messagebox.showinfo("Success", "Request Rejected")
            pending_tree.delete(selected_item)
        else:
            messagebox.showwarning("No Selection", "Please select a request to reject.")

    tk.Button(faculty_frame, text="Approve", command=approve_request).pack()
    tk.Button(faculty_frame, text="Reject", command=reject_request).pack()

# HOD Dashboard
def hod_dashboard(department):
    hod_frame = tk.Frame(root)
    hod_frame.pack()

    tk.Label(hod_frame, text="Requests to Approve").pack()

    pending_tree = ttk.Treeview(hod_frame, columns=('Name', 'Department', 'Register No', 'Day Scholar', 'Attendance', 'Reason', 'OD Date', 'Status'))
    pending_tree.heading('#0', text='Request ID')
    pending_tree.heading('Name', text='Name')
    pending_tree.heading('Department', text='Department')
    pending_tree.heading('Register No', text='Register No')
    pending_tree.heading('Day Scholar', text='Day Scholar')
    pending_tree.heading('Attendance', text='Attendance')
    pending_tree.heading('Reason', text='Reason')
    pending_tree.heading('OD Date', text='OD Date')
    pending_tree.heading('Status', text='Status')
    pending_tree.pack(expand=True, fill='both')

    tk.Label(hod_frame, text="Approved Requests").pack()

    approved_tree = ttk.Treeview(hod_frame, columns=('Name', 'Department', 'Register No', 'Day Scholar', 'Attendance', 'Reason', 'OD Date', 'Status'))
    approved_tree.heading('#0', text='Request ID')
    approved_tree.heading('Name', text='Name')
    approved_tree.heading('Department', text='Department')
    approved_tree.heading('Register No', text='Register No')
    approved_tree.heading('Day Scholar', text='Day Scholar')
    approved_tree.heading('Attendance', text='Attendance')
    approved_tree.heading('Reason', text='Reason')
    approved_tree.heading('OD Date', text='OD Date')
    approved_tree.heading('Status', text='Status')
    approved_tree.pack(expand=True, fill='both')

    cursor.execute("""
        SELECT od_requests.request_id, students.name, students.department, students.register_no, students.day_scholar, students.attendance, od_requests.reason, od_requests.od_date, od_requests.status
        FROM od_requests
        JOIN students ON od_requests.student_id = students.student_id
        WHERE students.department = %s AND (od_requests.status = 'approved_by_faculty' OR od_requests.status = 'approved_by_hod')
    """, (department,))

    requests = cursor.fetchall()

    for request in requests:
        if request[-1] == 'approved_by_faculty':
            pending_tree.insert('', 'end', text=request[0], values=request[1:])
        else:
            approved_tree.insert('', 'end', text=request[0], values=request[1:])

    def approve_request():
        selected_item = pending_tree.selection()
        if selected_item:
            request_id = pending_tree.item(selected_item, 'text')
            cursor.execute("UPDATE od_requests SET status='approved_by_hod' WHERE request_id=%s", (request_id,))
            db.commit()
            messagebox.showinfo("Success", "Request Approved")
            values = pending_tree.item(selected_item, 'values')
            approved_tree.insert('', 'end', text=request_id, values=values)
            pending_tree.delete(selected_item)
        else:
            messagebox.showwarning("No Selection", "Please select a request to approve.")

    def reject_request():
        selected_item = pending_tree.selection()
        if selected_item:
            request_id = pending_tree.item(selected_item, 'text')
            cursor.execute("UPDATE od_requests SET status='rejected' WHERE request_id=%s", (request_id,))
            db.commit()
            messagebox.showinfo("Success", "Request Rejected")
            pending_tree.delete(selected_item)
        else:
            messagebox.showwarning("No Selection", "Please select a request to reject.")

    tk.Button(hod_frame, text="Approve", command=approve_request).pack()
    tk.Button(hod_frame, text="Reject", command=reject_request).pack()

# Warden Dashboard
def warden_dashboard():
    warden_frame = tk.Frame(root)
    warden_frame.pack()

    tk.Label(warden_frame, text="Approved Requests").pack()

    tree = ttk.Treeview(warden_frame, columns=('Name', 'Department', 'Register No', 'Day Scholar', 'Attendance', 'Reason', 'OD Date', 'Status'))
    tree.heading('#0', text='Request ID')
    tree.heading('Name', text='Name')
    tree.heading('Department', text='Department')
    tree.heading('Register No', text='Register No')
    tree.heading('Day Scholar', text='Day Scholar')
    tree.heading('Attendance', text='Attendance')
    tree.heading('Reason', text='Reason')
    tree.heading('OD Date', text='OD Date')
    tree.heading('Status', text='Status')
    tree.pack(expand=True, fill='both')

    cursor.execute("""
        SELECT od_requests.request_id, students.name, students.department, students.register_no, students.day_scholar, students.attendance, od_requests.reason, od_requests.od_date, od_requests.status
        FROM od_requests
        JOIN students ON od_requests.student_id = students.student_id
        WHERE od_requests.status = 'approved_by_hod' AND students.day_scholar = 0
    """)

    requests = cursor.fetchall()

    for request in requests:
        tree.insert('', 'end', text=request[0], values=request[1:])


root.mainloop()
