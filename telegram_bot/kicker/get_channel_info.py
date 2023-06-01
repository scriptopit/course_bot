import loguru
from telethon import TelegramClient

from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.types import PeerChannel

from config import API_ID, API_HASH, SESSION_STRING


async def get_channel_data(user_input_channel: str) -> dict[int, dict]:
    """
     Returns dictionary with channel users data
     user_input_channel: ID of channel without head "-100"
    """

    async with TelegramClient(StringSession(SESSION_STRING), int(API_ID), str(API_HASH)) as client:
        await client.start()
        print("Client Created!")

        if user_input_channel.isdigit():
            entity = PeerChannel(int(user_input_channel))
        else:
            entity = user_input_channel

        my_channel = await client.get_entity(entity)

        offset = 0
        limit = 100
        all_participants = []

        while True:
            participants = await client(GetParticipantsRequest(
                my_channel, ChannelParticipantsSearch(""), offset, limit,
                hash=0
            ))

            if not participants.users:
                break
            all_participants.extend(participants.users)
            offset += len(participants.users)

        all_user_details: dict[int, dict] = {
            participant.id:
                {
                    "id": participant.id,
                    "first_name": participant.first_name,
                    "last_name": participant.last_name,
                    "user": participant.username,
                    "phone": participant.phone,
                    "is_bot": participant.bot
                }
            for participant in all_participants
            if not participant.bot
        }

    return all_user_details


async def get_helper_channel_data(ticket_chat: int):
    """
     Returns dictionary with new answered ticket
    """

    async with TelegramClient(StringSession(SESSION_STRING), int(API_ID), str(API_HASH)) as client:
        await client.start()

        my_channel = await client.get_entity(ticket_chat)
        all_messages = []

        ticket = None
        answer = None

        async for message in client.iter_messages(my_channel):
            if message.reply_to:
                ticket_message_id = message.reply_to.reply_to_msg_id
                answer_message_id = message.id

                all_messages.extend([ticket_message_id, answer_message_id])

                example_ticket = await client.get_messages(my_channel, ids=ticket_message_id)
                example_answer = await client.get_messages(my_channel, ids=answer_message_id)
                if example_answer and example_ticket:
                    ticket = example_ticket.message
                    answer = example_answer.message

                break

        await client.delete_messages(entity=my_channel, message_ids=all_messages)
        return [ticket, answer]












