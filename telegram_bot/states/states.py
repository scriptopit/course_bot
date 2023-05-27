from aiogram.dispatcher.filters.state import State, StatesGroup


class SubscriptionState(StatesGroup):
    choose_sub_packet = State()


class AdminState(StatesGroup):
    add_new_channel = State()
    processing = State()
    receive_tag = State()
    check_data = State()
    get_user_info = State()
    choose_tag_user = State()
    deactivate_user = State()


class TicketStates(StatesGroup):
    open_ticket = State()
    input_ticket_info = State()
    accept_ticket = State()
