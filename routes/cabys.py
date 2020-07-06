
import connexion
from service import cabys as service


# Searches for medicaments matching the received text
def search_meds():
    body = connexion.request.json;
    stuff = service.search(body, service.Search.MEDS) # I'M BAD A NAMING THINGS
    response = prepareResponse(stuff, 'medicamentos')
    return response, stuff['status'];


# Searches for cabys goods matching the received text
def search_cabys():
    body = connexion.request.json;
    stuff = service.search(body, service.Search.CABYS)
    response = prepareResponse(stuff, 'cabys')
    return response, stuff['status']


# Finds SAC codes based on the Cabys code provided
def find_sacs_by_cabys():
    body = connexion.request.json;
    stuff = service.find(body, service.Find.SACS)
    response = prepareResponse(stuff, 'cabysxsac')
    return response, stuff['status']


# Prepares the response to be sent with random stuff... ugh, I need to find a better way or place to do this...
def prepareResponse(stuff, mainpropertyname):
    response = {mainpropertyname : stuff['body']}

    if 'error' in stuff:
        response['error'] = stuff['error']

    if 'message' in stuff:
        response['message'] = stuff['message']

    return response
