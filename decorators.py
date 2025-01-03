from twitchio.message import Message


def channel_user(message_handler):
    async def wrapper(self, message: Message):
        channel_user = await self.get_user(message.channel.name)
        return await message_handler(self, message, channel_user)

    return wrapper


def lower_message(message_handler):
    def wrapper(message: str):
        return message_handler(message.lower())

    return wrapper
