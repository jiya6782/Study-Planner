TASK_FILE = "tasks.json"

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
