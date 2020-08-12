
import connexion
from service import cabys as service
from service import utils

# Searches for medicaments matching the received text
def search_meds():
    body = connexion.request.json
    stuff = service.search(body, service.Search.MEDS) # I'M BAD A NAMING THINGS
    response = utils.prepareResponse('medicamentos', stuff)
    return response, stuff['httpstatus']


# Searches for cabys goods matching the received text
def search_cabys():
    body = connexion.request.json;
    stuff = service.search(body, service.Search.CABYS)
    response = utils.prepareResponse('cabys', stuff)
    return response, stuff['httpstatus']


# Finds SAC codes based on the Cabys code provided
def find_sacs_by_cabys():
    body = connexion.request.json
    stuff = service.find(body, service.Find.SACS)
    response = utils.prepareResponse('cabysxsac', stuff)
    return response, stuff['httpstatus']
