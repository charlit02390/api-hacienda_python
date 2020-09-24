

def build_response_data(result: dict, warn_msg: str = 'No data was found', error_msg: str = 'An issue was found and the application had to be stopped.') -> dict:
    """
    Builds data for a response from the given result.
    
    Expects three main properties on "result":
        'data' - the data requested by the client
        'message' - a string containing a message informing the client about the action taken by their request
        'error' - a dictionary with an 'errorcode', 'message' and 'debug' to be relayed to the client.
    A property 'http_status' can be used to set an HTTP Status for the response, but will only be set for errors. Default is 200
    A property 'headers' with a dictionary can be set to send headers to the client.

    Optionally, receives strings for warning and/or error messages to be set.

    :param result: dict - a dictionary with possible data for the response body.
    :param warn_msg: [optional] str - a warning message to be displayed if a warning was triggered.
    :param error_msg: [optional] str - an error message to be displayed if an error was raised.
    :returns: dict - A dictionary with data to be used to generate a proper response.
    """
    response = {'http_status' : 200,
                'status' : 0 }

    if 'error' in result:
        error = result['error']
        response['http_status'] = result['http_status'] if 'http_status' in result else 500
        response['status'] = error['code'] if 'code' in error else 400
        response['error'] = error['message'] if 'message' in error else error_msg
        if 'debug' in error:
            response['debug'] = error['debug']
    elif 'data' in result:
        data = result['data']
        if data:
            response['data'] = data
        else:
            response['message'] = warn_msg
    elif 'message' in result:
        message = result['message']
        response['message'] = message if message else warn_msg
    else:
        response['message'] = warn_msg

    if 'headers' in result:
        headers = result['headers']
        if headers and isinstance(headers, dict):
            response['headers'] = headers

    return response


def build_response(data: dict):
    """Builds a value that can be returned to the flask framework to be converted into a response.

    Basically, if "data" doesn't have an 'http_status' and/or 'headers' properties,
    data is returned as is. Else, a tuple will be returned in the form of either:
    (data, http_status), (data, headers) or (data, http_status, headers)

    :param data: dict - data to be converted into a return value for making a response.
    """
    if not 'http_status' in data and not 'headers' in data:
        return data

    elements = [data]
    if 'http_status' in data:
        elements.append(data.pop('http_status'))

    if 'headers' in data:
        elements.append(data.pop('headers'))

    return tuple(elements)
