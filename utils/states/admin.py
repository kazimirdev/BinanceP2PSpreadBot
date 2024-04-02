from aiogram.fsm.state import State, StatesGroup

class SpreadLimit(StatesGroup):
    UsingData = State()
    UpdatingLimit = State()

