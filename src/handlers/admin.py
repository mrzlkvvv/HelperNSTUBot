from aiogram import Router

from middlewares import AdminMiddleware


router = Router()
router.message.middleware(AdminMiddleware())

