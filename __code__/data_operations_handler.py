import sqlite3

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
    threadname TEXT,
    short_description TEXT,
    description LONGTEXT,
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


last_thread_id = 0


def generate_thread_id():
    global last_thread_id
    last_thread_id += 1
    return last_thread_id + 1


def check_for_unique_threadname(threadname):
    return cur.execute("SELECT * FROM threads WHERE threadname=?", (threadname,)).fetchone() is None


def add_thread_to_db(thread_id, threadname, short_description):
    cur.execute("INSERT INTO threads (id, threadname, short_description, messages) VALUES (?,?,?,?)", (int(thread_id), threadname, short_description, 0))
    conn.commit()


def add_thread_description(threadname, description):
    cur.execute("INSERT INTO threads (description) VALUES (?) WHERE threadname=?", (description, threadname))
    conn.commit()
