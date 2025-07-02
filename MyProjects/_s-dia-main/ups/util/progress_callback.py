from typing import Callable
from dask.callbacks import Callback


class ProgressCallback(Callback):
    def __init__(self, callback: Callable, loop_count: int = 1, loop_compute_count: int = 1):
        self.callback = callback
        self.total_tasks = 0
        self.completed_tasks = 0
        self.loop_count = loop_count
        self.loop_compute_count = loop_compute_count
        self.current_schedule = 0
        self.current_schedule_tasks = 0
        self.total_schedules = loop_count * loop_compute_count

    def _start(self, dsk):
        self.current_schedule += 1
        self.current_schedule_completed_tasks = 0
        self.current_schedule_tasks = len(dsk)
        self.total_tasks += self.current_schedule_tasks

        # self.callback(
        #     f'start: {self.schedule_no}: {self.completed_tasks} / {self.total_tasks} / {self.loop_compute_count} / {self.loop_count}'
        # )

    def _posttask(self, key, result, dsk, state, worker_id):
        self.current_schedule_completed_tasks += 1
        self.completed_tasks += 1
        # progress_percent = self.completed_tasks / self.total_tasks * 100 / self.job_count
        # progress_status = {
        #     'loop_count': self.loop_count,
        #     'loop_compute_count': self.loop_compute_count,
        #     'schedule_no': self.schedule_no,
        #     'schedule_tasks': self.schedule_tasks,
        #     'total_tasks': self.total_tasks,
        #     'completed_tasks': self.completed_tasks,
        # }
        self.callback(
            {
                'current_schedule': self.current_schedule,
                'total_schedules': self.total_schedules,
                'current_schedule_completed_tasks': self.current_schedule_completed_tasks,
                'current_schedule_tasks': self.current_schedule_tasks,
            }
        )
        # self.callback(
        #     progress_percent,
        #     {'key': key, 'result': result, 'dsk': dsk, 'state': state, 'worker_id': worker_id},
        # )

    def _finish(self, dsk, state, failed):
        if self.current_schedule_completed_tasks != self.current_schedule_tasks:
            self.callback(
                {
                    'current_schedule': self.current_schedule,
                    'total_schedules': self.total_schedules,
                    'current_schedule_completed_tasks': self.current_schedule_tasks,
                    'current_schedule_tasks': self.current_schedule_tasks,
                }
            )

    # self.callback(
    #     100,
    #     {'dsk': dsk, 'state': state, 'failed': failed},
    # )


class TaskTrackingCallback(Callback):
    def __init__(self, client, callback: Callable):
        self.client = client
        self.previous_task_count = 0
        self.new_tasks_count = 0
        self.completed_tasks = 0
        self.callback = callback

    def _start(self, dsk):
        self.previous_task_count = len(self.client.scheduler_info()['tasks'])
        self.callback(f'{self.previous_task_count} tasks')

    def _posttask(self, key, result, dsk, state, worker_id):
        self.completed_tasks += 1
        current_task_count = len(self.client.scheduler_info()['tasks'])
        new_tasks_count = current_task_count - self.previous_task_count
        if new_tasks_count > 0:
            self.new_tasks_count += new_tasks_count
        self.previous_task_count = current_task_count
        self.callback(f'{self.completed_tasks}/{self.previous_task_count}')

    def _finish(self, dsk, state, failed):
        self.callback(self.new_tasks_count)
