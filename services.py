import logging

from fuzzywuzzy import fuzz
from validators import domain as validate_domain
from validators import url as validate_url

from decorators import lower_message
from settings import AGROWORDS, MIN_SIMILARITY_RATIO

logger = logging.getLogger(__name__)


def is_adv_message(adv_templ, message):
    logger.debug(f"Checking if '{message}' is an advertisement for '{adv_templ}'")
    return any([fuzz.ratio(adv_templ, " ".join(message.split()[:2])) >= MIN_SIMILARITY_RATIO])


def has_url_or_domain(message):
    logger.debug(f"Checking if '{message}' has a URL or domain")
    return any([validate_url(word) or validate_domain(word) for word in message.split()])


@lower_message
def is_adv_message_with_url_or_domain(message):
    adv_templ = ("cheap viewers", "best v̐iewers ͚on")
    return any([is_adv_message(adv, message) and has_url_or_domain(message) for adv in adv_templ])


@lower_message
def is_agro_message(message):
    return any([word in message for word in AGROWORDS])
