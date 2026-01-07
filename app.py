import streamlit as st
import json
import os
from datetime import date, timedelta, datetime


# Initialize the study list in session_state
if "study_list" not in st.session_state:
    if os.path.exists("tasks.json"):
        with open("tasks.json", mode="r") as file:
            st.session_state.study_list = json.load(file)
    else:
        st.session_state.study_list = []
    

# Helper functions
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
        st.write("---")

def days_until_due(task):
    due = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
    return (due - date.today()).days
    
# Title
st.title("📚 Smart Study Planner")

# Sidebar menu
st.sidebar.title("📚 Study Planner")
st.sidebar.info("✅ Add tasks, mark as studied, and track your progress here!")
st.sidebar.markdown("💡 Tip: Use negative days for overdue tasks.")
st.sidebar.write("Select an action: ")
st.sidebar.markdown("---")
option = st.sidebar.selectbox(
    "Menu",
    ["Add Task", "Remove Task", "View Tasks", "Mark Complete", "Next Task", "Progress"]
)

# -------------------- ADD TASK --------------------
if option == "Add Task":
    st.header("Add a Study Task")
    name = st.text_input("Assignment/Test Name")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    priority_num = {"Low":1, "Medium":2, "High":3}[priority]
    due_date = st.date_input("What is the date it's due? ", value=date.today())

    if st.button("Add Task"):
        st.session_state.study_list.append({
            "name": name,
            "priority": priority_num,
            "due_date": due_date.isoformat(),
            "done": False
        })
        st.success(f"Task '{name}' added!")
    with open("tasks.json", mode="w") as file:
        json.dump(st.session_state.study_list, file)

# -------------------- REMOVE TASK --------------------
elif option == "Remove Task":
    st.header("Remove a Task")
    if not st.session_state.study_list:
        st.info("Your study list is empty!")
    else:
        formatted_list(st.session_state.study_list)
        remove_index = st.number_input(
            f"Which task to remove? (1-{len(st.session_state.study_list)})",
            min_value=1, max_value=len(st.session_state.study_list), step=1
        )
        if st.button("Remove Task"):
            removed = st.session_state.study_list.pop(remove_index-1)
            st.success(f"Removed task: {removed['name']}")
        with open("tasks.json", mode="w") as file:
            json.dump(st.session_state.study_list, file)

# -------------------- VIEW TASKS --------------------
elif option == "View Tasks":
    st.header("Your Study Plan")
    if not st.session_state.study_list:
        st.info("Your study list is empty!")
    else:
        sort_option = st.selectbox("Sort by", ["Unsorted", "Priority", "Due Date", "Summary"])
        if sort_option == "Summary":
            st.title("📚Study Plan Summary")
            st.write(f'Total tasks: {len(st.session_state.study_list)}')
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
            f"Which task have you studied? (1-{len(st.session_state.study_list)})",
            min_value=1, max_value=len(st.session_state.study_list), step=1
        )
        if st.button("Mark as Studied"):
            st.session_state.study_list[complete_index-1]["done"] = True
            st.success(f"Marked '{st.session_state.study_list[complete_index-1]['name']}' as studied!")
        with open("tasks.json", mode="w") as file:
            json.dump(st.session_state.study_list, file)

# -------------------- NEXT TASK --------------------
elif option == "Next Task":
    st.header("Next Task to Study")
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





