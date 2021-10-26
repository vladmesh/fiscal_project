import aiomysql
import asyncio
from core.utils import strip


class MySqlHelper:
    def __init__(self, host, database, login, password):
        self.host = host
        self.database = database
        self.login = login
        self.password = password
        self.connection = None
        self.cursor = None

    async def open_connection(self):
        loop = asyncio.get_event_loop()
        self.connection = await aiomysql.connect(user=self.login, password=self.password, host=self.host,
                                           db=self.database, loop=loop)
        self.cursor = await self.connection.cursor()

    async def close_connection(self):
        await self.cursor.close()
        self.connection.close()

    async def execute_query(self, query, has_result=True):
        answer = []
        await self.open_connection()

        await self.cursor.execute(query)
        if has_result:
            rows = await self.cursor.fetchall()
            for row in rows:
                record_dict = {}  # каждой записи сопоставляем словарь, типа {Имя колонки : значение}
                for i in range(len(self.cursor.description)):
                    record_dict[self.cursor.description[i][0]] = strip(row[i])
                answer.append(record_dict)
        await self.connection.commit()
        await self.close_connection()
        if has_result:
            return answer
