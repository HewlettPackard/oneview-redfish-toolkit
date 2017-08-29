class OneViewRedfishError(Exception):
    def __init__(self, msg):
        self.msg = msg

class OneviewRedfishResourceNotFoundError(OneViewRedfishException):
    def __init__(self, res_name, rest_type)
        self.msg = "{} {} not found".format(res_type, res_name)

class OneviewRedfishResourceNotAccessibleError(OneViewRedfishException):
    def __init__(self, res_name, rest_type)
        self.msg = "Can't access {} {}".format(res_type, res_name)
    