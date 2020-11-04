from traceback import format_exc
from smtplib import SMTPConnectError, SMTPNotSupportedError, SMTPAuthenticationError, SMTPSenderRefused, SMTPDataError, SMTPRecipientsRefused

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

    if 'message' in result:
        message = result['message']
        response['message'] = message if message else warn_msg


    if 'error' in result:
        error = result['error']
        response['http_status'] = result.get('http_status', error.get('http_status', 500))
        response['status'] = error.get('code', error.get('status', 400))
        response['detail'] = error.get('message', error.get('details', error_msg))
        if 'debug' in error:
            response['debug'] = error['debug']
    elif 'data' in result:
        response['data'] = result['data']


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


def run_and_summ_collec_job(collec_cb, item_cb,
                                     item_id_key, collec_cb_args = (),
                                     collec_cb_kwargs = {},
                                     item_cb_kwargs_map = {}):
    try:
        collection = collec_cb(*collec_cb_args,
                               **collec_cb_kwargs)
    except Exception:
        return """***Could not fetch collection:***
Collection callback: {}
Callback Args: {}
Callback Kwargs: {}
{}
""".format(collec_cb.__qualname__, collec_cb_args,
           collec_cb_kwargs, format_exc())

    summary = {
        'success': 0,
        'errors': []
        }
    param_names = item_cb_kwargs_map.keys()
    item_keys = item_cb_kwargs_map.values()
    for item in collection:
        params = dict(zip(param_names, (item[key] for key in item_keys)))
        try:
            item_cb(**params)
            summary['success'] += 1
        except Exception:
            summary['errors'].append("""***An exception was found:***
Item Id: {}
Callback: {}
Params: {}
{}
""".format(item[item_id_key], item_cb.__qualname__,
           params, format_exc()))

    summary_str = """-Successful counter: {}
-Errors ({}):
""".format(summary['success'], len(summary['errors']))
    
    summary_str += '\n'.join(summary['errors'])

    return summary_str


def get_smtp_error_code(exception: Exception):
    if isinstance(exception, SMTPConnectError):
        return 1
    if isinstance(exception, SMTPNotSupportedError):
        return 2
    if isinstance(exception, SMTPAuthenticationError):
        return 3
    if isinstance(exception, SMTPSenderRefused):
        return 4
    if isinstance(exception, SMTPDataError):
        return 5
    if isinstance(exception, SMTPRecipientsRefused):
        return 6
    else:
        return -1
