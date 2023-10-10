from aiogram import types
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher
from config import TOKEN
from db import Database


bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dbs = Database('C:/Users/vipar/OneDrive/Desktop/edubot.db')


class RegData(StatesGroup):
    start = State()
    access = State()
    homework_init = State()
    homework_mail = State()


@dp.message_handler(commands=["admin"])
async def open_admin(message: types.Message):    
    user_id = message.from_user.id
    user_info = dbs.get_user(user_id)
    user_role = bool(user_info[-3])

    if user_role:
        await bot.send_message(user_id, "Меню администратора")
    else:
        await bot.send_message(user_id, "Шлепок майонезный")




@dp.message_handler(commands=["info"])
async def show_users_info(message: types.Message):
    user_info = dbs.get_user(message.from_user.id)
    user_role = bool(user_info[-3])

    users = dbs.get_users()

    if user_role:
        
        message_pack = ""

        user_confirmed = {                
                True: 'доступ имеется',
                False: 'доступа нет'
            }

        for user in users:

            message_pack += (f"{user[1]} {user[2]} - {user_confirmed[user[-2]]}") 

            if bool(user[-2]) == True:
                message_pack += (f"ключ доступа: {user[-1]}\n")
           

        await bot.send_message(user_info[0], f"Пользователи:\n{message_pack}")

    else:
        await bot.send_message(user_info[0], "У вас недостаточно прав")




@dp.message_handler(commands=["orders"])
async def show_orders(message: types.Message):
    user_id = message.from_user.id
    users = dbs.get_users()

    message_pack = ""
    for user in users:        
        if bool(user[-2]) == False:
            message_pack += f"{user[1]} {user[2]} {user[-1]}\n" 

    await bot.send_message(user_id, message_pack)




@dp.message_handler(commands=["access"], state = None)
async def access_user(message: types.Message):
    await RegData.access.set()
    await bot.send_message(message.from_user.id, "Введите ключ пользователя для запрета/разрешения доступа")



@dp.message_handler(commands=["back"], state = RegData.access)
async def back_to_main(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(message.from_user.id, "Главное меню")
    


@dp.message_handler(commands=["back"], state = RegData.homework_mail)
async def back_to_main(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(message.from_user.id, "Главное меню")




@dp.message_handler(commands=["make"])
async def make_homework(message: types.Message):
    await RegData.homework_init.set()
    await bot.send_message(message.from_user.id, "Введите текст домашнего задания")




@dp.message_handler(state = RegData.homework_init)
async def choose_mailer(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['homework'] = message.text

    await RegData.homework_mail.set()
    await bot.send_message(message.from_user.id, "Введите ключ получателя")




@dp.message_handler(state = RegData.homework_mail)
async def send_homework(message: types.Message, state: FSMContext):
    user_info = dbs.get_user(message.from_user.id)
    user_id = user_info[0]
    user_role = bool(user_info[-3])

    reciever_id = dbs.get_user_by_key(message.text)[0]

    if user_role:
        async with state.proxy() as data:
            
            if dbs.get_last_id("homework") != None:
                dbs.set_homework(dbs.get_last_id("homework") + 1, reciever_id, data['homework'])
            else:
                dbs.set_homework(1, reciever_id, data['homework'])

            await bot.send_message(reciever_id, f"Домашнее задание:\n{data['homework']}")
            await bot.send_message(user_id, f"Домашнее задание успешно отправлено! ")
            
    else:
        await bot.send_message(user_id, "У вас недостаточно прав") 

    await state.finish()



@dp.message_handler(state = RegData.access)
async def confirmed_user(message: types.Message):
    user_key = int(message.text)

    if bool(dbs.get_user_by_key(user_key)):
        user_confirmerd = dbs.get_user_by_key(user_key)[-2]
    else:
        user_confirmerd = False
    
    if bool(dbs.key_exist(user_key)) and bool(user_confirmerd):
        dbs.set_confirmed(False, user_key)
        await bot.send_message(message.from_user.id, "Пользователю был закрыт доступ")
    elif bool(dbs.key_exist(user_key)) and bool(user_confirmerd) == False:
        dbs.set_confirmed(True, user_key)
        await bot.send_message(message.from_user.id, "Пользователю был открыт доступ")
    else:
        await bot.send_message(message.from_user.id, "Пользователя с таким ключом не существует")




if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)