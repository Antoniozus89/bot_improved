import products
from aiogram import Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import asyncio

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

def create_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    buttons = [
        types.KeyboardButton("Рассчитать"),
        types.KeyboardButton("Информация"),
        types.KeyboardButton("Купить")
    ]
    kb.add(*buttons)
    return kb

def create_inline_keyboard():
    kb = InlineKeyboardMarkup()
    buttons = [
        InlineKeyboardButton("Рассчитать норму калорий", callback_data='calories'),
        InlineKeyboardButton("Формулы расчёта", callback_data='formulas'),
        InlineKeyboardButton("Product1", callback_data='product_buying'),
        InlineKeyboardButton("Product2", callback_data='product_buying'),
        InlineKeyboardButton("Product3", callback_data='product_buying'),
        InlineKeyboardButton("Product4", callback_data='product_buying')
    ]
    kb.add(*buttons)
    return kb

@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью. Нажми "Рассчитать", чтобы начать.',
                         reply_markup=create_keyboard())

@dp.message_handler(lambda message: message.text == "Рассчитать")
async def main_menu(message: types.Message):
    await message.answer('Выберите опцию:', reply_markup=create_inline_keyboard())

@dp.message_handler(lambda message: message.text == "Купить")
async def get_buying_list(message: types.Message):
    products = [
        {"name": "Product1", "description": "Описание 1", "price": 100,
         "image":
         "https://balthazar.club/uploads/posts/2022-10/1666112821_37-balthazar-club-p-tort-kusok-sala-pinterest-40.png"},
        {"name": "Product2", "description": "Описание 2", "price": 200,
         "image":"https://derevenskie-produkty-v-saratove.ru/f/store/item/82/00000282/cover/fullsize.jpg"},
        {"name": "Product3", "description": "Описание 3", "price": 300,
         "image": "https://i.pinimg.com/736x/d6/b2/e5/d6b2e57136c343f0d0ca4d6e9eb03813.jpg"},
        {"name": "Product4", "description": "Описание 4", "price": 400,
         "image": "https://klike.net/uploads/posts/2023-02/1675231900_4-122.jpg"}
    ]

    for product in products:
        await message.answer(f'Название: {product["name"]} | Описание: '
                             f'{product["description"]} | Цена: {product["price"]} руб.')
        await message.answer_photo(photo=product["image"])

    await message.answer('Выберите продукт для покупки:', reply_markup=create_inline_keyboard())

@dp.callback_query_handler(lambda call: call.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    await call.message.answer("Формула Миффлина-Сан Жеора:\n"
                              "Для мужчин: BMR = 10 * вес + 6.25 * рост - 5 * возраст + 5\n"
                              "Для женщин: BMR = 10 * вес + 6.25 * рост - 5 * возраст - 161")
    await call.answer()

@dp.callback_query_handler(lambda call: call.data == 'calories')
async def set_age(call: types.CallbackQuery):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()

@dp.message_handler(state=UserState.age)
async def set_growth(message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state: FSMContext):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state: FSMContext):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    age = int(data['age'])
    growth = int(data['growth'])
    weight = int(data['weight'])
    calories = 10 * weight + 6.25 * growth - 5 * age + 5
    await message.answer(f'Ваша норма калорий: {calories} ккал в день.')
    await state.finish()

@dp.callback_query_handler(lambda call: call.data == 'product_buying')
async def send_confirm_message(call: types.CallbackQuery):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)