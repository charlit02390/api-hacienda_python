
import json
import re
from enum import Enum
# import messages #maybe make something with constants that translate into user messages...?
from infrastructure import cabys
from helpers import errors, utils
from flask import g


# Enums for memes... I mean, maps an enum value to a function from infrastructure
class Search(Enum):
    MEDS = cabys.search_meds
    CABYS = cabys.search_cabys


class Find(Enum):
    SACS = cabys.find_sacs

# Defines a minimum length for the search query sent by the user for searching
_MIN_LENGTH = 3


# Takes a "query" string and formats it to be used as a pattern
# for searching.
# Then, dispatches it to the correct function based on "where"...
def search(data, where):
    # I think I'm already checking this in the yaml, but might as well...
    if 'query' in data:
        _query = data['query'].strip()
        # Serve queries that conform to the minimal length
        if len(_query) >= _MIN_LENGTH:
            # Search. Asume all good
            # Dispatch to proper method depending on "where"
            result = {'data' : where(format(_query))}

    else:
        error = { 'message' : "There was no query specified in the request's body.",
                 'code' : 21 }
        result = {'http_status' : 400,
                  'error': error }

    response = utils.build_response_data(
        result,
        warn_msg=(
            'No matches were found for the query "{}".'
            ).format(_query))
    return response


# Finds (? should just be Get, prolly... dunno... whatvs) an
# identifier in the requested place/collection/infrastructure
# function... I don't know...
def find(data, where):
    # Better safe than sorry...?
    if 'cabys' in data:
        _code = data['cabys'].strip()
        # Go. Dispatch the "where" method
        result = { 'data' : where(_code)}


    else:
       error = { 'message' : "There was no Cabys code specified in the request's body.",
                'code': 21} 
       result = {'http_status' : 400,
                 'error': error }

    response = utils.build_response_data(
        result,
        warn_msg=(
            'The requested Cabys code "{}" was not found.'
        ).format(_code))
    return response


def get(code: str):
    cabys = cabys.select(code)
    if not cabys:
        return utils.build_response_data(
            {
                'http_status': 404,
                'error': {
                    'message': (
                        'No cabys was found for code {}.'
                        ).format(code),
                    'code': 21
                }
            }
        )
    
    return utils.build_response_data({
        'data': cabys
    })


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

