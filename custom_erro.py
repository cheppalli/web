ERROR_CODE_MAPPING = {100:(400, 'Bad Request', 'Invalid Request. Please try with correct request')}

from collections import OrderedDict
def get_response(service_handler, error_code, error_msg=None):
    ret_dict = OrderedDict()
    error_detail = ERROR_CODE_MAPPING[error_code]
    ret_dict.setdefault('status', error_detail[0])
    ret_dict.setdefault('kind', error_detail[1])
    ret_dict.setdefault('method', service_handler.request.method)
    if error_msg:
        ret_dict.setdefault('message', error_msg)
    else:
        ret_dict.setdefault('message', error_detail[2])
    return {'response' : ret_dict}
