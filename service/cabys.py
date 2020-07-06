
import json
import re
from enum import Enum
# import messages #maybe make something with constants that translate into user messages...?
from infrastructure import cabys


# Enums for memes... I mean, maps an enum value to a function from infrastructure
class Search(Enum):
    MEDS = cabys.search_meds
    CABYS = cabys.search_cabys


class Find(Enum):
    SACS = cabys.find_sacs

# Defines a minimum length for the search query sent by the user for searching
_MIN_LENGTH = 3


# Takes a "query" string and formats (not right now...) it to be used as a pattern for searching.
# Then, dispatches it to the correct function based on "where"...
def search(data, where):
    response = {'status' : 204, 'body' : None }
    # I think I'm already checking this in the yaml, but might as well...
    if 'query' in data:
        _query = data['query'].strip()
        # Serve queries that conform to the minimal length
        if len(_query) >= _MIN_LENGTH:
            # Search. Asume all good
            # Dispatch to proper method depending on "where"
            result = where(format(_query))
            response = buildResponse(result, 'No matches were found for the query "' + _query + '".')

    else:
        response = {'status' : 400, 'body' : [], 'error':'Error: there was no query specified in the request\'s body.'}


    return response


# Finds (? should just be Get, prolly... dunno... whatvs) an identifier in the requested place/collection/infrastructure function... I don't know...
def find(data, where):
    response = {'status' : 200, 'body' : None}
    # Better safe than sorry...?
    if 'cabys' in data:
        _code = data['cabys'].strip()
        # Go. Dispatch the "where" method
        result = where(_code)
        response = buildResponse(result, 'The requested Cabys code "' + _code + '" was not found.')

    else:
        response = {'status' : 400, 'body' : [] , 'error':'Error: there was no Cabys code specified in the request\'s body.'}


    return response


# Formats a query into a Regular Expression matching pattern... maybe...
def format(query):
    # dunno what to do here, so just trying stuff. Better find a more efficient way
    # what a mess... meh, will look up into this better some other time...
    separator = '|';

    # le pattern
    pattern = re.compile(r'["](.*?)["]')

    # Get all parts enclosed in double quotes
    quotedParts = pattern.findall(query)

    # Get all parts NOT enclosed in double quotes...
    queryNonQuotedParts = pattern.sub('', query)

    # Since these might mean different keywords, gotta split them with a whitespace
    explodedquery = queryNonQuotedParts.split(' ');

    # Clean any empty strings
    cleanerexplosion = [string for string in explodedquery if string != ""]

    # Join dem arrays
    joinedParts = cleanerexplosion + quotedParts

    # Join them into a string separated by '|' for regexp "or"
    formattedQuery = separator.join(joinedParts) # Hopefully this is it, and I'm done here

    # le debug
    print(formattedQuery)

    return formattedQuery # flush this trash


# Builds a response with an empty array as body. Optionally receives warning and error messages to set
def buildResponse(result, warningmsg = None, errormsg = None):
    response = {'status' : 200, 'body' : []}

    # Error happened? Set error message and status code
    if '_error' in result:
        response['error'] = errormsg or result['_error']
        response['status'] = 500

    # Warning prompted? Set a nice message
    elif '_warning' in result:
        response['message'] = warningmsg or result['_warning']

    # All good? Valid body, therefore set it
    else:
        response['body'] = result

    return response
