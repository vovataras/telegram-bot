import telebot
import dbworker
import config
import apiface
import requests
import json


bot = telebot.TeleBot(config.token)


# При введенні команди '/start' привітаємося з користувачем.
@bot.message_handler(commands=['start'])
def handle_start_help(message):
    if (dbworker.get_data(str(message.chat.id) + 'name')):
        bot.send_message(message.chat.id, f"Привіт, {dbworker.get_data(str(message.chat.id) + 'name')}!")
    else: 
        bot.send_message(message.chat.id, "Привіт! Як я можу до тебе звертатись?")
        dbworker.set_data(message.chat.id, config.States.S_ENTER_NAME.value)



# При введенні команди '/set_name' змінимо ім'я користувача.
@bot.message_handler(commands=['set_name'])
def set_name(message):
    bot.send_message(message.chat.id, "Тож, як тебе звати?")
    dbworker.set_data(message.chat.id, config.States.S_ENTER_NAME.value)



# Записуємо ім'я користувача
@bot.message_handler(func=lambda message: dbworker.get_data(message.chat.id) == config.States.S_ENTER_NAME.value)
def user_entering_name(message):
    # В випадку з іменем не будемо нічого перевіряти
    bot.send_message(message.chat.id, "Чудове ім'я, запам'ятаю!")
    dbworker.set_data(str(message.chat.id) + 'name', message.text)
    dbworker.set_data(message.chat.id, config.States.S_START.value)



# При введенні команди '/help' виведемо команди для роботи з ботом.
@bot.message_handler(commands=['help'])
def handle_start_help(message):
    bot.send_message(message.chat.id, 'Можливо колись тут появиться документація, але це не точно, 🙃')



# При введенні команди '/how_old_am_i' визначимо скільки років людині на фото
@bot.message_handler(commands=['how_old_am_i'])
def funcname(message):
    bot.send_message(message.chat.id, 'Для того, щоб я визначив вік, закинь мені фото на якому одна людина.\n' \
                     + 'Якщо на фото буде декілька людей то я визначу вік випадково для когось одного.')
    # Переводимо користувача в стан надсилання фотографії для визначення віку
    dbworker.set_data(message.chat.id, config.States.S_SEND_PIC_FOR_AGE.value)



# Аналізуємо фото користувача та визначаємо вік людини на фото
@bot.message_handler(content_types=["photo"],
                     func=lambda message: dbworker.get_data(message.chat.id) == config.States.S_SEND_PIC_FOR_AGE.value)
def sending_photo_for_age(message):
    # Те, що це фотографія, ми вже перевірили в хендлері, ніяких додаткових дій не потрібно.
    bot.send_message(message.chat.id, "Чудово! Почекай трішки, я проаналізую фотографію та дам відповідь)")
    
    # Дізнаємось відносний шлях до фото
    file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
    # Повна URL-адреса фотографії
    url_photo = 'https://api.telegram.org/file/bot' + config.token +  '/' + file_info.file_path
    image = apiface.ClImage(url=url_photo)
    # Отримуємо json-відповідь проаналізованого фото
    response = apiface.model.predict([image])

    # Витягуємо вік з відповіді
    try:
        age = response["outputs"][0]["data"]["regions"][0]["data"]["face"]["age_appearance"]["concepts"][0]["name"]
        # print(f'Людині на фото приблизно {age}')
        bot.send_message(message.chat.id, f'Людині на фото приблизно {age}')
    except:
        bot.send_message(message.chat.id, 'Кумедно, але на фото не людина 🧐')

    # Переводимо користувача в нормальний стан
    dbworker.set_data(message.chat.id, config.States.S_START.value)



# При введенні команди '/random_dog' виведемо випадкове фото чи відео собаки.
@bot.message_handler(commands=['random_dog'])
def random_dog(message):
    r = requests.get(url=config.random_dog_api)
    response = r.json()
    print(response)
    bot.send_message(message.chat.id, response["url"])





if __name__ == '__main__':
    bot.polling(none_stop=True)