import streamlit as st

# Initialize the study list in session_state
if "study_list" not in st.session_state:
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
        if task["due_days"] == 0:
            due_msg = "DUE TODAY ⚠️"
        elif task["due_days"] < 0:
            due_msg = "OVERDUE ❗"
        else:
            due_msg = f'Due in {task["due_days"]} days'

        st.write(f"**{i}. {task['name']}**")
        st.write(f"- Priority: {priority_word(task['priority'])}")
        st.write(f"- {due_msg}")
        st.write(f"- Status: {status}")
        st.write("---")

# Title
st.title("📚 Smart Study Planner")

# Sidebar menu
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
    due_days = st.number_input("Days until due", min_value=0, value=0, step=1)

    if st.button("Add Task"):
        st.session_state.study_list.append({
            "name": name,
            "priority": priority_num,
            "due_days": due_days,
            "done": False
        })
        st.success(f"Task '{name}' added!")

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

# -------------------- VIEW TASKS --------------------
elif option == "View Tasks":
    st.header("Your Study Plan")
    if not st.session_state.study_list:
        st.info("Your study list is empty!")
    else:
        sort_option = st.selectbox("Sort by", ["Unsorted", "Priority", "Due Date"])
        if sort_option == "Priority":
            display_list = sorted(st.session_state.study_list, key=lambda t: t["priority"], reverse=True)
        elif sort_option == "Due Date":
            display_list = sorted(st.session_state.study_list, key=lambda t: t["due_days"])
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

# -------------------- NEXT TASK --------------------
elif option == "Next Task":
    st.header("Next Task to Study")
    remaining = [task for task in st.session_state.study_list if not task["done"]]
    if not remaining:
        st.success("You have studied everything! 🎉")
    else:
        remaining.sort(key=lambda t: (-t["priority"], t["due_days"]))
        task = remaining[0]
        st.write(f"**You should study: {task['name']}**")
        st.write(f"- Priority: {priority_word(task['priority'])}")
        st.write(f"- Due in {task['due_days']} days")

# -------------------- PROGRESS --------------------
elif option == "Progress":
    st.header("Study Progress")
    total = len(st.session_state.study_list)
    completed = sum(task["done"] for task in st.session_state.study_list)
    if total == 0:
        st.info("You haven't added any tasks yet!")
    else:
        st.write(f"You've completed {completed} out of {total} tasks.")
