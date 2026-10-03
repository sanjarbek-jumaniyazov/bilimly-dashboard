from aiogram import Router

from . import start, admin

router = Router()
router.include_router(start.router)
router.include_router(admin.router)
