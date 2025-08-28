from gettingInfoFromUser import get_user_info
from telebot import TeleBot
import time
import json
import os
import threading

DATA_BASE_USERS = "dataUsers"

def save_data(chat_id: int, user_id: int, info_user: list[list] = None):
        result = {
            "id": user_id,
            "roads": [{
                "number_prior": prior,
                "place": place,
                "name_prior": namePrior,
            } for prior, place, namePrior in [get_user_info(user_id) if info_user == None else info_user][0]]
        }

        filename = os.path.join(DATA_BASE_USERS, f"user_{chat_id}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

def get_place(chat_id: int) -> str:
    chat_id = str(chat_id)
    listUsers = os.listdir(DATA_BASE_USERS)
    user_id = 0
    
    for dataUser in listUsers:
        if chat_id in dataUser:
            with open(os.path.join(DATA_BASE_USERS, dataUser), 'r', encoding='utf-8') as file:
                data = json.load(file)
            user_id = data["id"]
            break

    if user_id == 0:
        return "Вы не зарегистрированы"
    
    user_info = get_user_info(user_id)
    
    if len(user_info) == 0:
        return "Вас нет в списках"

    save_data(chat_id, user_id, user_info)

    result = (
        "Ваше текущее состояние:\n"
        "<i>(Приоритет (название направлениея) -> место)</i>\n"
        "\n"
    )

    result += "<blockquote>" + "\n\n".join([f"<b>{prior}-ий приоритет</b>\n<i>({namePrior})</i> -> <code>№{place}</code>" for prior, place, namePrior in user_info]) + "</blockquote>"

    return result

def send_message_for_ALL(bot: TeleBot):
    def spam_request():
        while True:
            listUsers = os.listdir(DATA_BASE_USERS)

            for dataUser in listUsers:
                with open(os.path.join(DATA_BASE_USERS, dataUser), 'r', encoding='utf-8') as file:
                    data = json.load(file)
                
                user_id = data["id"]
                chat_id = int(dataUser.replace("user_", "").replace(".json", ""))
                new_user_info = get_user_info(user_id)
                info_user = data["roads"]
                
                if len(new_user_info) == 0:
                    continue
                
                move_road = ""

                for i, new_data in enumerate(new_user_info, 0):
                    new_prior, new_place, new_namePrior = new_data
                    for j, road in enumerate(info_user, 0):
                        prior = road["number_prior"]
                        place = road["place"]
                        namePrior = road["name_prior"]

                        if i == j:
                            if new_place != place:
                                move_place = place-new_place
                                move_place = f"{"+" if move_place > 0 else ""}{move_place}"

                                move_road += (
                                    f"Смещение в <b>{new_prior}-ом приоритете</b> на <code>{move_place}</code>\n"
                                    f"<i>({new_namePrior})</i>\n"
                                    f"Текущее место -> <code>{new_place}</code>\n"
                                    "\n"
                                )

                if move_road != "":
                    bot.send_message(chat_id, parse_mode="HTML", text=(
                        "Вы сместились в следующих позициях:\n"
                        "\n"
                        f"<blockquote>{move_road}</blockquote>"
                    ))
                save_data(chat_id, user_id, new_user_info)
            
            time.sleep(10)

    # Создаем и запускаем поток
    task_thread = threading.Thread(target=spam_request)
    task_thread.daemon = True  # Поток будет остановлен при завершении main потока
    task_thread.start()

    