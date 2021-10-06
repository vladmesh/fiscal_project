from aiohttp.web import Response


async def get_token(request):
    return Response(text='{"token": "testtoken"}', content_type='application/json')
