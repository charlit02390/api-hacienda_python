
import connexion
from service import cabys as service
from helpers import utils

# Searches for medicaments matching the received text
def search_meds():
    body = connexion.request.json
    response = service.search(body, service.Search.MEDS) # I'M BAD A NAMING THINGS
    return utils.build_response(response)


# Searches for cabys goods matching the received text
def search_cabys():
    body = connexion.request.json
    response = service.search(body, service.Search.CABYS)
    return utils.build_response(response)


# Finds SAC codes based on the Cabys code provided
def find_sacs_by_cabys():
    body = connexion.request.json
    response = service.find(body, service.Find.SACS)
    return utils.build_response(response)

def get(code: str):
    response = service.get(code)
    return utils.build_response(response)
