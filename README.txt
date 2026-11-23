CAMPUS CONNECT - ROLL NUMBER LOGIN DEMO

This fictional classroom project uses a username/email and college roll number.
It does not ask for or collect a password.

Windows setup:
1. Extract the ZIP and open the folder in VS Code.
2. In Terminal run:
   py -m venv venv
   venv\Scripts\activate
   py -m pip install -r requirements.txt
   py app.py
3. Open http://127.0.0.1:5000
4. Create a demo account, then log in with its username/email and roll number.
5. Admin dashboard: http://127.0.0.1:5000/admin
   Default local demo admin password: admin123-change-me

The dashboard displays the submitted demo username/email, roll number, login result,
and timestamp. Use fictional details or get permission before recording classmates'
identifying information. Do not ask anyone for their real account password.

The database campus_demo.db is created automatically on first run.
