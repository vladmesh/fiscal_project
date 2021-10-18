from enum import Enum


class ErrorType(Enum):
    ValidationError = 1
    ValueError = 2
    SystemError = 3


def decode_request(request):
    request = request.decode('utf-8')
    answer = ''
    for char in request:
        if char not in ('\r', '\n'):
            answer += char
    return answer


class ErrorHandler:

    async def handle(self, error_type: ErrorType, request, err: Exception, loggers: list):
        request = decode_request(request)
        error = MegapolisApiError(0, error_type, text, fields_list)
        error.error_id = await self.postgres_helper.insert_error(error, request)
        answer_schema = MegapolisApiAnswerSchema()
        answer_dict = {'status': MegapolisAnswerStatus.ERROR, 'timestamp': datetime.datetime.now(), 'error': error}
        answer_json = answer_schema.dumps(answer_dict)
        return aiohttp.web.Response(text=answer_json, content_type='application/json')
