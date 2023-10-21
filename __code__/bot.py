from __code__.data_operations_handler import *
from telebot import TeleBot, types

with open("__misc__/_bot_token_.txt", "r") as f:
    bot = TeleBot(f.read())

commands_list = {
    "Account": [
        ["/logout", "Log out of your account"],
        ["/delete_account", "Delete your account"]
    ],
    "General": [
        ["/help", "See the list of commands"]
    ],
    "Threads": [
        ["/create_thread", "Create a new thread"],
        ["/thread_list", "See the list of all threads"],
        ["/my_threads", "See the list of your threads"],
        ["/read_thread", "Read one of the threads"]
    ]
}


@bot.callback_query_handler(lambda call: True)
def callback_query(call):
    match call.data:
        case "login":
            login(call.message.chat.id, False)
        case "login_pass":
            login(call.message.chat.id, True)
        case "register":
            register(call.message.chat.id)
        case "created_by":
            return_threads_list_by_user_id(call.message.chat.id)
        case "read_by":
            pass


@bot.message_handler(commands=["start"])
def starting_handler(message):
    bot.send_message(message.chat.id, "Hello and welcome to the ChatForumBot.")
    markup = types.InlineKeyboardMarkup()
    if check_user_login(message.chat.id)[0]:
        markup.add(types.InlineKeyboardButton(text=f"Continue as {check_user_login(message.chat.id)[1]}", callback_data="login"))
    else:
        if check_user_login(message.chat.id)[1] is not None:
            markup.add(types.InlineKeyboardButton(text=f"Log in as {check_user_login(message.chat.id)[1]}", callback_data="login_pass"))
        else:
            markup.add(types.InlineKeyboardButton(text="Create an account", callback_data="register"))
    bot.send_message(message.chat.id, "Before using the bot, you need to log in or register.", reply_markup=markup)


@bot.message_handler(commands=["help"])
def help_handler(message):
    if check_user_login(message.chat.id)[0]:
        msg = "Commands: \n"
        for command_group in commands_list.keys():
            msg += f"==== {command_group} ====\n"
            for command in commands_list[command_group]:
                msg += f"{command[0]}: {command[1]}\n"
                msg += ("-" * 20) + "\n"
        bot.send_message(message.chat.id, msg)
    else:
        starting_handler(message)


@bot.message_handler(commands=["login"])
def login_through_command(message):
    login(message.chat.id, True)


def login(user_id, require_password):
    if check_user_login(user_id)[1] is not None:
        username = get_data(user_id, "username")
        if require_password:
            msg = bot.send_message(user_id, f"Please, enter the password for {username}:")
            bot.register_next_step_handler(msg, login_step2)
        else:
            bot.send_message(user_id, f"Welcome back, {username}! Use /help for the list of commands")
    else:
        bot.send_message(user_id, "Sorry, but you don't have an account yet! Use /start to register an account.")


def login_step2(message):
    password = get_data(message.chat.id, "password")
    if message.text == password:
        set_user_login(message.chat.id, True)
        bot.send_message(message.chat.id, "Logged in successfully! Use /help for the list of commands.")
    else:
        msg = bot.send_message(message.chat.id, "Error: Wrong password!")
        bot.register_next_step_handler(msg, login, (message.chat.id, True))


def register(user_id):
    msg = bot.send_message(user_id, "Plese, enter your username:")
    bot.register_next_step_handler(msg, register_step2)


def register_step2(message):
    if check_for_unique_username(message.text):
        msg = bot.send_message(message.chat.id, f"Now, please, enter the password you would like to use for {message.text}:")
        bot.register_next_step_handler(msg, register_step3, message.text)
    else:
        msg = bot.send_message(message.chat.id, f"Sorry, but it seems like there already exists an account named {message.text}.")
        bot.register_next_step_handler(msg, register)


def register_step3(message, username):
    password = message.text
    create_new_user(message.chat.id, username, password)
    bot.send_message(message.chat.id, f"Registered you as {username} successfully! Use /help for the list of commands.")


@bot.message_handler(commands=["logout"])
def logout(message):
    if check_user_login(message.chat.id)[0]:
        username = get_data(message.chat.id, "username")
        msg = bot.send_message(message.chat.id, f"Please, enter the password for {username} to log out:")
        bot.register_next_step_handler(msg, logout_step2)
    else:
        starting_handler(message)


def logout_step2(message):
    password = get_data(message.chat.id, "password")
    if message.text == password:
        set_user_login(message.chat.id, False)
        bot.send_message(message.chat.id, "Logged out successfully!")
    else:
        bot.send_message(message.chat.id, "Error: Wrong password!")


@bot.message_handler(commands=["delete_account"])
def delete_account(message):
    if check_user_login(message.chat.id)[0]:
        username = get_data(message.chat.id, "username")
        msg = bot.send_message(message.chat.id, f"Please, enter the password for {username} to delete the account:")
        bot.register_next_step_handler(msg, delete_account_step2)
    else:
        starting_handler(message)


def delete_account_step2(message):
    password = get_data(message.chat.id, "password")
    if message.text == password:
        delete_account_from_db(message.chat.id)
        bot.send_message(message.chat.id, "Deleted your account successfully!")
    else:
        bot.send_message(message.chat.id, "Error: Wrong password!")


@bot.message_handler(commands=["create_thread"])
def create_thread(message):
    msg = bot.send_message(message.chat.id, "What do you want the theme of the thread to be:")
    bot.register_next_step_handler(msg, create_thread_step2)


def create_thread_step2(message):
    if check_for_unique_threadname(message.text):
        msg = bot.send_message(message.chat.id, "Now, please, give your thread a short description:")
        bot.register_next_step_handler(msg, create_thread_step3, message.text)
    else:
        msg = bot.send_message(message.chat.id, f"There already exists a thread with name {message.text}")
        bot.register_next_step_handler(msg, create_thread)


def create_thread_step3(message, threadname):
    new_thread_id = generate_thread_id()
    add_thread(new_thread_id, threadname, message.text, message.chat.id)
    bot.send_message(message.chat.id, f"Thread {threadname} was successfully created!")


@bot.message_handler(commands=["thread_list"])
def return_threads_list(message):
    threads_list = get_threads_list()
    msg = "Threads: \n"
    for el in threads_list:
        msg += f"Name: {el[2]} | Description: {el[3]} \n"
        msg += ("-" * 20) + "\n"
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=["my_threads"])
def choose_threads_to_return(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="See the threads you created", callback_data="created_by"))
    markup.add(types.InlineKeyboardButton(text="See the threads you read", callback_data="read_by"))
    bot.send_message(message.chat.id, "Do you want to see the threads you created or the threads you read?", reply_markup=markup)


def return_threads_list_by_user_id(user_id):
    threads_list = get_threads_list()
    msg = "Threads you created: \n"
    for el in threads_list:
        if el[1] == user_id
            msg += f"Name: {el[2]} | Description: {el[3]} \n"
            msg += ("-" * 20) + "\n"
    bot.send_message(message.chat.id, msg)
