from aiogram.dispatcher.filters.state import State, StatesGroup


class SubscriptionState(StatesGroup):
    choose_sub_packet = State()
