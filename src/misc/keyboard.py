from typing import Dict

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.database import Database
from database.models import TranslatedProduct, Translations, LanguageNames


db = Database()

btn_text_to_action: Dict[str, str] = {}


async def init_buttons_mapping() -> None:
    # Mapping: Localized text -> Action code
    # For example: "Смена языка 🇷🇺" -> "change_language"
    
    global btn_text_to_action

    supported_languages = list(Translations.model_fields.keys())

    for lang in supported_languages:
        btn_text_to_action[await db.get_message('kb_view_menu', lang)] = 'view_menu'
        btn_text_to_action[await db.get_message('kb_change_language', lang)] = 'change_lang'


async def get_main_keyboard(language_code: str) -> ReplyKeyboardMarkup:

    kb_view_menu = await db.get_message('kb_view_menu', language_code)
    kb_change_language = await db.get_message('kb_change_language', language_code)
    
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=kb_view_menu)],
            [KeyboardButton(text=kb_change_language)],
        ],
        resize_keyboard=True,
    )

    return kb


async def get_change_language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    supported_languages = list(Translations.model_fields.keys())
    language_names = LanguageNames()

    for lang_code in supported_languages:
        builder.button(
            text=getattr(language_names, lang_code),
            callback_data=f'change_lang_to_{lang_code}',
        )
    
    builder.adjust(2)
    return builder.as_markup()


async def get_categories_keyboard(language_code: str) -> InlineKeyboardMarkup:
    btn_dishes = await db.get_message('kb_categories_dishes', language_code)
    btn_drinks = await db.get_message('kb_categories_drinks', language_code)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=btn_dishes, callback_data='selected_category_dishes')],
        [InlineKeyboardButton(text=btn_drinks, callback_data='selected_category_drinks')],
    ])

    return kb


async def get_keyboard_for_product(language_code: str, product: TranslatedProduct) -> InlineKeyboardMarkup:
    btn_previous = InlineKeyboardButton(
        text=await db.get_message('btn_previous', language_code),
        callback_data=f'product_prev_{product.category}_{product.id}',
    )

    btn_next = InlineKeyboardButton(
        text=await db.get_message('btn_next', language_code),
        callback_data=f'product_next_{product.category}_{product.id}',
    )

    btn_back_to_categories = InlineKeyboardButton(
        text=await db.get_message('btn_back_to_categories', language_code),
        callback_data='product_back-to-categories',
    )

    return InlineKeyboardMarkup(inline_keyboard=[
        [btn_previous, btn_next],
        [btn_back_to_categories],
    ])
