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
    description TEXT,
    messages INTEGER
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
    cur.execute("INSERT INTO threads VALUES (?,?,?,?,?)", (int(thread_id), int(user_id), threadname, description, 0))
    conn.commit()
    add_thread_to_list(thread_id, user_id, threadname, description)


def add_thread_to_list(user_id, thread_id, threadname, description):
    thread_json = {
        "global_info": {
            "id": thread_id,
            "auth": user_id,
            "name": threadname,
            "desc": description
        },
        "messages": {
            "": ""
        }
    }
    with open(f"__misc__/_threads_/{threadname}.json", "w") as output:
        json.dump(thread_json, output)


def get_threads_list():
    return cur.execute("SELECT * FROM threads").fetchall()
