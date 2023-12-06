# -*- coding: utf-8 -*-
# @author: zelenka.guru/zcxw

import asyncio

class Threads:
    def __init__(self):
        self.run_threads = []
        self.main_loop = asyncio.new_event_loop()
        
        self.main_loop.set_exception_handler(handler=lambda *a: True)
        asyncio.set_event_loop(self.main_loop)

    def thread_wait(self, coro, **kwargs):
        self.main_loop.run_until_complete(coro(**kwargs))

    def add_thread(self, coro, **kwargs):
        task: asyncio.Task = asyncio.ensure_future(coro(**kwargs))
        task.add_done_callback(self._callback_task_end)
        self.run_threads.append(task)
        return task

    def terminate(self, task: asyncio.Task):
        if not task.cancelled():
            return task.cancel()
        try:
            self.run_threads.remove(task)
        except Exception:
            pass

    def wait_time(self, delay: float):
        self.main_loop.run_until_complete(asyncio.sleep(delay))

    def terminate_all(self):
        for task in self.run_threads:
            try:
                self.terminate(task)
            except Exception:
                pass

    def _callback_task_end(self, task: asyncio.Task):
        try:
            self.run_threads.remove(task)
        except Exception:
            pass
