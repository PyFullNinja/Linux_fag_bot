import asyncio
import time
from io import UnsupportedOperation
import g4f
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, URLInputFile
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from g4f.models import gpt_4
from config import TOKEN

# from keyboards import films_keyboard_markup, FilmCallback
# from data import get_films, add_film, get_film_name
# from model import Film
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from g4f.client import Client
from g4f.client import AsyncClient
from g4f import ChatCompletion, Provider, models
# from g4f.Provider import OpenaiChat, Gemini, Bing

from commands import *
from data import get_data, get_film_name
from keyboards import (
    linux_keyboard_markup,
    LinuxCallback,
    questions_keyboard_markup,
    QuestionCallback,
)

print("\n=======================================")

print("sms: Импорты успешно завершены! (DONE)")

dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))

#                           ==============CONFIG==============
telemetria = True  # включает запис всех действий пользователей
amount_of_memory = 2  # количество предыдущих сообщений которое помнит ИИ
admin_id = int  # telegram_id техподдержки


#                           ==============AI===================
class AiGptText(StatesGroup):
    text = State()


@dp.message(AI_START_COMMAND)
async def ai_start(message: Message, state: FSMContext) -> None:
    await state.set_state(AiGptText.text)
    await message.answer(
        "Введiть запрос до AI",
        reply_markup=ReplyKeyboardRemove(),
    )

    if telemetria:
        with open("log.txt", "a") as user_log:
            user_log.write(str(message) + "\n")


