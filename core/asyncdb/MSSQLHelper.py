import asyncio
import sqlserverport
import aioodbc
from core.utils import strip


class MSSql:
    def __init__(self, server, database, user, password):
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.cursor = None
        self.loop = None
        if '\\' in server:
            # unixODBC не умеет распознавать имена инстансов, поэтому лезем каждый раз и тянем текущий порт
            # TODO  тут хорошо хотя бы научить по имени получать ip, так как ip может поменяться.
            # TODO для этого нужно разобраться, как внутрь контейнера пробросить информацию с ДНС сервера внутри сети
            pass
            servername = server.split('\\')[0].upper()
            domen = server.split('\\')[1].upper()
            server = '{0},{1}'.format(
                servername,
                sqlserverport.lookup(servername, domen))
        self.dsn = f'Driver=ODBC Driver 17 for SQL Server;Server={server};Database={database};UID={user};'

    async def open_connection(self):
        self.loop = asyncio.get_event_loop()
        self.connection = await aioodbc.connect(dsn=self.dsn, password=self.password,  loop=self.loop)
        self.cursor = await self.connection.cursor()

    async def close_connection(self):
        await self.cursor.close
        await self.connection.close()

    async def execute(self, command, has_result=True):
        answer = []
        await self.open_connection()
        await self.cursor.execute(command)
        if has_result:
            rows = await self.cursor.fetchall()
            for row in rows:
                record_dict = {}  # каждой записи сопоставляем словарь, типа {Имя колонки : значение}
                for i in range(len(self.cursor.description)):
                    record_dict[self.cursor.description[i][0]] = strip(row[i])
                answer.append(record_dict)
            return answer
        await self.close_connection()
