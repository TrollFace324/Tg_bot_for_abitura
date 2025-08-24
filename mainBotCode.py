from getHTMLsite import get_html_table
from getTableFromHtml import extract_applicants
import telebot
from telebot.types import Message
import json
from TG_BOT_API_TOKEN import API_TOKEN
import os

PATH_FOR_DATA = "dataUsers"

bot = telebot.TeleBot(API_TOKEN)

# Словарь для временного хранения данных пользователей во время регистрации
user_data = {}

# Словарь предметов
subjects = {
    1: "Русский язык",
    2: "Математика",
    3: "Биология",
    4: "География",
    5: "Иностранный язык",
    6: "Информатика",
    7: "История",
    8: "Литература",
    9: "Обществознание",
    10: "Физика",
    11: "Химия"
}

def send_error(message: Message, chat_id: int, func, *arg, **kwargs):
    bot.send_message(chat_id, "Неверный ввод")
    return bot.register_next_step_handler(message, func, *arg, **kwargs)

def save_to_json(chat_id):
    data = user_data[chat_id]
    result = {
        "id": data["id"],
        "subjects": {
            subjects[s]: data["scores"][i] for i, s in enumerate(data["subjects"])
        }
    }
    
    filename = os.path.join(PATH_FOR_DATA, f"user_{chat_id}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

# --- Команда /start ---
@bot.message_handler(commands=['start'])
def start_message(message: Message):
    bot.send_message(message.chat.id, "Добро пожаловать! Для регистрации отправьте команду 'Регистрация'.")


# --- Начало регистрации ---
@bot.message_handler(func=lambda msg: msg.text == "Регистрация")
def registration(message: Message):
    chat_id = message.chat.id
    user_data[chat_id] = {}

    bot.send_message(chat_id, parse_mode="HTML", text=(
        "Введите ваш идентификационный номер\n"
        "Пример: <code>12345</code>"))
    bot.register_next_step_handler(message, get_id)


def get_id(message: Message):
    chat_id = message.chat.id
    id_abitur = message.text.strip()

    try:
        user_data[chat_id]["id"] = int(id_abitur)
    except:
        return send_error(message, chat_id, get_id)
    
    subj_list = "\n".join([f"{k}) {v}" for k, v in subjects.items()])

    bot.send_message(chat_id, parse_mode="HTML", text=(
        "Укажите 3 номера предметов, которые вы сдали с результатами ЕГЭ:\n"
        f"{subj_list}\n"
        "Пример: <code>1 2 3</code>"))
    bot.register_next_step_handler(message, get_subjects)


def get_subjects(message: Message):
    chat_id = message.chat.id
    try:
        chosen = list(map(int, message.text.strip().split()))
        if len(chosen) != 3 or any(s not in subjects for s in chosen):
            raise ValueError
        user_data[chat_id]["subjects"] = chosen
        user_data[chat_id]["scores"] = []
        
        subj_name = subjects[chosen[0]]
        bot.send_message(chat_id, parse_mode="HTML", text=(
            f"Введите кол-во баллов по предмету <b>{subj_name}</b>\n"
            "Пример: <code>90</code>"))
        bot.register_next_step_handler(message, get_score, 0)
    except ValueError:
        send_error(message, chat_id, get_subjects)


def get_score(message: Message, idx: int):
    chat_id = message.chat.id
    subj_name = subjects[user_data[chat_id]["subjects"][idx]]

    bot.send_message(chat_id, parse_mode="HTML", text=(
        f"Введите кол-во баллов по предмету <b>{subj_name}</b>\n"
        "Пример: <code>90</code>"))

    try:
        score = int(message.text.strip())
        user_data[chat_id]["scores"].append(score)
        
        bot.register_next_step_handler(message, get_score, idx+1)
    except ValueError:
        return send_error(message, chat_id, get_score)

    if idx == 2:
        # Сохраняем в JSON
        save_to_json(chat_id)
        return bot.send_message(chat_id, "Регистрация завершена! Данные сохранены.")


print("Бот запущен...")
bot.polling(none_stop=True)

