import asyncio

import aioodbc
from core.utils import strip


class MSSql:
    def __init__(self, server, database, user, password):
        self.database = database
        self.user = user
        self.password = password
        self.server = server
        self.connection = None
        self.cursor = None
        self.loop = None
        self.dsn = f'Driver=ODBC Driver 17 for SQL Server;Server={server};Database={database};UID={user};' \
                   f'PWD={password}'
    
    async def open_connection(self):
        self.loop = asyncio.get_event_loop()
        self.connection = await aioodbc.connect(dsn=self.dsn, loop=self.loop)
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

    

    




class MSsqlOLEDB:
    def __init__(self, host, db_name):
        self.host = host
        self.db_name = db_name
        self.connection = None

    def open_connection(self):
        self.connection = adodbapi.connect("PROVIDER=SQLOLEDB;Data Source={0};Database={1};"
                                           "trusted_connection=yes;Timeout=500;ConnectTimeout=500;".format(self.host, self.db_name))
        self.connection.CommandTimeout = 5000
        self.connection.timeout = 5000

    def close_connection(self):
        self.connection.close()

    def execute(self, command, has_answer=True):
        self.open_connection()
        answer = None
        cursor = self.connection.cursor()
        cursor.execute(command)
        if has_answer:
            col_names = [i[0] for i in cursor.description]
            rows = cursor.fetchall()
            answer = [dict(zip(col_names, record)) for record in rows]
        self.connection.commit()
        self.close_connection()
        return answer


