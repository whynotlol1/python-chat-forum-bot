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
        ["/thread_list", "See the list of all threads"],
        ["/my_threads", "See the list of your threads"],
        ["/read_thread", "Read one of the threads"],
        ["/create_thread", "Create a new thread"],
        ["/subscribe", "Subscribe to one of the threads"],
        ["/mute_thread", "Mute the notifications from a given thread"],
        ["/unmute_thread", "Unmute the notifications from a given thread"]
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
    add_thread_to_db(new_thread_id, threadname, message.text)
    bot.send_message(message.chat.id, f"Thread {threadname} was successfully created!")
    msg = bot.send_message(message.chat.id, "Now, please, give your thread a detailed description (if you don`t want to do it, type 'NoDesc')")
    bot.register_next_step_handler(msg, create_thread_step4, threadname)


def create_thread_step4(message, threadname):
    if message.text != "NoDesc":
        add_thread_description(threadname, message.text)
        bot.send_message(message.chat.id, f"Successfully dded a description to thred {threadname}!")
