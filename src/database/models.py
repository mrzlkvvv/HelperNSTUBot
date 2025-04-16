from bson import ObjectId

from pydantic import BaseModel, Field, ConfigDict
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError('Invalid ObjectId')


class LanguageNames(BaseModel):
    ru: str = 'Русский 🇷🇺'
    en: str = 'English 🇺🇸'


class Translations(BaseModel):
    ru: str
    en: str


assert set(LanguageNames.model_fields.keys()) == set(Translations.model_fields.keys()), \
    'Ключи LanguageNames и Translations не совпадают'


class User(BaseModel):
    _id: ObjectId
    language_code: str
    is_admin: bool


class Product(BaseModel):
    id: ObjectId = Field(..., alias='_id')
    category: str
    name: Translations
    ingredients: Translations
    photo_path: str
    cost: int

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


class TranslatedProduct(BaseModel):
    id: ObjectId = Field(..., alias='_id')
    category: str
    name: str
    ingredients: str
    photo_path: str
    cost: int

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )

    def to_string(self) -> str:
        return f'*{self.name} — {self.cost}₽*\n\n{self.ingredients}'


class Message(BaseModel):
    _id: ObjectId
    text: Translations
