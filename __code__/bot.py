# (c) cat dev 2023

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
        ["/help", "See the list of commands"],
        ["/rules", "See the list of rules"]
    ],
    "Threads": [
        ["/create_thread", "Create a new thread"],
        ["/thread_list", "See the list of all threads"],
        ["/my_threads", "See the list of your threads"],
        ["/read_thread", "Read one of the threads"],
        ["/write_to_thread", "Write a message in one of the threads"],
        ["/subscribe", "Subscribe to one of the threads"],
        ["/unsubscribe", "Unsubscribe from one of the threads"]
    ]
}
rules_list = {
    "Account": [
        [1, "Do not use any bad words in your username (e.g. N-word)"],
        [2, "Do not use bot commands in your username (e.g. /start)"]
    ],
    "Threads": [
        [1, "Do not use any bad words in your username (e.g. N-word)"],
        [2, "Do not use bot commands in your username (e.g. /start)"],
        [3, "Do not discuss anything which breaks the law of your country and/or the international law (e.g. drugs)"],
        [4, "Do not insult other users"],
        [5, "Discuss things in the respective threads (e.g. discuss food only in the 'food' thread and not in the 'pets' thread)"]
    ],
    "Copyright (for developers)": [
        [1, "Feel free to use the bot's source code in your project for as long as you credit @whynotlol1 (github) or @cat_dev_lol (telegram)"]
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


@bot.message_handler(commands=["rules"])
def rules_handler(message):
    if check_user_login(message.chat.id)[0]:
        msg = "Rules: \n"
        for rule_group in rules_list.keys():
            msg += f"==== {rule_group} ====\n"
            for rule in rules_list[rule_group]:
                msg += f"{rule[0]}: {rule[1]}\n"
                msg += ("-" * 20) + "\n"
        bot.send_message(message.chat.id, msg)
    else:
        starting_handler(message)


@bot.message_handler(commands=["help"])
def help_handler(message):
    if check_user_login(message.chat.id)[0]:
        msg = "Commands: \n"
        for command_group in commands_list.keys():
            msg += f"==== {command_group} ====\n"
            for command in commands_list[command_group]:
                msg += f"{command[0]}: {command[1]}\n"
                msg += ("-" * 20) + "\n"
        msg += "If you want to stop executing any command, type 'quit'!"
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
            bot.send_message(user_id, f"Welcome back, {username}! Use /help for the list of commands. Make sure not to break the /rules!")
    else:
        bot.send_message(user_id, "Sorry, but you don't have an account yet! Use /start to register an account.")


def login_step2(message):
    password = get_data(message.chat.id, "password")
    if message.text == password:
        set_user_login(message.chat.id, True)
        bot.send_message(message.chat.id, "Logged in successfully! Use /help for the list of commands. Make sure not to break the /rules!")
    else:
        msg = bot.send_message(message.chat.id, "Error: Wrong password!")
        bot.register_next_step_handler(msg, login, (message.chat.id, True))


def register(user_id):
    msg = bot.send_message(user_id, "Please, enter your username:")
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
    bot.send_message(message.chat.id, f"Registered you as {username} successfully! Use /help for the list of commands. Make sure not to break the /rules!")


@bot.message_handler(commands=["logout"])
def logout(message):
    if check_user_login(message.chat.id)[0]:
        username = get_data(message.chat.id, "username")
        msg = bot.send_message(message.chat.id, f"Please, enter the password for {username} to log out:")
        bot.register_next_step_handler(msg, logout_step2)
    else:
        starting_handler(message)


def logout_step2(message):
    if message.text.lower() == "quit":
        bot.send_message(message.chat.id, "Quitting logout process")
    else:
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
    if message.text.lower() == "quit":
        bot.send_message(message.chat.id, "Quitting delete_account process")
    else:
        password = get_data(message.chat.id, "password")
        if message.text == password:
            delete_account_from_db(message.chat.id)
            bot.send_message(message.chat.id, "Deleted your account successfully!")
        else:
            bot.send_message(message.chat.id, "Error: Wrong password!")


@bot.message_handler(commands=["create_thread"])
def create_thread(message):
    if check_user_login(message.chat.id)[0]:
        msg = bot.send_message(message.chat.id, "What do you want the theme of the thread to be:")
        bot.register_next_step_handler(msg, create_thread_step2)
    else:
        starting_handler(message)


def create_thread_step2(message):
    if message.text.lower() == "quit":
        bot.send_message(message.chat.id, "Quitting create_thread process")
    else:
        if check_for_unique_threadname(message.text):
            msg = bot.send_message(message.chat.id, "Now, please, give your thread a short description:")
            bot.register_next_step_handler(msg, create_thread_step3, message.text)
        else:
            msg = bot.send_message(message.chat.id, f"There already exists a thread with name {message.text}.")
            bot.register_next_step_handler(msg, create_thread)


def create_thread_step3(message, threadname):
    if message.text.lower() == "quit":
        bot.send_message(message.chat.id, "Quitting create_thread process")
    else:
        new_thread_id = generate_thread_id()
        add_thread(new_thread_id, message.chat.id, threadname, message.text)
        bot.send_message(message.chat.id, f"Thread {threadname} was successfully created!")


@bot.message_handler(commands=["thread_list"])
def return_threads_list(message):
    if check_user_login(message.chat.id)[0]:
        threads_list = get_threads_list()
        msg = "Threads: \n"
        for el in threads_list:
            msg += f"Name: {el[2]} | Description: {el[3]} \n"
            msg += ("-" * 20) + "\n"
        bot.send_message(message.chat.id, msg)
    else:
        starting_handler(message)


@bot.message_handler(commands=["my_threads"])
def choose_threads_to_return(message):
    if check_user_login(message.chat.id)[0]:
        return_threads_list_by_user_id(message.chat.id)
    else:
        starting_handler(message)


def return_threads_list_by_user_id(user_id):
    threads_list = get_threads_list()
    msg = "Threads you created: \n"
    for el in threads_list:
        if el[1] == user_id:
            msg += f"Name: {el[2]} | Description: {el[3]} \n"
            msg += ("-" * 20) + "\n"
    bot.send_message(user_id, msg)


@bot.message_handler(commands=["read_thread"])
def read_handler0(message):
    if check_user_login(message.chat.id):
        msg = bot.send_message(message.chat.id, "What thread would you like to read?")
        bot.register_next_step_handler(msg, read_handler1)
    else:
        starting_handler(message)


def read_handler1(message):
    if message.text.lower() == "quit":
        bot.send_message(message.chat.id, "Quitting read_handler process")
    else:
        if not check_for_unique_threadname(message.text):
            thread = parse_thread(message.text)
            if len(thread["messages"]) != 0:
                bot.send_message(message.chat.id, f"Now reading the {thread['global_info']['name']} thread.")
                msg = bot.send_message(message.chat.id, "How many latest messages of this thread do you want to see? (Type a number)")
                bot.register_next_step_handler(msg, show_msgs, thread)
            else:
                bot.send_message(message.chat.id, "There are no messages in this thread.")
        else:
            msg = bot.send_message(message.chat.id, "Sorry, but it seems like this thread does not exist! Try again.")
            bot.register_next_step_handler(msg, read_handler1)


def show_msgs(message, thread):
    if int(message.text) <= len(thread["messages"]):
        bot.send_message(message.chat.id, f"There are the {message.text} latest messages in this thread:")
        for i in range((len(thread["messages"]) - int(message.text)), len(thread["messages"])):
            bot.send_message(message.chat.id, f"{thread['messages'][i][0]}: {thread['messages'][i][1]}")
    else:
        bot.send_message(message.chat.id, f"There are less than {message.text} messages in this thread. Here they are:")
        for i in range(len(thread["messages"])):
            bot.send_message(message.chat.id, f"{thread['messages'][i][0]}: {thread['messages'][i][1]}")


@bot.message_handler(commands=["write_to_thread"])
def write_handler0(message):
    if check_user_login(message.chat.id):
        msg = bot.send_message(message.chat.id, "What thread would you like to write to?")
        bot.register_next_step_handler(msg, write_handler1)
    else:
        starting_handler(message)


def write_handler1(message):
    if message.text.lower() == "quit":
        bot.send_message(message.chat.id, "Quitting write_handler process")
    else:
        if not check_for_unique_threadname(message.text):
            msg = bot.send_message(message.chat.id, "Now, please, enter the message text:")
            bot.register_next_step_handler(msg, write_handler2, message.text)
        else:
            msg = bot.send_message(message.chat.id, "Sorry, but it seems like this thread does not exist! Try again.")
            bot.register_next_step_handler(msg, write_handler1)


def write_handler2(message, threadname):
    user_ids = write_to(threadname, message.chat.id, message.text)
    bot.send_message(message.chat.id, f"Your message has been successfully added to the {threadname} thread!")
    if len(user_ids) != 0:
        for user_id in user_ids:
            if user_id != message.chat.id:
                bot.send_message(user_id, f"There's a new message in the {threadname} thread you're subscribed to:\n{get_data(message.chat.id, "username")}: {message.text}")


@bot.message_handler(commands="subscribe")
def sub_handler0(message):
    if check_user_login(message.chat.id):
        msg = bot.send_message(message.chat.id, "What thread would you like to subscribe to?")
        bot.register_next_step_handler(msg, sub_handler1)
    else:
        starting_handler(message)


def sub_handler1(message):
    if message.text.lower() == "quit":
        bot.send_message(message.chat.id, "Quitting sub_handler process")
    else:
        if not check_for_unique_threadname(message.text):
            sub_to_thread(message.chat.id, message.text)
            bot.send_message(message.chat.id, f"Now you are subscribed to the {message.text} thread!")
        else:
            msg = bot.send_message(message.chat.id, "Sorry, but it seems like this thread does not exist! Try again.")
            bot.register_next_step_handler(msg, sub_handler1)


@bot.message_handler(commands="unsubscribe")
def unsub_handler0(message):
    if check_user_login(message.chat.id):
        msg = bot.send_message(message.chat.id, "What thread would you like to unsubscribe from?")
        bot.register_next_step_handler(msg, unsub_handler1)
    else:
        starting_handler(message)


def unsub_handler1(message):
    if message.text.lower() == "quit":
        bot.send_message(message.chat.id, "Quitting unsub_handler process")
    else:
        if not check_for_unique_threadname(message.text):
            unsub_from_thread(message.chat.id, message.text)
            bot.send_message(message.chat.id, f"Now you are no longer subscribed to the {message.text} thread!")
        else:
            msg = bot.send_message(message.chat.id, "Sorry, but it seems like this thread does not exist! Try again.")
            bot.register_next_step_handler(msg, unsub_handler1)
