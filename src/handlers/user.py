from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto

from database.database import Database
from config import BOT_MSG_PARSE_MODE
from misc.keyboard import btn_text_to_action, get_categories_keyboard, \
    get_main_keyboard, get_change_language_keyboard, get_keyboard_for_product


router = Router()

db = Database()


@router.message(CommandStart())
async def start(message: Message):
    user = message.from_user

    if (user is None) or (user.language_code is None):
        return

    language_code = None
    user_from_db = await db.get_user(user.id)

    if user_from_db is None:
        await db.add_user(user.id, user.language_code)
        language_code = user.language_code
    else:
        language_code = user_from_db.language_code

    if message.bot is not None:
        await message.bot.send_message(
            chat_id=message.chat.id, 
            text=await db.get_message('start', language_code),
            parse_mode=BOT_MSG_PARSE_MODE,
            reply_markup=await get_main_keyboard(language_code),
        )


@router.message(F.text.in_(btn_text_to_action))
async def handle_dynamic_buttons(message: Message):
    if (message.text is None) or (message.from_user is None) or (message.bot is None):
        return

    action = btn_text_to_action[message.text]
    
    if action == 'view_menu':
        await show_menu(message.from_user.id, message.bot)
    elif action == 'change_lang':
        await change_language(message)


async def change_language(message: Message):
    if message.from_user is None:
        return

    user = await db.get_user(message.from_user.id)

    if user is None:
        return

    await message.answer(
        text=await db.get_message('change_language', user.language_code),
        parse_mode=BOT_MSG_PARSE_MODE,
        reply_markup=await get_change_language_keyboard(),
    )


@router.callback_query(F.data.startswith('change_lang_to_'))
async def handle_language_change(callback: CallbackQuery):
    if (callback.data is None) or (callback.bot is None):
        return

    new_language_code = callback.data.split('_')[-1]

    await db.change_user_language(callback.from_user.id, new_language_code)

    await callback.bot.send_message(
        chat_id=callback.from_user.id,
        text=await db.get_message('changed_language', new_language_code),
        parse_mode=BOT_MSG_PARSE_MODE,
        reply_markup=await get_main_keyboard(new_language_code),
    )

    await callback.answer()

    if callback.message is not None:
        await callback.message.delete()  # pyright: ignore


async def show_menu(user_id: int, bot: Bot):
    user = await db.get_user(user_id)

    if user is None:
        return

    await bot.send_message(
        chat_id=user_id,
        text=await db.get_message('view_menu', user.language_code),
        parse_mode=BOT_MSG_PARSE_MODE,
        reply_markup=await get_categories_keyboard(user.language_code),
    )


@router.callback_query(F.data.startswith('selected_category_'))
async def handle_category_selection(callback: CallbackQuery):
    if (callback.data is None) or (callback.bot is None):
        return

    user = await db.get_user(callback.from_user.id)

    if user is None:
        return

    product = await db.get_translated_adjacent_product(
        category=callback.data.split('_')[-1],
        current_id='000000000000000000000000',  # минимально возможный ObjectId
        direction=1,
        language_code=user.language_code,
    )

    if product is None:
        return

    await callback.bot.send_photo(
        chat_id=callback.from_user.id,
        photo=FSInputFile(f'./data/imgs/{product.photo_path}'),
        caption=product.to_string(),
        parse_mode='MarkdownV2',
        reply_markup=await get_keyboard_for_product(user.language_code, product),
    )

    await callback.answer()

    if callback.message is not None:
        await callback.message.delete()  # pyright: ignore


@router.callback_query(F.data.startswith('product_'))
async def handle_product_btns(callback: CallbackQuery):
    if (callback.data is None) or (callback.bot is None):
        return

    tokens = callback.data.split('_')
    action = tokens[1]

    if action == 'back-to-categories':
        await show_menu(callback.from_user.id, callback.bot)
        
        if callback.message is not None:
            await callback.message.delete()  # pyright: ignore
    
    elif action in ('prev', 'next'):
        direction = -1 if action == 'prev' else 1

        user = await db.get_user(callback.from_user.id)

        if user is None:
            return

        product = await db.get_translated_adjacent_product(
                category=tokens[2],
                current_id=tokens[3],
                direction=direction,
                language_code=user.language_code
            )
        
        if (product is not None) and (str(product.id) != tokens[3]):
            await callback.message.edit_media(  # pyright: ignore
                InputMediaPhoto(
                    media=FSInputFile(f'./data/imgs/{product.photo_path}'),
                    caption=product.to_string(),
                    parse_mode='MarkdownV2'
                ),
                reply_markup=await get_keyboard_for_product(language_code=user.language_code, product=product),
            )

    await callback.answer()
