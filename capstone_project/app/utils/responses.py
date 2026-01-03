def make_response(data=None, message=None, error=None, status_code=200, status=None):
    if status is not None:
        status_code = status

    payload = {}

    if message is not None:
        payload["message"] = message
    if data is not None:
        payload["data"] = data
    if error is not None:
        payload["error"] = error

    return payload, status_code
