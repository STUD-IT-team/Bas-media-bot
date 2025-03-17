import asyncio

from keyboards.default.admin import AdminDefaultKeyboard
from keyboards.default.member import MemberDefaultKeyboard
from handlers.state import MemberStates, AdminStates
from models.activist import Activist, Admin

from aiogram.types import Message
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext




async def TransitToMemberDefault(message: Message, state: FSMContext, activist: Activist):
    await state.clear()
    await state.set_data({"user-type": "activist"})
    await state.set_state(MemberStates.Default)
    await message.answer(f"Активист, {activist.Name}! Что хотите сделать?", reply_markup=MemberDefaultKeyboard.Сreate())


async def TransitToAdminDefault(message: Message, state: FSMContext, admin: Admin):
    await state.clear()
    await state.set_data({"user-type": "admin"})
    await state.set_state(AdminStates.Default)
    await message.answer(f"Админ, {admin.Name}! Что хотите сделать?", reply_markup=AdminDefaultKeyboard.Сreate())

async def TransitToUnauthorized(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Не могу найти вас в своих базах, если это ошибка - напишите администратору", reply_markup=ReplyKeyboardRemove())



