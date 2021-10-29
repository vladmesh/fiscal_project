import cx_Oracle
import asyncio
import concurrent.futures

# TODO Тут бы тоже нужно какую-то асинхронную либу, но у меня не получилось подключиться ни через cx_Oracle_async,
# TODO ни через aioodbc

class OracleHelper:
    def __init__(self, conn_string):
        self.connString = conn_string
        self.conn = None
        self.cursor = None

    def open(self):
        try:
            self.conn = cx_Oracle.connect(self.connString)
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(e)

    def close(self):
        self.cursor.close()
        self.conn.close()

    def execute(self, command, has_result=True):
        records = []
        col_names = []
        self.open()
        self.cursor.execute(command)
        if has_result:
            records = self.cursor.fetchall()
            col_names = [x[0] for x in self.cursor.description]
        self.close()
        if has_result:
            return [dict(zip(col_names, record)) for record in records]


async def main():
    loop = asyncio.get_running_loop()
    helper = OracleHelper('fiscal/_si3dgzp4cjxb6d07t891rv3@10.2.54.10:1545/TRCARD')

    # 2. Run in a custom thread pool:
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool, helper.execute, "select 1;")
        print('custom thread pool', result)


asyncio.run(main())