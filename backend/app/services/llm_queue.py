"""
Simple async queue that serialises exam-generation jobs.
Ensures only one exam is being generated at a time.
Individual LLM calls within a job use the semaphore in llm_service.
"""

import asyncio
import logging
import uuid
from typing import Callable, Coroutine, Any

logger = logging.getLogger(__name__)

class LLMQueue:
    """In-process async queue for exam generation jobs."""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[
            tuple[Callable[..., Coroutine], tuple, asyncio.Future]
        ] = asyncio.Queue()
        self._processing = False

    async def enqueue(
        self, task_fn: Callable[..., Coroutine], *args: Any
    ) -> Any:
        """
        Add a generation job to the queue.
        Returns the result when the job completes.
        """
        future: asyncio.Future = asyncio.get_event_loop().create_future()
        await self._queue.put((task_fn, args, future))

        if not self._processing:
            asyncio.create_task(self._process())

        return await future

    def enqueue_fire_and_forget(
        self, task_fn: Callable[..., Coroutine], *args: Any
    ) -> None:
        """Add a generation job without waiting for the result."""
        future: asyncio.Future = asyncio.get_event_loop().create_future()
        asyncio.ensure_future(self._queue.put((task_fn, args, future)))

        if not self._processing:
            asyncio.ensure_future(self._process())

    async def _process(self) -> None:
        self._processing = True
        logger.info("LLM queue worker started")

        while not self._queue.empty():
            task_fn, args, future = await self._queue.get()
            job_id = str(uuid.uuid4())[:8]

            try:
                logger.info(f"[Job {job_id}] Starting")
                result = await task_fn(*args)
                if not future.done():
                    future.set_result(result)
                logger.info(f"[Job {job_id}] Completed")
            except Exception as exc:
                logger.error(f"[Job {job_id}] Failed: {exc}")
                if not future.done():
                    future.set_exception(exc)
            finally:
                self._queue.task_done()

        self._processing = False
        logger.info("LLM queue worker idle")


# Global singleton
generation_queue = LLMQueue()