from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import TELEGRAM_TOKEN
import re

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

messages_storage = []
admin_id = 'admin'
user_counter = 0
user_dict = {}

async def set_commands(bot: Bot):
    commands = [
        types.BotCommand(command='/start', description='Запустить бота'),
        types.BotCommand(command='/help', description='Помощь по командам бота'),
        types.BotCommand(command='/mute', description='Отключить уведомления из чата'),
        types.BotCommand(command='/unmute', description='Включить уведомления из чата'),
        types.BotCommand(command='/search', description='Поиск по ключевому слову'),
        types.BotCommand(command='/settings', description='Настройки бота'),
        types.BotCommand(command='/info', description='Получить информацию'),
        types.BotCommand(command='/contact_admin', description='Связаться с админом')
    ]
    await bot.set_my_commands(commands)

def main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton("Помощь"),
        KeyboardButton("Отключить уведомления"),
        KeyboardButton("Включить уведомления"),
        KeyboardButton("Поиск"),
        KeyboardButton("Настройки"),
        KeyboardButton("Информация"),
        KeyboardButton("Связаться с админом")
    ]
    keyboard.add(*buttons)
    return keyboard

def settings_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton("Изменить имя"),
        KeyboardButton("Изменить возраст"),
        KeyboardButton("Вернуться в главное меню")
    ]
    keyboard.add(*buttons)
    return keyboard

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    global user_counter
    if message.from_user.id not in user_dict:
        user_counter += 1
        user_dict[message.from_user.id] = f"user{user_counter}"
    await message.answer('Привет! Я бот и готов помочь вам.', reply_markup=main_menu())

@dp.message_handler(commands=['help'])
@dp.message_handler(Text(equals='Помощь', ignore_case=True))
async def help(message: types.Message):
    await message.answer('Я могу помочь вам с выполнением следующих команд:\n'
                         '/start - Запустить бота\n'
                         '/help - Получить помощь\n'
                         '/mute - Отключить уведомления\n'
                         '/unmute - Включить уведомления\n'
                         '/search - Поиск информации\n'
                         '/settings - Настройки бота\n'
                         '/info - Получить информацию\n'
                         '/contact_admin - Связаться с админом')

@dp.message_handler(commands=['mute'])
@dp.message_handler(Text(equals='Отключить уведомления', ignore_case=True))
async def mute(message: types.Message):
    await message.answer('Уведомления отключены.')

@dp.message_handler(commands=['unmute'])
@dp.message_handler(Text(equals='Включить уведомления', ignore_case=True))
async def unmute(message: types.Message):
    await message.answer('Уведомления включены.')

@dp.message_handler(commands=['search'])
@dp.message_handler(Text(equals='Поиск', ignore_case=True))
async def search_prompt(message: types.Message):
    await message.answer('Пожалуйста, введите ключевое слово или запрос для поиска.')

@dp.message_handler(commands=['settings'])
@dp.message_handler(Text(equals='Настройки', ignore_case=True))
async def settings(message: types.Message):
    await message.answer('Выберите, что вы хотите изменить:', reply_markup=settings_menu())

@dp.message_handler(Text(equals='Изменить имя', ignore_case=True))
async def change_name(message: types.Message):
    await message.answer('Пожалуйста, введите ваше новое имя:')
    dp.register_message_handler(process_name_change, state=None)

@dp.message_handler(Text(equals='Изменить возраст', ignore_case=True))
async def change_age(message: types.Message):
    await message.answer('Пожалуйста, введите ваш новый возраст:')
    dp.register_message_handler(process_age_change, state=None)

@dp.message_handler(Text(equals='Вернуться в главное меню', ignore_case=True))
async def back_to_main_menu(message: types.Message):
    await message.answer('Вы вернулись в главное меню.', reply_markup=main_menu())

async def process_name_change(message: types.Message):
    new_name = message.text
    await message.answer(f'Ваше имя было изменено на {new_name}', reply_markup=main_menu())
    dp.message_handlers.unregister(process_name_change)

async def process_age_change(message: types.Message):
    new_age = message.text
    await message.answer(f'Ваш возраст был изменен на {new_age}', reply_markup=main_menu())
    dp.message_handlers.unregister(process_age_change)

@dp.message_handler(commands=['info'])
@dp.message_handler(Text(equals='Информация', ignore_case=True))
async def info(message: types.Message):
    await message.answer('Это информационное сообщение от бота.')

@dp.message_handler(commands=['contact_admin'])
@dp.message_handler(Text(equals='Связаться с админом', ignore_case=True))
async def contact_admin(message: types.Message):
    await message.answer('Пожалуйста, введите ваше сообщение для админа:')

@dp.message_handler(Text)
async def handle_text(message: types.Message):
    messages_storage.append({
        'text': message.text,
        'user': message.from_user.full_name,
        'date': message.date.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': message.from_user.id,
        'username': user_dict.get(message.from_user.id, message.from_user.username)
    })

    # Обработка поиска
    if message.text.startswith('/search '):
        keyword = message.text.replace('/search ', '').strip()
        if keyword:
            search_results = [msg for msg in messages_storage if re.search(keyword, msg['text'], re.IGNORECASE)]
            if search_results:
                response = f'Найденные сообщения по запросу "{keyword}":\n\n'
                for msg in search_results:
                    response += f'Сообщение: {msg["text"]}\nОтправлено: {msg["user"]} в {msg["date"]}\n\n'
                await message.answer(response)
            else:
                await message.answer(f'По запросу "{keyword}" ничего не найдено.')
        else:
            await message.answer('Пожалуйста, укажите ключевое слово для поиска.')
    elif user_dict.get(message.from_user.id) == 'admin':
        # Обработка сообщений от админа
        if message.reply_to_message:
            original_message_id = message.reply_to_message.message_id
            original_message = next((msg for msg in messages_storage if msg['message_id'] == original_message_id), None)
            if original_message:
                user_id = original_message['user_id']
                await bot.send_message(user_id, f'Ответ от админа:\n{message.text}')
    else:
        if message.reply_to_message:
            await message.answer('Ваше сообщение было отправлено администратору.')
            await bot.send_message(admin_id, f'Сообщение от {message.from_user.full_name} ({user_dict[message.from_user.id]}):\n{message.text}')
        else:
            state = await dp.current_state(user=message.from_user.id).get_state()
            if state == 'waiting_for_name':
                await process_name_change(message)
            elif state == 'waiting_for_age':
                await process_age_change(message)

async def on_startup(dispatcher):
    await set_commands(dispatcher.bot)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
