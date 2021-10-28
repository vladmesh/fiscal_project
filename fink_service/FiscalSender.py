import asyncio
import logging




class FiscalSender:
    def __init__(self):
        pass

    async def send_ticket(self, ticket: Ticket):
        logging.info(f"Отправляем билет {ticket}")
        await asyncio.sleep(5)
        answer = {'status': 'wait', 'uuid': ticket}
        return answer

    async def get_document(self, uid):
        pass
