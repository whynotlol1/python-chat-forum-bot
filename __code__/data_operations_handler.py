# (c) cat dev 2023

import sqlite3
import json

conn = sqlite3.connect("__misc__/data.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users 
(
    user_id INTEGER,
    username LONGTEXT,
    password LONGTEXT,
    is_logged_in BOOLEAN
)
""")
conn.commit()

cur.execute("""
CREATE TABLE IF NOT EXISTS threads
(
    id INTEGER,
    author_id INTEGER,
    threadname TEXT,
    description TEXT
)
""")
conn.commit()


def check_user_login(user_id):
    check = cur.execute("SELECT * FROM users WHERE user_id=?", (int(user_id),)).fetchone()
    if check is not None:
        if check[3] != 0:
            return [True, check[1]]
        else:
            return [False, check[1]]
    else:
        return [False, None]


def get_data(user_id, data):
    user = cur.execute("SELECT * FROM users WHERE user_id=?", (int(user_id),)).fetchone()
    match data:
        case "username":
            return user[1]
        case "password":
            return user[2]


def set_user_login(user_id, login_status):
    if login_status:
        cur.execute("UPDATE users SET is_logged_in=? WHERE user_id=?", (1, int(user_id)))
    else:
        cur.execute("UPDATE users SET is_logged_in=? WHERE user_id=?", (0, int(user_id)))


def check_for_unique_username(username):
    return cur.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone() is None


def create_new_user(user_id, username, password):
    cur.execute("INSERT INTO users VALUES (?,?,?,?)", (int(user_id), username, password, 1))
    conn.commit()


def delete_account_from_db(user_id):
    cur.execute("DELETE FROM users WHERE user_id=?", (int(user_id),))
    conn.commit()


last_thread_id = 0


def generate_thread_id():
    global last_thread_id
    last_thread_id += 1
    return last_thread_id


def check_for_unique_threadname(threadname):
    return cur.execute("SELECT * FROM threads WHERE threadname=?", (threadname,)).fetchone() is None


def add_thread(thread_id, user_id, threadname, description):
    cur.execute("INSERT INTO threads VALUES (?,?,?,?)", (int(thread_id), int(user_id), threadname, description))
    conn.commit()
    add_thread_to_list(thread_id, user_id, threadname, description)


def add_thread_to_list(thread_id, user_id, threadname, description):
    thread_json = {
        "global_info": {
            "id": thread_id,
            "auth": user_id,
            "name": threadname,
            "desc": description
        },
        "messages": [],
        "subbed_by": []
    }
    file_path = f"__misc__/_threads_/{threadname}.json"
    with open(file_path, "w") as output:
        json.dump(thread_json, output)


def get_threads_list():
    return cur.execute("SELECT * FROM threads").fetchall()


def parse_thread(threadname):
    file_path = f"__misc__/_threads_/{threadname}.json"
    with open(file_path, "r") as output:
        return json.loads(output.read())


def write_to(threadname, user_id, message_text):
    username = get_data(user_id, "username")
    thread = parse_thread(threadname)
    thread["messages"].append([username, message_text])
    file_path = f"__misc__/_threads_/{threadname}.json"
    with open(file_path, "w") as output:
        output.write(json.dumps(thread))
    thread = parse_thread(threadname)
    ids_returned = []
    for username in thread["subbed_by"]:
        user_id = cur.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()[0]
        ids_returned.append(user_id)
    return ids_returned


def sub_to_thread(user_id, threadname):
    username = get_data(user_id, "username")
    thread = parse_thread(threadname)
    if username not in thread["subbed_by"]:
        thread["subbed_by"].append(username)
        file_path = f"__misc__/_threads_/{threadname}.json"
        with open(file_path, "w") as output:
            output.write(json.dumps(thread))


def unsub_from_thread(user_id, threadname):
    username = get_data(user_id, "username")
    thread = parse_thread(threadname)
    if username in thread["subbed_by"]:
        del thread["subbed_by"][thread["subbed_by"].index(username)]
        file_path = f"__misc__/_threads_/{threadname}.json"
        with open(file_path, "w") as output:
            output.write(json.dumps(thread))
