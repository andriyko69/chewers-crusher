import logging

from twitchio import Message, User
from twitchio.errors import HTTPException
from twitchio.ext import commands, routines

from decorators import channel_user
from services import is_adv_message_with_url_or_domain, is_rus_agro_message
from settings import (
    ACCESS_TOKEN,
    ALREADY_SHOUTED_OUT,
    INITIAL_CHANNELS,
    USERS_TO_SHOUTOUT,
)

LIST_TO_RESHOUTOUT = {}


# reshoutput only one user and remove it from the list
@routines.routine(minutes=2)
async def reshoutout(bot):
    logger.info("Reshouting out")
    for channel, users in LIST_TO_RESHOUTOUT.items():
        if users:
            user = users.pop(0)
            logger.info(f"[{channel.name}] Re-shouting out {user}")
            await bot.shoutout_user(channel, user)


logger = logging.getLogger()


class Bot(commands.Bot):
    def __init__(self):
        self.shouted_out: dict = ALREADY_SHOUTED_OUT
        self.fetched_users = {}
        self.user = None
        super().__init__(token=ACCESS_TOKEN, prefix="!", initial_channels=INITIAL_CHANNELS)

    async def get_user(self, user_name):
        if user_name in self.fetched_users:
            return self.fetched_users[user_name]

        users = await self.fetch_users([user_name])
        self.fetched_users[user_name] = users[0]
        return users[0]

    async def get_user_id(self, user_name):
        user = await self.get_user(user_name)
        return user.id

    async def ban_user(self, channel, user_id_to_ban, reason):
        await channel.ban_user(ACCESS_TOKEN, self.user.id, user_id_to_ban, reason)

    async def shoutout_user(self, channel, user_id_to_broadcast):
        await channel.shoutout(ACCESS_TOKEN, user_id_to_broadcast, self.user.id)

    async def event_ready(self):
        logger.info(f"Ready | {self.nick}")
        logger.info(f"Initial channels: {INITIAL_CHANNELS}")
        logger.info(f"Already shouted out: {ALREADY_SHOUTED_OUT}")
        self.user: User = await self.get_user(self.nick)

    async def event_message(self, message: Message):
        if message.echo or message.author.name == message.channel.name:
            return

        logger.info(f"[{message.channel.name}] {message.author.name}: {message.content}")

        await self.check_for_advertisements_and_ban(message)
        await self.check_for_agro_russian_messages_and_ban(message)
        await self.check_for_shoutout_and_shoutout(message)

    @channel_user
    async def check_for_advertisements_and_ban(self, message: Message, channel_user):
        if is_adv_message_with_url_or_domain(message.content) and message.first:
            logging.info(f"[{channel_user.name}] Banning {message.author.name}")
            user_id_to_ban = await self.get_user_id(message.author.name)
            return await self.ban_user(channel_user, user_id_to_ban, "Cheap viewers advertisement")

    @channel_user
    async def check_for_agro_russian_messages_and_ban(self, message: Message, channel_user):
        if is_rus_agro_message(message.content):
            logging.info(f"[{channel_user.name}] Banning {message.author.name}")
            user_id_to_ban = await self.get_user_id(message.author.name)
            return await self.ban_user(channel_user, user_id_to_ban, "Russian agro message")

    @channel_user
    async def check_for_shoutout_and_shoutout(self, message: Message, channel_user):
        message_author = message.author.name
        if any(
            (
                message_author in self.shouted_out.get(channel_user.name, []),
                message_author in LIST_TO_RESHOUTOUT.get(channel_user, []),
                message_author not in USERS_TO_SHOUTOUT,
            )
        ):
            return
        try:
            logger.info(f"[{channel_user.name}] Shouting out {message_author}")
            user_id_to_broadcast = await self.get_user_id(message_author)
            await channel_user.shoutout(ACCESS_TOKEN, user_id_to_broadcast, self.user.id)
        except HTTPException as e:
            logger.error(f"[{channel_user.name}] Error shouting out {message_author}: {e}")
            LIST_TO_RESHOUTOUT.setdefault(channel_user, []).append(message_author)
        else:
            self.shouted_out.setdefault(channel_user.name, []).append(message_author)


def main():
    try:
        bot = Bot()
        bot.run()
        reshoutout.start(bot)
    except (KeyboardInterrupt, RuntimeError):
        print("Exiting...")
        bot.close()


if __name__ == "__main__":
    main()
