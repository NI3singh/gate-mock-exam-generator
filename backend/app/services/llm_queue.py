"""
asyncio.Queue singleton for sequential LLM processing.

One generation job processes at a time — others wait in the queue.
The worker is started/stopped via the FastAPI lifespan in main.py.
"""

import asyncio
import uuid
from dataclasses import dataclass
from typing import Callable, Awaitable

# Module-level singleton queue
_queue: asyncio.Queue["GenerationJob | None"] = asyncio.Queue()


@dataclass
class GenerationJob:
    """A single exam generation job placed in the queue."""
    exam_id: uuid.UUID
    paper: str
    scope: str
    selected_topics: list[str] | None
    difficulty: str
    types_ratio: dict[str, float]


def get_queue() -> asyncio.Queue["GenerationJob | None"]:
    """Returns the singleton queue instance."""
    return _queue


async def enqueue(job: GenerationJob) -> None:
    """Add a generation job to the queue."""
    await _queue.put(job)


async def shutdown_queue() -> None:
    """Signal the worker to stop by sending the None sentinel."""
    await _queue.put(None)


async def run_worker(
    process_fn: Callable[[GenerationJob], Awaitable[None]],
) -> None:
    """
    Long-running worker coroutine. Runs inside an asyncio.Task managed
    by the FastAPI lifespan. Processes one job at a time sequentially.
    """
    while True:
        job = await _queue.get()
        if job is None:
            # Shutdown sentinel received
            break
        try:
            await process_fn(job)
        except Exception as exc:
            print(f"[llm_queue] Job {job.exam_id} failed: {exc}")
        finally:
            _queue.task_done()
