from typing import Callable, Dict, List, Any
import asyncio

class Task:
    def __init__(self, name: str, func: Callable, dependencies: List[str] = None, is_async: bool = False):
        self.name = name
        self.func = func
        self.dependencies = dependencies or []
        self.is_async = is_async
        self.result = None

    async def run(self, *args: Any):
        """Execute the task function."""
        if self.is_async:
            self.result = await self.func(*args)
        else:
            self.result = self.func(*args).call()
        return self.result

class Pipeline:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    def add_task(self, name: str, func: Callable, dependencies: List[str] = None):
        def wrapped_func(*args: Any):
            return func(*args)
        is_async = False
        self.tasks[name] = Task(name, wrapped_func, dependencies, is_async)

    def add_task_async(self, name: str, coro_func: Callable, dependencies: List[str] = None):
        async def wrapped_func(*args: Any):
            return await coro_func(*args)
        is_async = True
        self.tasks[name] = Task(name, wrapped_func, dependencies, is_async)

    async def run_task(self, name: str, completed: Dict[str, Any]):
        """Run a task and its dependencies."""
        task = self.tasks[name]

        # If the task is already computed, return the result
        if name in completed:
            return completed[name]

        # Resolve dependencies
        dep_results = await asyncio.gather(*(self.run_task(dep, completed) for dep in task.dependencies))

        # Execute the task with resolved dependencies
        completed[name] = await task.run(*dep_results)
        return completed[name]

    async def run(self):
        """Run all tasks in the pipeline."""
        completed = {}
        for name in self.tasks:
            await self.run_task(name, completed)
        return completed


class AsyncFunc:
    def __init__(self, coro_func: Callable, *args, **kwargs):
        self._coro_func = coro_func
        self._args = args
        self._kwargs = kwargs

    def __await__(self):
        return self._coro_func(*self._args, **self._kwargs).__await__()

class Func:
    def __init__(self, func: Callable, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs
    
    def call(self):
        return self._func(*self._args, **self._kwargs)
