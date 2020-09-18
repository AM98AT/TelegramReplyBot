import random
import traceback
from ast import literal_eval
from datetime import datetime

import pyrebase
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

# --------- for enable the firebase database --------- #

config2 = {
    "apiKey": "AIzaSyCQou2GNxE8BZBohrh0iUYAhU2GQsiauug",
    "authDomain": "telegram-bot-f6779.firebaseapp.com",
    "databaseURL": "https://telegram-bot-f6779.firebaseio.com",
    "storageBucket": "telegram-bot-f6779.appspot.com",
}
firebase2 = pyrebase.initialize_app(config2)
db2 = firebase2.database()

config = {
    "apiKey": "AIzaSyCmNQjaN2duGUUxWF-FxF9ubawb0LSHMVk",
    "authDomain": "reply-bot-for-telegram.firebaseapp.com",
    "databaseURL": "https://reply-bot-for-telegram.firebaseio.com",
    "storageBucket": "reply-bot-for-telegram.appspot.com",
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()

# --------- for enable the telegram bot --------- #

token = "1309329858:AAGdZIqTFEhbW-oQp0IOrZVurAbwuT-S2SI"
updater = Updater(token, use_context=True)
bot = Bot(token)


def error_handle(context, chat_id, error):

    global bot_message

    try:
        context.bot.delete_message(
            chat_id=chat_id, message_id=bot_message["message_id"]
        )

    except:
        pass

    bot_message = context.bot.send_message(
        chat_id=chat_id,
        text="Sorry there is a error the bot will stop\nto reactive the bot please click /start",
    )
    context.bot.send_message(
        chat_id=99781774, text=f"the error in chat {chat_id} \n{error}"
    )


def get_file_id(file_id):

    try:
        file_link = bot.getFile(file_id)
        file_path = file_link["file_path"]
        return file_path
    except:
        return "The File is too big"


def file_path(message):

    if message.get("photo") != []:
        file_id = message["photo"][-1]["file_id"]
        message["photo"][-1]["file_path"] = get_file_id(file_id)

    the_type = [
        "sticker",
        "animation",
        "document",
        "video",
        "voice",
        "video_note",
        "audio",
    ]

    for i in the_type:
        if message.get(f"{i}") != None:
            file_id = message[f"{i}"]["file_id"]
            message[f"{i}"]["file_path"] = get_file_id(file_id)

    return message


def the_username(message):

    first_name = message["from"].get("first_name")
    last_name = message["from"].get("last_name")
    username = message["from"].get("username")
    from_id = message["from"].get("id")

    if username != None:
        return "@" + username

    elif first_name != None and last_name != None:
        return first_name + " " + last_name

    elif first_name != None:
        return first_name

    elif last_name != None:
        return last_name

    else:
        return from_id


def my_pop(my_dict):

    my_dict.pop("channel_chat_created")
    my_dict.pop("delete_chat_photo")
    my_dict.pop("group_chat_created")
    my_dict.pop("supergroup_chat_created")
    return my_dict


def start(update, context):

    global the_bot

    try:
        message_receive(update, context)
        the_start_message = literal_eval(str(update.message))

        try:
            context.bot.delete_message(
                chat_id=the_start_message["chat"]["id"],
                message_id=bot_message["message_id"],
            )

        except:
            pass

        mess_id = db.child("all_message").get()
        chats_id_in_firebase = mess_id.val().keys()

        if str(the_start_message["chat"]["id"]) in chats_id_in_firebase:
            reply_markup = InlineKeyboardMarkup(keyboard4)

        else:
            reply_markup = InlineKeyboardMarkup(keyboard2)

        mess = update.message.reply_text(
            "Please choose what you want :", reply_markup=reply_markup
        )

        if the_start_message["chat"]["id"] in the_bot.keys():
            the_bot[the_start_message["chat"]["id"]][
                the_start_message["from"]["id"]
            ] = {
                "state": "start",
                "random message": 0,
                "message_id": mess["message_id"],
                "username": the_username(the_start_message),
            }

        else:
            the_bot[the_start_message["chat"]["id"]] = {
                the_start_message["from"]["id"]: {
                    "state": "start",
                    "random message": 0,
                    "message_id": mess["message_id"],
                    "username": the_username(the_start_message),
                }
            }

    except:
        error = traceback.format_exc()
        error_handle(context, the_start_message["chat"]["id"], error)

        the_bot.pop(the_start_message["chat"]["id"])


def button(update, context):

    global button_message_id, button_message_text, query, button_clicker_username, bot_message, the_message_in_firebase

    try:
        query = update.callback_query
        query_dic = literal_eval(str(query))
        button_chat_id = query_dic["message"]["chat"]["id"]
        button_message_id = query_dic["message"]["message_id"]
        button_message_text = query_dic["message"]["text"]
        button_clicker_id = query_dic["from"]["id"]
        button_clicker_username = the_username(query_dic)

        if button_chat_id in the_bot and button_clicker_id in the_bot[button_chat_id]:

            if query.data == "ADD":

                mess = query.edit_message_text(
                    text=f"{button_clicker_username} To add new massage please reply to the message"
                )
                the_bot[button_chat_id][button_clicker_id] = {
                    "state": "ADD",
                    "random message": 0,
                    "message_id": mess["message_id"],
                    "username": button_clicker_username,
                }

            elif query.data == "DELETE":

                mess = query.edit_message_text(
                    text=f"{button_clicker_username} To delete any message please reply to the message"
                )
                the_bot[button_chat_id][button_clicker_id] = {
                    "state": "DELETE",
                    "random message": 0,
                    "message_id": mess["message_id"],
                    "username": button_clicker_username,
                }

            elif query.data == "STOP":

                context.bot.delete_message(
                    chat_id=button_chat_id,
                    message_id=the_bot[button_chat_id][button_clicker_id]["message_id"],
                )
                context.bot.send_message(
                    chat_id=button_chat_id,
                    text=f"{button_clicker_username} you lost the access to the bot now",
                )

                the_bot[button_chat_id].pop(button_clicker_id)

                if the_bot[button_chat_id] == {}:
                    the_bot.pop(button_chat_id)

                else:
                    the_users = the_bot[button_chat_id].keys()
                    reply_markup = InlineKeyboardMarkup(keyboard4)

                    for i in the_users:
                        context.bot.send_message(
                            chat_id=button_chat_id,
                            text=f'{the_bot[button_chat_id][i]["username"]} still has access to the bot ',
                            reply_markup=reply_markup,
                        )

            elif query.data == "RANDOM":

                context.bot.delete_message(
                    chat_id=button_chat_id,
                    message_id=the_bot[button_chat_id][button_clicker_id]["message_id"],
                )

                while True:

                    try:
                        chat_id_in_firebase = (
                            db.child("all_message")
                            .child(str(button_chat_id))
                            .shallow()
                            .get()
                        )
                        messages_in_chat_id_in_firebase = list(
                            chat_id_in_firebase.val()
                        )
                        the_random_key = random.randint(
                            0, len(messages_in_chat_id_in_firebase) - 1
                        )
                        the_message_in_firebase = messages_in_chat_id_in_firebase[
                            the_random_key
                        ]

                        random_message = (
                            db.child("all_message")
                            .child(str(button_chat_id))
                            .child(str(the_message_in_firebase))
                            .get()
                        )

                        info_of_random_message = dict(random_message.val())

                        keyboard5 = [
                            [
                                InlineKeyboardButton(
                                    "Add New Massage", callback_data="ADD"
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    "Delete a Message", callback_data="DELETE"
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    "Send a Random Message",
                                    callback_data="RANDOM",
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    "Stop The Bot", callback_data="STOP"
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    "Delete the Random Message",
                                    callback_data="DELETE THIS",
                                )
                            ],
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard5)

                        context.bot.send_message(
                            chat_id=button_chat_id,
                            text=f'"{the_username(info_of_random_message)}" save this message\n'
                            f"with caption \"{info_of_random_message['text']}\" \nat {datetime.fromtimestamp(info_of_random_message['date'])}",
                            reply_to_message_id=the_message_in_firebase,
                        )

                        mess = context.bot.send_message(
                            chat_id=button_chat_id,
                            text="Please choose what you want :",
                            reply_markup=reply_markup,
                        )
                        the_bot[button_chat_id][button_clicker_id] = {
                            "state": "RANDOM",
                            "random message": the_message_in_firebase,
                            "message_id": mess["message_id"],
                            "username": button_clicker_username,
                        }

                        break

                    except TypeError:
                        reply_markup = InlineKeyboardMarkup(keyboard2)
                        mess = context.bot.send_message(
                            chat_id=button_chat_id,
                            text="I don't have any massage please add some",
                            reply_markup=reply_markup,
                        )
                        the_bot[button_chat_id][button_clicker_id] = {
                            "state": "Nothing",
                            "random message": 0,
                            "message_id": mess["message_id"],
                            "username": button_clicker_username,
                        }

                        break

                    except:
                        db.child("all_message").child(str(button_chat_id)).child(
                            str(the_message_in_firebase)
                        ).remove()

            elif query.data == "DELETE THIS":

                message_id = the_bot[button_chat_id][button_clicker_id][
                    "random message"
                ]

                if message_id != 0:

                    db.child("all_message").child(str(button_chat_id)).child(
                        str(message_id)
                    ).remove()

                    reply_markup = InlineKeyboardMarkup(keyboard4)

                    context.bot.delete_message(
                        chat_id=button_chat_id,
                        message_id=the_bot[button_chat_id][button_clicker_id][
                            "message_id"
                        ],
                    )

                    context.bot.send_message(
                        chat_id=button_chat_id,
                        text="This message has been deleted",
                        reply_to_message_id=message_id,
                    )

                    mess = context.bot.send_message(
                        chat_id=button_chat_id,
                        text="Please choose what you want :",
                        reply_markup=reply_markup,
                    )
                    the_bot[button_chat_id][button_clicker_id] = {
                        "state": "RANDOM",
                        "random message": 0,
                        "message_id": mess["message_id"],
                        "username": button_clicker_username,
                    }

                else:

                    context.bot.delete_message(
                        chat_id=button_chat_id, message_id=button_message_id
                    )

            else:
                the_bot[button_chat_id][button_clicker_id] = {
                    "state": "NOTHING",
                    "random message": 0,
                    "username": button_clicker_username,
                }

        else:
            try:
                context.bot.delete_message(
                    chat_id=button_chat_id, message_id=button_message_id
                )

            except:
                pass

            if (
                bot_message["text"]
                != f"{button_clicker_username} you don't have access to the bot if you want to use it click /start"
            ):
                bot_message = context.bot.send_message(
                    chat_id=button_chat_id,
                    text=f"{button_clicker_username} you don't have access to the bot if you want to use it click /start",
                )

    except:
        error = traceback.format_exc()
        error_handle(context, button_chat_id, error)
        the_bot.pop(button_chat_id)


def replay(update, context):

    message_receive(update, context)

    try:
        reply_message = literal_eval(str(update.message))
        reply_chat_id = reply_message["chat"].get("id")
        reply_user_id = reply_message["from"].get("id")

        if reply_chat_id in the_bot and reply_user_id in the_bot[reply_chat_id]:

            reply_markup = InlineKeyboardMarkup(keyboard4)

            mess_id = db.child("all_message").get()
            chats_id_in_firebase = mess_id.val().keys()
            message_id_for_reply = reply_message["reply_to_message"].get("message_id")

            if the_bot[reply_chat_id][reply_user_id]["state"] == "ADD":

                reply_message = my_pop(reply_message)
                reply_message["reply_to_message"] = my_pop(
                    reply_message["reply_to_message"]
                )
                reply_message["reply_to_message"] = file_path(
                    reply_message["reply_to_message"]
                )

                if str(reply_chat_id) not in chats_id_in_firebase:
                    db.child("all_message").child(str(reply_chat_id)).set(
                        {message_id_for_reply: reply_message}
                    )

                else:
                    db.child("all_message").child(str(reply_chat_id)).update(
                        {message_id_for_reply: reply_message}
                    )

                try:
                    context.bot.delete_message(
                        chat_id=reply_chat_id,
                        message_id=the_bot[reply_chat_id][reply_user_id]["message_id"],
                    )

                    context.bot.send_message(
                        chat_id=reply_chat_id,
                        text="This massage has been added",
                        reply_to_message_id=message_id_for_reply,
                    )

                    mess = context.bot.send_message(
                        chat_id=reply_chat_id,
                        text="Please choose what you want :",
                        reply_markup=reply_markup,
                    )
                    the_bot[reply_chat_id][reply_user_id] = {
                        "state": "Add",
                        "random message": 0,
                        "message_id": mess["message_id"],
                        "username": the_username(reply_message),
                    }

                except:
                    reply_markup = InlineKeyboardMarkup(keyboard4)
                    mess = context.bot.send_message(
                        chat_id=reply_chat_id,
                        text="I can't add this message",
                        reply_markup=reply_markup,
                    )
                    the_bot[reply_chat_id][reply_user_id] = {
                        "state": "Add",
                        "random message": 0,
                        "message_id": mess["message_id"],
                        "username": the_username(reply_message),
                    }

            elif the_bot[reply_chat_id][reply_user_id]["state"] == "DELETE":

                try:

                    chat_id_in_firebase = (
                        db.child("all_message")
                        .child(str(reply_chat_id))
                        .shallow()
                        .get()
                    )
                    all_message_id_in_firebase = []
                    j = 0
                    for i in chat_id_in_firebase.val():
                        all_message_id_in_firebase.append(i)

                        if i == str(message_id_for_reply):

                            j += 1
                            db.child("all_message").child(str(reply_chat_id)).child(
                                i
                            ).remove()
                            all_message_id_in_firebase.pop(
                                all_message_id_in_firebase.index(i)
                            )

                    if j == 0:
                        the_message = "I don't have this message"

                    else:
                        the_message = "This message has been deleted"

                    if all_message_id_in_firebase == []:
                        reply_markup = InlineKeyboardMarkup(keyboard2)
                    else:
                        reply_markup = InlineKeyboardMarkup(keyboard4)

                    context.bot.delete_message(
                        chat_id=reply_chat_id,
                        message_id=the_bot[reply_chat_id][reply_user_id]["message_id"],
                    )

                    try:
                        context.bot.send_message(
                            chat_id=reply_chat_id,
                            text=the_message,
                            reply_to_message_id=message_id_for_reply,
                        )
                        mess = context.bot.send_message(
                            chat_id=reply_chat_id,
                            text="Please choose what you want :",
                            reply_markup=reply_markup,
                        )
                        the_bot[reply_chat_id][reply_user_id] = {
                            "state": "Nothing",
                            "random message": 0,
                            "message_id": mess["message_id"],
                            "username": the_username(reply_message),
                        }

                    except:
                        reply_markup = InlineKeyboardMarkup(keyboard4)
                        mess = context.bot.send_message(
                            chat_id=reply_chat_id,
                            text="I can't delete this message",
                            reply_markup=reply_markup,
                        )
                        the_bot[reply_chat_id][reply_user_id] = {
                            "state": "Nothing",
                            "random message": 0,
                            "message_id": mess["message_id"],
                            "username": the_username(reply_message),
                        }

                except TypeError:
                    reply_markup = InlineKeyboardMarkup(keyboard2)
                    mess = context.bot.send_message(
                        chat_id=reply_chat_id,
                        text="I don't have any massage please add some",
                        reply_markup=reply_markup,
                    )
                    the_bot[reply_chat_id][reply_user_id] = {
                        "state": "Nothing",
                        "random message": 0,
                        "message_id": mess["message_id"],
                        "username": the_username(reply_message),
                    }

    except:
        error = traceback.format_exc()
        error_handle(context, reply_chat_id, error)
        the_bot.pop(reply_chat_id)


def message_receive(update, context):

    try:
        message = literal_eval(str(update.message))
        message_chat_id = message["chat"].get("id")

        if message.get("reply_to_message") != None:
            message["reply_to_message"] = my_pop(message["reply_to_message"])
            message["reply_to_message"] = file_path(message["reply_to_message"])

        message = my_pop(message)
        message = file_path(message)

        message_id = message.get("message_id")

        all_message = db2.child("all_message").get()

        chat_id_in_firebase = all_message.val().keys()

        if str(message_chat_id) not in chat_id_in_firebase:
            db2.child("all_message").child(str(message_chat_id)).set(
                {message_id: message}
            )

        else:
            db2.child("all_message").child(str(message_chat_id)).update(
                {message_id: message}
            )

    except:
        error = traceback.format_exc()
        error_handle(context, message_chat_id, error)


the_bot = {}
bot_message = {"text": " "}

keyboard4 = [
    [InlineKeyboardButton("Add New Massage", callback_data="ADD")],
    [InlineKeyboardButton("Delete a Message", callback_data="DELETE")],
    [InlineKeyboardButton("Send a Random Message", callback_data="RANDOM")],
    [InlineKeyboardButton("Stop The Bot", callback_data="STOP")],
]

keyboard2 = [
    [InlineKeyboardButton("Add New Massage", callback_data="ADD")],
    [InlineKeyboardButton("Stop The Bot", callback_data="STOP")],
]


def main():

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(MessageHandler(Filters.reply, replay))
    updater.dispatcher.add_handler(MessageHandler(Filters.all, message_receive))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
