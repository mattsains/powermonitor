import json


def createmessage(success, heading, message, code=0):
    """
    :param success: boolean value, did the request succeed?
    :param heading: string, heading of error
    :param message: a string message to display to user
    :param code: an integer code to style the message appropriately (maybe)
    :return: string, the message as json
    """
    content = {'heading': heading, 'success': success,  'message': message, 'code': code}
    #maybe the code property could affect a graphic or something if we don't use simple alerts

    return json.dumps(content)




