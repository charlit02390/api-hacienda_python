
import connexion

from service import message as model_message
from helpers.utils import build_response
from helpers.debugging import set_debug_mode

def create_message():
    body = connexion.request.json
    result = model_message.create(body)
    return build_response(result)


def process_message(key: str):
    result = model_message.process_message(key)
    return build_response(result)
