from bson import ObjectId
from typing import Optional, Literal
from motor.motor_asyncio import AsyncIOMotorClient

import config

from .models import TranslatedProduct, Translations, User, Product, Message


class Database:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'client'):
            self.client = AsyncIOMotorClient(config.MONGO_DSN)
            self.db = self.client[config.MONGO_DB_NAME]

    def _translate(self, translations: Translations, language_code: str) -> str:
        return getattr(translations, language_code, translations.ru)

    async def get_user(self, user_id: int) -> Optional[User]:
        user = await self.db.users.find_one({'_id': user_id})
        return User(**user) if user else None
        user = await self.db.users.find_one({'_id': user_id})
        return user is not None

    async def add_user(self, user_id: int, language_code: str = 'ru') -> None:        
        user_data = {
            '_id': user_id,
            'language_code': language_code,
            'is_admin': False,
        }
        
        await self.db.users.insert_one(user_data)

    async def change_user_language(self, user_id: int, new_language_code: str) -> None:
        await self.db.users.update_one(
            {'_id': user_id},
            {'$set': {'language_code': new_language_code}}
        )

    async def get_message(self, message_id: str, language_code: str) -> str:
        message = await self.db.messages.find_one({'_id': message_id})

        if message is None:
            return ''

        translations = Message(**message).text

        # return getattr(translations, language_code, translations.ru)
        return self._translate(translations, language_code)
        
    async def _get_adjacent_product(
            self,
            category: str,
            current_id: str,
            direction: Literal[1, -1],  # 1 => next, -1 => previous
        ) -> Optional[Product]:

        current_obj_id = ObjectId(current_id)
        
        # Пытаемся получить соседний элемент
        adjacent = await self.db.products.find_one({
            'category': category,
            '_id': {'$gt' if direction > 0 else '$lt': current_obj_id}
        }, sort=[('_id', direction)])
        
        if adjacent:
            return Product(**adjacent)
        
        # Если не нашли - берем крайний элемент с противоположного конца
        opposite = await self.db.products.find_one(
            {'category': category},
            sort=[('_id', direction)]
        )
        
        return Product(**opposite) if opposite else None

    async def get_translated_adjacent_product(
            self,
            category: str,
            current_id: str,
            direction: Literal[1, -1],  # 1 => next, -1 => previous
            language_code: str,
        ) -> Optional[TranslatedProduct]:

        product = await self._get_adjacent_product(category, current_id, direction)

        if product is None:
            return None

        return TranslatedProduct(
            id=product.id,
            category=product.category,
            name=getattr(product.name, language_code, product.name.ru),
            ingredients=getattr(product.ingredients, language_code, product.ingredients.ru),
            photo_path=product.photo_path,
            cost=product.cost,
        )
