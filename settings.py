import logging

from environs import Env

env = Env()
env.read_env()

DEBUG = env.bool("DEBUG", False)

LOGGER_TIME_FORMAT = "%H:%M:%S"
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)
logger = logging.getLogger()
if logger.hasHandlers():
    logger.removeHandler(logger.handlers[0])
    handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt="[%(asctime)s] %(levelname)s - %(message)s", datefmt=LOGGER_TIME_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

ACCESS_TOKEN = env.str("ACCESS_TOKEN")
logger.debug(f"ACCESS_TOKEN: {ACCESS_TOKEN}")

INITIAL_CHANNELS = env.list("INITIAL_CHANNELS")
logger.debug(f"INITIAL_CHANNELS: {INITIAL_CHANNELS}")

MIN_SIMILARITY_RATIO = env.int("MIN_SIMILARITY_RATIO")
logger.debug(f"MIN_SIMILARITY_RATIO: {MIN_SIMILARITY_RATIO}")

AGROWORDS = env.list("AGROWORDS")
logger.debug(f"AGROWORDS: {AGROWORDS}")

USERS_TO_SHOUTOUT = env.list("USERS_TO_SHOUTOUT")
logger.debug(f"USERS_TO_SHOUTOUT: {USERS_TO_SHOUTOUT}")

ALREADY_SHOUTED_OUT = env.json("ALREADY_SHOUTED_OUT")
logger.debug(f"ALREADY_SHOUTED_OUT: {ALREADY_SHOUTED_OUT}")
