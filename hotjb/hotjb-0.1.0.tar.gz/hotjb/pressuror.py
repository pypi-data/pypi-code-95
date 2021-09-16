from time import time_ns
from asyncio.tasks import as_completed
from .client import HotJBClient

class HotJBPressuror:
    '''
    '''

    def __init__(self, logger, host='127.0.0.1', port=30000):
        '''
        '''

        self.logger = logger
        self.client = HotJBClient(
            host=host,
            port=port
        )

    async def pressure(self, batch_size=100, total_count=10000):
        '''
        '''

        total_start_time = time_ns()
        total_done_count = 0
        total_pending_count = 0
        for j in range(0, total_count, batch_size):
            k = j + batch_size
            start_time = time_ns()
            self.logger.info(f'batch start: [{j} - {k}] / {total_count}')
            tasks = []
            for i in range(batch_size):
                task = self.client.tokenize(f'{i}个中文分词库')
                tasks.append(task)

            done_count = 0
            pending_count = 0
            for task in as_completed(tasks):
                try:
                    self.logger.debug(await task)
                    done_count += 1
                except Exception as e:
                    self.logger.error(e)
                    pending_count += 1
            end_time = time_ns()
            duration = (end_time - start_time) / 1000000000.0
            self.logger.info(f'batch end: [{j} - {k}] / {total_count} | time: {duration}s | done: {done_count} | pending: {pending_count}')
            total_done_count += done_count
            total_pending_count += pending_count
        total_end_time = time_ns()
        total_duration = (total_end_time - total_start_time) / 1000000000.0
        self.logger.info(f'[total] | time: {total_duration}s | done: {total_done_count} | pending: {total_pending_count}')
            
