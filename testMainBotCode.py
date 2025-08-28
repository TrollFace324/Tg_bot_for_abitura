from gettingInfoFromUser import get_user_info
import telebot
from telebot.types import Message, ReplyKeyboardMarkup
import json
from TG_BOT_API_TOKEN import API_TOKEN
import os

PATH_FOR_DATA = "dataUsers"

COMMANDS = {
    "COMMAND_REGISTRATION": "Регистрация",
    "COMMAND_PLACE": "Место",
    "COMMAND_HELP": "help",
    "COMMAND_BACK": "Назад",
}

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
    user_id = data["id"]

    result = {
        "id": user_id,
        "subjects": {
            subjects[s]: data["scores"][i] for i, s in enumerate(data["subjects"])
        },
        "roads": [{
            "number_prior": prior,
            "place": place,
            "name_prior": namePrior,
        } for prior, place, namePrior in get_user_info(user_id)]
    }
    
    filename = os.path.join(PATH_FOR_DATA, f"user_{chat_id}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

class CreatKeyboard:
    def initKeyboard(listBtn: list) -> ReplyKeyboardMarkup:
        # Создаем клавиатуру
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

        # Добавляем кнопки
        for btn in listBtn:
            markup.add(COMMANDS[btn])

        return markup

    def menuBoard() -> ReplyKeyboardMarkup:
        return CreatKeyboard.initKeyboard(["COMMAND_REGISTRATION", "COMMAND_PLACE", "COMMAND_HELP"])
    
    def regBoard() -> ReplyKeyboardMarkup:
        return CreatKeyboard.initKeyboard(["COMMAND_BACK"])

# Класс команды назад
class CommandBack():
    # Обработчик команды /Назад
    @bot.message_handler(func=lambda msg: msg.text == COMMANDS["COMMAND_BACK"] or msg.text not in COMMANDS.values())
    def returnKeyboardFunc(message: Message):
        chat_id = message.chat.id

        bot.send_message(chat_id, reply_markup=CreatKeyboard.menuBoard(), text=f"Введите команду")

    # Декоратор отмены выполнения команды
    def decorator_return(func):
        def wrapper(message: Message, *args, **kwargs):
            if message.text == COMMANDS["COMMAND_BACK"]:
                chat_id = message.chat.id

                bot.send_message(chat_id, reply_markup=CreatKeyboard.menuBoard(), text="Ввод отменен")
                if chat_id in user_data:
                    del user_data[chat_id]  # Удаляем неполные данные
                
                return
            func(message, *args, **kwargs)

        return wrapper

class Start:
    # --- Команда /start ---
    @bot.message_handler(commands=['start'])
    def start_message(message: Message):
        bot.send_message(message.chat.id, reply_markup=CreatKeyboard.menuBoard(), text="Добро пожаловать! Для регистрации отправьте команду 'Регистрация'.")

class Registration:
    # --- Начало регистрации ---
    @bot.message_handler(func=lambda msg: msg.text == "Регистрация")
    def registration(message: Message):
        chat_id = message.chat.id
        user_data[chat_id] = {}

        bot.send_message(chat_id, parse_mode="HTML", reply_markup=CreatKeyboard.regBoard(), text=(
            "Введите ваш идентификационный номер\n"
            "Пример: <code>12345</code>"))
        bot.register_next_step_handler(message, Registration.get_id)

    @CommandBack.decorator_return
    def get_id(message: Message):
        chat_id = message.chat.id
        id_abitur = message.text.strip()

        try:
            id_abitur = int(id_abitur)
            
            if id_abitur <= 0:
                raise ValueError
        except:
            return send_error(message, chat_id, Registration.get_id)
        user_data[chat_id]["id"] = int(id_abitur)
        
        subj_list = "\n".join([f"{k}) {v}" for k, v in subjects.items()])

        bot.send_message(chat_id, parse_mode="HTML", reply_markup=CreatKeyboard.regBoard(), text=(
            "Укажите 3 номера предметов, которые вы сдали с результатами ЕГЭ:\n"
            f"{subj_list}\n"
            "Пример: <code>1 2 3</code>"))
        bot.register_next_step_handler(message, Registration.get_subjects)

    @CommandBack.decorator_return
    def get_subjects(message: Message):
        chat_id = message.chat.id
        try:
            chosen = list(map(int, message.text.strip().split()))
            if len(set(chosen)) != 3 or any(s not in subjects for s in chosen):
                raise ValueError
            user_data[chat_id]["subjects"] = chosen
            user_data[chat_id]["scores"] = []
            
            Registration.get_score(message, 0)
        except ValueError:
            send_error(message, chat_id, Registration.get_subjects)

    @CommandBack.decorator_return
    def get_score(message: Message, idx: int):
        chat_id = message.chat.id

        if idx != 0:
            try:
                score = int(message.text.strip())
                
                if score < 0:
                    raise ValueError
            except ValueError:
                return send_error(message, chat_id, Registration.get_score, idx)
            user_data[chat_id]["scores"].append(score)

        if idx != 3:
            subj_name = subjects[user_data[chat_id]["subjects"][idx]]

            bot.send_message(chat_id, parse_mode="HTML", reply_markup=CreatKeyboard.regBoard(), text=(
                f"Введите кол-во баллов по предмету <b>{subj_name}</b>\n"
                "Пример: <code>90</code>"))

            if idx == 0:
                return bot.register_next_step_handler(message, Registration.get_score, idx+1)
        
        if idx != 3:
            return bot.register_next_step_handler(message, Registration.get_score, idx+1)
        else:
            # Сохраняем в JSON
            save_to_json(chat_id)
            return bot.send_message(chat_id, reply_markup=CreatKeyboard.menuBoard(), text="Регистрация завершена! Данные сохранены.")

print("Бот запущен...")
bot.polling(none_stop=True)

