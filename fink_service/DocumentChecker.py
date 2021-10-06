import asyncio
import logging


class DocumentChecker:
    def __init__(self):
        pass

    async def check_uid(self, uid):
        await asyncio.sleep(5)
        logging.info(f"проверяем документ {uid}")
