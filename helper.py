import streamlit as st
TASK_FILE = "tasks.json"
# Initialize the study list in session_state
if "study_list" not in st.session_state:
    if os.path.exists("tasks.json"):
        with open("tasks.json", mode="r") as file:
            data = json.load(file)
            st.session_state.study_list = data.get("study_list")
            st.session_state.user_name = data.get("user_name")
            
    else:
        st.session_state.study_list = []
        st.session_state.user_name = ""
    
for task in st.session_state.study_list:
    if "reminded" not in task:
        task["reminded"] = False
def load_data():
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, "r") as f:
            data = json.load(f)
            return data.get("study_list", []), data.get("user_name", "")
    return [], ""

def save_data():
    with open(TASK_FILE, "w") as f:
        json.dump({
            "user_name": st.session_state.user_name,
            "study_list": st.session_state.study_list
        }, f)
def priority_word(priority):
    if priority == 3:
        return "High"
    elif priority == 2:
        return "Medium"
    else:
        return "Low"

def formatted_list(list_to_print):
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

def days_until_due(task):
    due = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
    today = datetime.now(LOCAL_TZ).date()
    return (due - today).days

def send_email_reminder(to_email, task_name, due_date):
    sender_email = st.secrets["email"]["user"]
    sender_password = st.secrets["email"]["password"]
    msg = MIMEMultipart()
    msg["From"] = "📚 Study Plan Reminder <{}>".format(sender_email)
    msg["To"] = to_email
    msg["Subject"] = f'Reminder: {task_name} due soon!'
    body = f'''
Hi!
This is a reminder that your assignment:
{task_name}
Due date: {due_date}

Good luck studying! 💪
    '''
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f'Email failed: {e}')
        return False

for task in st.session_state.study_list:
    email = task.get("user_email")
    if not email:
        continue
        
    if (not task["reminded"]) and (days_until_due(task) == 1) and (not task["done"]):
        email_sent = send_email_reminder(task["user_email"], task["name"], task["due_date"])

        if email_sent:
            st.toast(f'📧 Email reminder sent for {task["name"]}')
            task["reminded"] = True
            with open("tasks.json", "w") as file:
                json.dump(st.session_state.study_list, file)
