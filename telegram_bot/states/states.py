from aiogram.dispatcher.filters.state import State, StatesGroup


class SubscriptionState(StatesGroup):
    choose_sub_packet = State()


class AdminState(StatesGroup):
    add_new_channel = State()
    processing = State()
    receive_tag = State()
    check_data = State()
