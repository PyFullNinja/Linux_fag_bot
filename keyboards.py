from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class LinuxCallback(CallbackData, prefix="film", sep=";"):
    id: int
    name: str


class QuestionCallback(CallbackData, prefix="q"):
    id: int
    category: str


def linux_keyboard_markup(films_list: list[dict]):
    builder = InlineKeyboardBuilder()
    builder.adjust(2, repeat=True)

    for index, film_data in enumerate(films_list):
        category_name = list(film_data.keys())[0]
        callback_data = LinuxCallback(id=index, name=category_name)
        builder.button(text=category_name, callback_data=callback_data.pack())
    return builder.as_markup()


class TestCallback(CallbackData, prefix="linux", sep=";"):
    id: int
    name: str


def OS_test_linux(button: list[dict]) -> InlineKeyboardMarkup | None:
    builder = InlineKeyboardBuilder()
    builder.adjust(1, repeat=True)

    for index, button_data in enumerate(button):
        callback_data = TestCallback(id=index, **button_data)
        builder.button(text=f"{callback_data.name}", callback_data=callback_data.pack())
        builder.adjust(1, repeat=True)
        return builder.as_markup()


def questions_keyboard_markup(questions: list[dict], category_name: str):
    builder = InlineKeyboardBuilder()
    builder.adjust(1, repeat=True)

    for index, question_data in enumerate(questions):
        question_text = question_data["питання"]
        callback_data = QuestionCallback(id=index, category=category_name)
        builder.button(text=question_text, callback_data=callback_data.pack())
    builder.adjust(1, repeat=True)
    return builder.as_markup()
