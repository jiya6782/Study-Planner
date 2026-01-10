
from datetime import date, timedelta, datetime
from streamlit_calendar import calendar
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pytz
import helper

LOCAL_TZ = pytz.timezone("America/New_York")





# Title
st.title("📚 Smart Study Planner")

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if not st.session_state.user_name:
    user_name = st.text_input("What's your name?", key="name_input")
    if user_name and user_name.strip():
        st.session_state.user_name = user_name.strip()
        save_data = {
            "user_name": st.session_state.user_name,
            "study_list": st.session_state.study_list
        }
        with open("tasks.json", "w") as file:
            json.dump(save_data, file)
        

# Show welcome if name exists
if st.session_state.user_name:
    st.subheader(f"Welcome, {st.session_state.user_name}!")
    

# Sidebar menu
st.sidebar.title("📚 Study Planner")
st.sidebar.info("✅ Add assignments, mark as studied, and track your progress here!")
st.sidebar.markdown("💡 Tip: Use negative days for overdue assignments.")
st.sidebar.write("Select an action: ")
st.sidebar.markdown("---")
option = st.sidebar.selectbox(
    "Menu",
    ["Add Assignment", "Edit Assignment", "Remove Assignment", "View Assignments", "Mark Complete", "Next Assignment", "Progress", "Assignment Calendar", "Clear Assignments"]
)

# -------------------- ADD TASK --------------------
if option == "Add Assignment":
    st.header("Add a Study Assignment")
    name = st.text_input("Assignment/Test Name")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    priority_num = {"Low":1, "Medium":2, "High":3}[priority]
    due_date = st.date_input("What is the date it's due? ", value=datetime.now(LOCAL_TZ).date())
    user_email = st.text_input("Your Email for reminders (leave blank if you don't want reminders)")
    user_email = user_email.strip()
    if user_email == "":
        user_email = None

    if st.button("Add Assignment"):
        st.session_state.study_list.append({
            "name": name,
            "priority": priority_num,
            "due_date": due_date.isoformat(),
            "done": False,
            "reminded": False,
            "user_email": user_email
        })
        st.success(f"Task '{name}' added!")
    with open("tasks.json", "w") as file:
        json.dump({
            "user_name": st.session_state.user_name,
            "study_list": st.session_state.study_list
        }, file)

# -------------------- REMOVE TASK --------------------
elif option == "Remove Assignment":
    st.header("Remove a Assignment")
    if not st.session_state.study_list:
        st.info("Your study list is empty!")
    else:
        formatted_list(st.session_state.study_list)
        remove_index = st.number_input(
            f"Which task to remove? (1-{len(st.session_state.study_list)})",
            min_value=1, max_value=len(st.session_state.study_list), step=1
        )
        if st.button("Remove Assignment"):
            removed = st.session_state.study_list.pop(remove_index-1)
            st.success(f"Removed Assignment: {removed['name']}")
        with open("tasks.json", "w") as file:
            json.dump({
                "user_name": st.session_state.user_name,
                "study_list": st.session_state.study_list
            }, file)

# -------------------- VIEW TASKS --------------------
elif option == "View Assignments":
    st.header("Your Study Plan")
    if not st.session_state.study_list:
        st.info("Your study list is empty!")
    else:
        sort_option = st.selectbox("Sort by", ["Unsorted", "Priority", "Due Date", "Summary"])
        if sort_option == "Summary":
            st.title("📚Study Plan Summary")
            st.write(f'Total Assignments: {len(st.session_state.study_list)}')
            st.write(f'Completed: {sum(1 for task in st.session_state.study_list if task["done"])}')
            st.write(f'Incomplete: {sum(1 for task in st.session_state.study_list if not task["done"])}')
            st.write(f'Due today: {sum(1 for task in st.session_state.study_list if days_until_due(task) == 0)}')
            st.write(f'Overdue: {sum(1 for task in st.session_state.study_list if days_until_due(task) < 0)}')
        else:
            if sort_option == "Priority":
                display_list = sorted(st.session_state.study_list, key=lambda t: t["priority"], reverse=True)
            elif sort_option == "Due Date":
                display_list = sorted(st.session_state.study_list, key=lambda t: t["due_date"])
            else:
                display_list = st.session_state.study_list
            formatted_list(display_list)

# -------------------- MARK COMPLETE --------------------
elif option == "Mark Complete":
    st.header("Mark a Task as Studied")
    if not st.session_state.study_list:
        st.info("Your study list is empty!")
    else:
        formatted_list(st.session_state.study_list)
        complete_index = st.number_input(
            f"Which assignment have you studied? (1-{len(st.session_state.study_list)})",
            min_value=1, max_value=len(st.session_state.study_list), step=1
        )
        if st.button("Mark as Studied"):
            st.session_state.study_list[complete_index-1]["done"] = True
            st.success(f"Marked '{st.session_state.study_list[complete_index-1]['name']}' as studied!")
        with open("tasks.json", "w") as file:
            json.dump({
                "user_name": st.session_state.user_name,
                "study_list": st.session_state.study_list
            }, file)

