import streamlit as st
import json
import os
from datetime import date, timedelta, datetime
import smtplib
from email.mime.text import MIMEText
import pytz

# Set local timezone
LOCAL_TZ = pytz.timezone("America/New_York")

# -------------------- SESSION STATE INITIALIZATION --------------------
# Initialize study list and user name in session state if not already present
if "study_list" not in st.session_state:
    st.session_state.study_list = []
    st.session_state.user_name = ""

    # Load existing tasks from tasks.json if it exists
    if os.path.exists("tasks.json"):
        try:
            with open("tasks.json", "r") as file:
                data = json.load(file)
                st.session_state.study_list = data.get("study_list", [])
                st.session_state.user_name = data.get("user_name", "")
        except json.JSONDecodeError:
            # If the file exists but is corrupted, reset data
            st.warning("tasks.json was corrupted. Resetting data.")
            st.session_state.study_list = []
            st.session_state.user_name = ""
    
# Ensure all tasks have a 'reminded' key
for task in st.session_state.study_list:
    if "reminded" not in task:
        task["reminded"] = False

def save_data():
    try: 
        with open(TASK_FILE, "w") as f:
            json.dump({
                "user_name": st.session_state.user_name,
                "study_list": st.session_state.study_list
            }, f)
    except Exception as e:
        st.error(f'Failed to save data: {e}')

# -------------------- HELPER FUNCTIONS --------------------
def priority_word(priority):
    """
    Converts numeric priority (1-3) to a string representation ("Low", "Medium", "High").
    """
    if priority == 3:
        return "High"
    elif priority == 2:
        return "Medium"
    else:
        return "Low"


def days_until_due(task):
    """
    Returns the number of days until a task is due.
    Positive if due in future, 0 if due today, negative if overdue.
    """
    due = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
    today = datetime.now(LOCAL_TZ).date()
    return (due - today).days


def formatted_list(list_to_print):
    """
    Displays a formatted list of tasks with their:
    - Name
    - Priority
    - Due date status (due today, overdue, or days left)
    - Completion status
    - Associated email (if any)
    """
    for i, task in enumerate(list_to_print, 1):
        status = "Studied" if task["done"] else "Not studied"
        if days_until_due(task) == 0:
            due_msg = "DUE TODAY ⚠️"
        elif days_until_due(task) < 0:
            due_msg = "OVERDUE ❗"
        else:
            due_msg = f'Due in {days_until_due(task)} days'

        st.write(f"**{i}. {task['name']}**")
        st.write(f"- Priority: {priority_word(task['priority'])}")
        st.write(f"- {due_msg}")
        st.write(f"- Status: {status}")
        if task.get("user_email"):
            st.write(f'Email: {task["user_email"]}')
        st.write("---")


def send_email_reminder(to_email, task_name, due_date):
    """
    Sends an email reminder for a task due tomorrow.
    Uses email credentials stored in Streamlit secrets.
    Returns True if email sent successfully, False otherwise.
    """
    sender_email = st.secrets["email"]["user"]
    sender_password = st.secrets["email"]["password"]

    # Create the email message using MIMEText
    body = f'''
Hi!
This is a reminder that your assignment:
{task_name}
Due date: {due_date}

Good luck studying! 💪
    '''
    msg = MIMEText(body, "plain")
    msg["From"] = f"📚 Study Plan Reminder <{sender_email}>"
    msg["To"] = to_email
    msg["Subject"] = f"Reminder: {task_name} due soon!"

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f'Email failed: {e}')
        return False

