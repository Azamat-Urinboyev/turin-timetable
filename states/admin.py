from aiogram.fsm.state import State, StatesGroup


class Admin(StatesGroup):
    message = State()