# -------------------- NEXT TASK --------------------
elif option == "Next Assignment":
    st.header("Next Assignment to Study")
    remaining = [task for task in st.session_state.study_list if not task["done"]]
    if not remaining:
        st.success("You have studied everything! 🎉")
    else:
        remaining.sort(key=lambda t: (-t["priority"], t["due_date"]))
        task = remaining[0]
        st.write(f"**You should study: {task['name']}**")
        st.write(f"- Priority: {priority_word(task['priority'])}")
        st.write(f"- Due in {days_until_due(task)} days")

# -------------------- PROGRESS --------------------
elif option == "Progress":
    st.header("Study Progress")
    total = len(st.session_state.study_list)
    completed = sum(task["done"] for task in st.session_state.study_list)
    if total == 0:
        st.write("You haven't added any tasks yet!")
    else:
        progress_fraction = completed / total
        st.write(f"You've completed {completed} out of {total} tasks ({progress_fraction * 100:.0f}%).")
        st.progress(progress_fraction)
# ---------------CLEAR TASKS---------------------
elif option == "Clear Assignments":
    if st.sidebar.button("Clear All Assignments"):
        st.session_state.study_list = []
        with open("tasks.json", "w") as file:
            json.dump({
                "user_name": st.session_state.user_name,
                "study_list": st.session_state.study_list
            }, file)
        st.success("All Assignments cleared!")
# ---------------TASK CALENDAR---------------------
elif option == "Assignment Calendar":
    st.header("📆 Assignment Calendar")
    calendar_events = [
        {
            "title" : task["name"],
            "start" : task["due_date"],
        }
        for task in st.session_state.study_list
    ]
    
    calendar_options = {
        "editable": False,
        "selectable": False,
        "initialView": "dayGridMonth",
        "headerToolBar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,dayGridWeek,dayGridDay",
        } 
    }
    calendar(
        events=calendar_events,
        options=calendar_options,
        key="study_calendar"
    )
elif option == "Edit Assignment":
    st.header("Edit a Assignment")
    if not st.session_state.study_list:
        st.info("Your study list is empty!")
    else:
        formatted_list(st.session_state.study_list)
        edit_index = st.number_input(
            f"Which assignment would you like to edit? (1-{len(st.session_state.study_list)})",
            min_value=1, max_value=len(st.session_state.study_list), step=1
        )
        
        task = st.session_state.study_list[edit_index - 1]
        change_option = st.selectbox("Edit assignment options", ["Name", "Priority", "Due Date", "Email"])
        if change_option == "Name":
            new_name = st.text_input("Assignment/Test Name", value=task["name"])
            if st.button("Save", key="save_name"):
                if new_name.strip():
                    task["name"] = new_name
                    with open("tasks.json", "w") as file:
                        json.dump({
                            "user_name": st.session_state.user_name,
                            "study_list": st.session_state.study_list
                        }, file)
                st.success("Assignment updated!")
        
        elif change_option == "Priority":
            priority_labels = ["Low", "Medium", "High"]
            current_priority = priority_labels[task["priority"] - 1]
            new_priority = st.selectbox("Priority", priority_labels, index=priority_labels.index(current_priority))
            if st.button("Save", key="save_priority"):
                task["priority"] = priority_labels.index(new_priority) + 1
                with open("tasks.json", "w") as file:
                        json.dump({
                            "user_name": st.session_state.user_name,
                            "study_list": st.session_state.study_list
                        }, file)
                st.success("Assignment updated!")

        elif change_option == "Due Date":
            new_due_date = st.date_input("What is the date it's due? ", value=datetime.strptime(task["due_date"], "%Y-%m-%d").date())
            if st.button("Save", key="save_due"):
                task["due_date"] = new_due_date.isoformat()
                with open("tasks.json", "w") as file:
                        json.dump({
                            "user_name": st.session_state.user_name,
                            "study_list": st.session_state.study_list
                        }, file)
                st.success("Assignment updated!")
                
        elif change_option == "Email":
            current_email = task.get("user_email") or ""
            new_email = st.text_input("Your Email for reminders (leave blank if you don't want reminders)")
            new_email = new_email.strip()
            if new_email == "":
                new_email = None
            if st.button("Save", key="save_email"):
                if new_email != task.get("user_email"):
                    task["user_email"] = new_email
                    task["reminded"] = False
                with open("tasks.json", "w") as file:
                        json.dump({
                            "user_name": st.session_state.user_name,
                            "study_list": st.session_state.study_list
                        }, file)
                st.success("Email updated!")
            else:
                st.info("Email unchanged")





