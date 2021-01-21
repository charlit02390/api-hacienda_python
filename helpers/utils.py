from traceback import format_exc
from smtplib import SMTPConnectError, SMTPNotSupportedError, SMTPAuthenticationError, SMTPSenderRefused, SMTPDataError, SMTPRecipientsRefused

from flask import jsonify

from .errors.enums import InternalErrorCodes

def build_response_data(result: dict,
                        warn_msg: str = 'No data was found',
                        error_msg: str = ('An issue was found'
                                          ' and the application had'
                                          ' to be stopped.')) -> dict:
    """
    Builds data for a response from the given result.
    
    Expects three main properties on "result":

        - 'message' - a string containing a message
           informing the client about the action taken
           by their request.
        - 'error'|'unexpected' - a dictionary with an
           'errorcode', 'message' and 'debug' to be
           relayed to the client.
        - 'data' - the data requested by the client.
        
    A property 'http_status' can be used to set an
        HTTP Status for the response, but will only be set
        for errors. Default is 200.
    A property 'headers' with a dictionary can be set to
        send headers to the client.

    Optionally, receives strings for warning and/or error
        messages to be set.

    :param result: dict - a dictionary with possible data for
        the response body.
    :param warn_msg: [optional] str - a warning message to
        be displayed if a warning was triggered.
    :param error_msg: [optional] str - an error message to be
        displayed if an error was raised.
    :returns: dict - A dictionary with data to be used to
        generate a proper response.
    """
    response = {'http_status' : 200,
                'status' : 0 }

    if 'message' in result:
        message = result['message']
        response['message'] = message if message else warn_msg


    if 'error' in result:
        error = result['error']
        response['http_status'] = result.get('http_status',
                                             error.get('http_status', 500))
        response['status'] = error.get('code',
                                       error.get('status',
                                                 InternalErrorCodes.INTERNAL_ERROR
                                                 )
                                       )
        response['detail'] = error.get('message',
                                       error.get('detail',
                                                 error.get('details',
                                                           error_msg
                                                           )
                                                 )
                                       )
        if 'debug' in error:
            response['debug'] = error['debug']

    elif 'unexpected' in result: # meh
        unexpected = result['unexpected']
        response['http_status'] = unexpected['status']
        response['status'] = InternalErrorCodes.HACIENDA_ERROR
        response['detail'] = """Unexpected Response from Hacienda.
Reason: {}
Content: {}""".format(unexpected['reason'],
                      unexpected['content'])

    elif 'data' in result:
        response['data'] = result['data']


    if 'headers' in result:
        headers = result['headers']
        if headers and isinstance(headers, dict):
            response['headers'] = headers


    return response


def build_response(data: dict):
    """
    Builds a flask response object that can be returned
    to the flask framework to be dispatched to the client.

    Basically, if "data" doesn't have an 'http_status'
    and/or 'headers' properties, data is jsonify-ied and
    returned.
    Else, the properties 'headers' and 'http_status' will be
    popped from "data" and a response object will be build
    by jsonify-ing "data" and setting 'headers' and
    'http_status' if they were successfully popped.

    :param data: dict - data to be converted into a response.
    :returns: flask.Response - a Response object to be
        dispatched to the client.
    """

    if 'http_status' not in data and 'headers' not in data:
        return jsonify(data)

    http_status = None
    if 'http_status' in data:
        http_status = data.pop('http_status')

    headers = None
    if 'headers' in data:
        headers = data.pop('headers')

    response = jsonify(data)

    if http_status is not None:
        response.status_code = http_status

    if headers is not None:
        response.headers = headers

    return response


def run_and_summ_collec_job(collec_cb, item_cb,
                                     item_id_keys, collec_cb_args = (),
                                     collec_cb_kwargs=None,
                            item_cb_kwargs_map=None):
    """
    Very generic function that runs functions designed as
    scheduled jobs and summarizes their results.

    :param collec_cb: callable - a callback that returns an
        iterable of data to be consumed by "item_cb".
    :param item_cb: callable - a callback to use for the
        entries from "collec_cb" to process them.
    :param collec_cb_args: [optional] tuple - a tuple with
        parameters to be sent to "collec_cb".
    :param collec_cb_kwargs: [optional] dict - a dictionary
        mapping the keyword arguments that "collec_cb"
        would receive.
    :param item_cb_kwargs_map: [optional?] dict - a
        dictionary that maps an entry from "collec_cb"'s
        properties to keyword arguments for "item_cb".

    :returns: str - a string with a summary for the
        executed operations.
    """
    if item_cb_kwargs_map is None:
        item_cb_kwargs_map = {}
    if collec_cb_kwargs is None:
        collec_cb_kwargs = {}
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
        params = dict(zip(param_names,
                          (item[key] for key in item_keys)))
        try:
            item_cb(**params)
            summary['success'] += 1
        except Exception:
            summary['errors'].append("""***An exception was found:***
Item Id: {}
Callback: {}
Params: {}
{}
""".format(item[item_id_keys] if isinstance(item_id_keys, str) \
    else (', '.join(item[key] for key in item_id_keys)),
           item_cb.__qualname__,
           params, format_exc()))

    summary_str = """-Successful counter: {}
-Errors ({}):
""".format(summary['success'], len(summary['errors']))
    
    summary_str += '\n'.join(summary['errors'])

    return summary_str


def get_smtp_error_code(exception: Exception):
    """
    Function that returns a code depending on the specific
    type of SMTPException the parameter "exception" is.

    @todo: Enum the codes...
    """
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