@dp.message(AiGptText.text)
async def give_films_actor(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    data = await state.update_data(None)
    history = []
    if telemetria:
        with open("log.txt", "a") as user_log:
            user_log.write(str(message) + "\n")
    client = AsyncClient(provider=Provider.Copilot)
    content = data["date"]
    if history:
        content = (
            data["date"] + f"вот история прерыдущих сообщений: {'\n'.join(history)}"
        )
        if len(history) > amount_of_memory:
            history.pop(0)
    response = await client.chat.completions.create(
        model=g4f.models.default,
        messages=[{"role": "Linux helper", "content": content}],
    )
    print(
        "log: ",
        data["date"],
        "|",
        message.from_user.full_name,
        message.from_user.username,
    )
    history.append(data["date"])
    if data["date"] == "/stop_ai":
        await state.clear()
        history.clear()
        await message.answer("Штучний iнтелект зупинено!")
    else:
        text_ai = str(response.choices[0].message.content)
        text_ai = text_ai.replace("*", "").replace("#", " ")
        await message.answer(text_ai)
        history.append(response.choices[0].message.content)
        print(
            "log: ",
            response.choices[0].message.content,
            "|",
            message.from_user.full_name,
            message.from_user.username,
        )
        with open("log.txt", "a") as user_log:
            user_log.write(response.choices[0].message.content + "\n")


# ============================================= start ==========
if telemetria:
    print(" - Телеметрия включена")
else:
    print(" - Телеметрия выключена")
print(" - Установлено число памяти ИИ:", amount_of_memory)
print(" - Айді техпідтримки:", admin_id)


@dp.message(START_COMMAND)
async def start(message: Message) -> None:
    await message.answer(
        f"Привіт, це бот, який допоможе тобі познайомитися з лінуксом.",
        reply_markup=linux_keyboard_markup(get_data()),
    )

    try:
        if telemetria:
            with open("log.txt", "a") as user_log:
                user_log.write(str(message) + "\n")
    except FileNotFoundError:
        with open("log.txt", "w") as user_log:
            user_log.write(str(message) + "\n")

    try:
        with open("users.txt") as user_id:
            users_account = []
            for x in user_id.readlines():
                users_account.append(x.strip())

        if str(message.from_user.id) not in users_account:
            with open("users.txt", "a") as user_id:
                user_id.write(str(message.from_user.id) + "\n")

    except FileNotFoundError:
        with open("users.txt", "w") as user_id:
            user_id.write(str(message.from_user.id) + "\n")

    print("log: нажал старт:", message.from_user.full_name, message.from_user.username)


# =================== Help user ================
class HelpUser(StatesGroup):
    text = State()


@dp.message(HELP_COMMAND)
async def help_user(message: Message, state: FSMContext):
    await message.answer(
        f"Напишіть ваше звернення, викладіть проблему і вам дадуть відповідь незабаром:"
    )
    await state.set_state(HelpUser.text)


@dp.message(HelpUser.text)
async def support_user(message: Message, state: FSMContext):
    await state.clear()
    await bot.send_message(
        admin_id,
        text=f"{message.text}\n\n "
        f"від: {message.from_user.id}, {message.from_user.full_name}, @{message.from_user.username}",
    )


@dp.message(SUPPORT_COMMAND)
async def support_help_user(message: Message):
    if message.from_user.id == admin_id:
        id_help_user = int(message.text.split(";")[1])
        help_message = message.text.split(";")[2]
    await bot.send_message(
        id_help_user,
        f"{help_message} \n\n для наступного повідомлення не забудьте натиснути /help",
    )


# =================== test linux ===============
class LinuxTest(StatesGroup):
    acquaintance: bool = State()  # знаком ли вам линукс
    month: int = State()  # сколько лет вы с линуксом
    wish: int = State()  # уровень желания перейти на линукс от 1 до 10
    current_os: int = State()  # текущая ос
    runs_on_windows_10: bool = State()  # тянет ли ваш ноут виндовс 10

    score: int = State()


@dp.message(TEST_LINUX_DISTRIBUTION_COMMAND)
async def linux_text_distribution(message: Message, state: FSMContext) -> None:
    await state.set_state(LinuxTest.acquaintance)
    await message.answer(
        f"""
Привіт! Тепер ми з тобою дізнаємося, який дистрибутив лінуксу тобі потрібен. 
По черзі відповідай на запитання номерами відповідей, які будуть представлені нижче. 

Перше питання: чи знайомі ви з лінуксом?
1. так
2. ні

(тобто відповідь має бути або 1 або 2)
"""
    )


@dp.message(LinuxTest.acquaintance)
async def acquaintance_linux(message: Message, state: FSMContext) -> None:
    if message.text == "1":
        await state.update_data(acquaintance=True)
        await state.set_state(LinuxTest.month)
        await message.answer(
            "Добре, ви знайомі, скільки місяців ви користувалися лінуксом? \n(можете написати 0, якщо ви не користувалися)"
        )
    elif message.text == "2":
        await state.update_data(acquaintance=False)
        await state.set_state(LinuxTest.wish)
        await message.answer(
            "Оцініть ваш рівень бажання перейти на лінукс від 1 до 10:"
        )
    else:
        await message.answer(
            "введіть 1 або 2. \n\nТест був завершений через помилку відповіді."
        )


@dp.message(LinuxTest.month)
async def month_linux(message: Message, state: FSMContext) -> None:
    try:
        await state.update_data(mounch=int(message.text))
    except ValueError:
        await message.answer(
            "введіть число. \n\nТест був завершений через помилку відповіді."
        )
    await message.answer("Оцініть ваш рівень бажання перейти на лінукс від 1 до 10:")
    await state.set_state(LinuxTest.wish)


@dp.message(LinuxTest.wish)
async def wish_linux(message: Message, state: FSMContext) -> None:
    try:
        await state.update_data(wish=int(message.text))
    except ValueError:
        await message.answer(
            "введіть число. \n\nТест був завершений через помилку відповіді."
        )

    await message.answer("""
Виберіть вашу поточну операційну систему зі списку:

1. Немає операційної системи
2. MacOS
3. GNU/Linux
4. Windows 95 / XP
5. Windows 7
6. Windows 8 / 8.1
7. Windows 10
8. Windows 11


""")
    await state.set_state(LinuxTest.current_os)


async def final_test(data, message: Message):
    if telemetria:
        with open("log.txt", "a") as user_log:
            user_log.write(str(message.from_user.id) + ": " + str(data) + "\n")

    acquaintance = data["acquaintance"]
    month = data.get("mounch", 0)
    wish = data["wish"]
    current_os = data["current_os"]
    runs_on_windows_10 = data["runs_on_windows_10"]

    if acquaintance:
        if month >= 12:
            if wish >= 8:
                distribution = "Arch Linux"
                reason = "ви досвідчений користувач і бажаєте максимальну гнучкість та контроль."
            else:
                distribution = "Debian"
                reason = (
                    "це стабільний дистрибутив, ідеальний для досвідчених користувачів."
                )
        else:
            if wish >= 7:
                distribution = "Fedora"
                reason = "вона сучасна, з новими технологіями, і підходить для тих, хто вже трохи знайомий з Linux."
            else:
                distribution = "Linux Mint"
                reason = "вона схожа на Windows і зручна у використанні навіть для нечастих користувачів."
    else:
        if runs_on_windows_10:
            distribution = "Ubuntu"
            reason = (
                "вона проста у використанні, має велику спільноту і гарну підтримку."
            )
        else:
            distribution = "Linux Mint XFCE"
            reason = "вона легка, не потребує потужного заліза і зручна для новачків."

    await message.answer(
        f"""
Тест завершено!

На основі відповідей, я рекомендуємо тобi спробувати: {distribution}

Тому що: {reason}

"""
    )


@dp.message(LinuxTest.current_os)
async def current_os_linux(message: Message, state: FSMContext) -> None:
    try:
        await state.update_data(current_os=int(message.text))
    except ValueError:
        await message.answer(
            "введіть число. \n\nТест був завершений через помилку відповіді."
        )
    if message.text != "7" and message.text != "8":
        await message.answer("Чи тягне ваш пристрій windows 10? \n\n1. Да\n2. Нет:")
        await state.set_state(LinuxTest.runs_on_windows_10)
    else:
        await state.update_data(runs_on_windows_10=True)
        data = await state.update_data(None)
        await state.clear()
        await final_test(data, message)


@dp.message(LinuxTest.runs_on_windows_10)
async def runs_on_windows_10_linux(message: Message, state: FSMContext) -> None:
    await state.update_data(runs_on_windows_10=message.text == "1")
    data = await state.update_data(None)
    await state.clear()
    await final_test(data, message)


# ============================ кнопки ==========================
@dp.callback_query(LinuxCallback.filter())
async def linux_button(callback: CallbackQuery, callback_data: LinuxCallback) -> None:
    await callback.message.answer(
        callback_data.name + ": ",
        reply_markup=questions_keyboard_markup(
            get_film_name(callback_data.name), callback_data.name
        ),
    )


@dp.callback_query(QuestionCallback.filter())
async def question_answer(callback: CallbackQuery, callback_data: QuestionCallback):
    questions = get_film_name(callback_data.category)
    if questions and 0 <= callback_data.id < len(questions):
        msg = questions[callback_data.id]["відповідь"]
        await callback.message.answer(msg, parse_mode="Markdown")


async def main() -> None:
    print("sms: Бот успешно запущен! (DONE)\n=======================================\n")
    await dp.start_polling(bot)
    print("sms: завершение.")


if __name__ == "__main__":
    asyncio.run(main())
    print("работает")
