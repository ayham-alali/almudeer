"""
Al-Mudeer - Background Task Queue
Simple async queue for AI processing tasks using Redis
Enables non-blocking message processing and better scalability
"""

import os
import asyncio
import json
from datetime import datetime
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass, asdict
from enum import Enum

from logging_config import get_logger

logger = get_logger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class QueuedTask:
    """A task in the queue"""
    task_id: str
    task_type: str  # "analyze", "draft", "process_message"
    payload: Dict[str, Any]
    status: str = TaskStatus.PENDING.value
    created_at: str = ""
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retries: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()


class TaskQueue:
    """
    Simple async task queue backed by Redis or in-memory.
    Processes AI tasks in the background without blocking API responses.
    """
    
    def __init__(self):
        self._redis_client = None
        self._use_redis = False
        self._memory_queue: List[QueuedTask] = []
        self._processing_tasks: Dict[str, QueuedTask] = {}
        self._completed_tasks: Dict[str, QueuedTask] = {}
        self._worker_running = False
        self._max_queue_size = 1000
        self._worker_task: Optional[asyncio.Task] = None
        
    async def initialize(self):
        """Initialize the queue, connect to Redis if available"""
        redis_url = os.getenv("REDIS_URL")
        
        if redis_url:
            try:
                import redis.asyncio as redis
                self._redis_client = redis.from_url(redis_url, decode_responses=True)
                await self._redis_client.ping()
                self._use_redis = True
                logger.info("Task queue connected to Redis")
            except Exception as e:
                logger.warning(f"Redis not available, using in-memory queue: {e}")
                self._use_redis = False
        else:
            logger.info("Redis URL not configured, using in-memory queue")
            self._use_redis = False
    
    async def enqueue(self, task_type: str, payload: Dict[str, Any]) -> str:
        """Add a task to the queue, returns task_id"""
        import uuid
        task_id = str(uuid.uuid4())[:8]
        
        task = QueuedTask(
            task_id=task_id,
            task_type=task_type,
            payload=payload
        )
        
        if self._use_redis and self._redis_client:
            # Store in Redis
            await self._redis_client.lpush("almudeer:task_queue", json.dumps(asdict(task)))
            await self._redis_client.set(f"almudeer:task:{task_id}", json.dumps(asdict(task)), ex=3600)
        else:
            # In-memory queue
            if len(self._memory_queue) >= self._max_queue_size:
                # Remove oldest completed tasks
                self._memory_queue = [t for t in self._memory_queue if t.status == TaskStatus.PENDING.value]
            self._memory_queue.append(task)
        
        logger.debug(f"Task {task_id} enqueued: {task_type}")
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a task"""
        if self._use_redis and self._redis_client:
            data = await self._redis_client.get(f"almudeer:task:{task_id}")
            if data:
                return json.loads(data)
        else:
            # Check all stores
            for task in self._memory_queue:
                if task.task_id == task_id:
                    return asdict(task)
            if task_id in self._processing_tasks:
                return asdict(self._processing_tasks[task_id])
            if task_id in self._completed_tasks:
                return asdict(self._completed_tasks[task_id])
        return None
    
    async def dequeue(self) -> Optional[QueuedTask]:
        """Get next task from queue"""
        if self._use_redis and self._redis_client:
            data = await self._redis_client.rpop("almudeer:task_queue")
            if data:
                task_dict = json.loads(data)
                return QueuedTask(**task_dict)
        else:
            for task in self._memory_queue:
                if task.status == TaskStatus.PENDING.value:
                    task.status = TaskStatus.PROCESSING.value
                    return task
        return None
    
    async def complete_task(self, task_id: str, result: Dict[str, Any] = None, error: str = None):
        """Mark a task as completed or failed"""
        status = TaskStatus.FAILED.value if error else TaskStatus.COMPLETED.value
        
        if self._use_redis and self._redis_client:
            data = await self._redis_client.get(f"almudeer:task:{task_id}")
            if data:
                task_dict = json.loads(data)
                task_dict["status"] = status
                task_dict["completed_at"] = datetime.utcnow().isoformat()
                task_dict["result"] = result
                task_dict["error"] = error
                await self._redis_client.set(f"almudeer:task:{task_id}", json.dumps(task_dict), ex=3600)
        else:
            if task_id in self._processing_tasks:
                task = self._processing_tasks.pop(task_id)
                task.status = status
                task.completed_at = datetime.utcnow().isoformat()
                task.result = result
                task.error = error
                self._completed_tasks[task_id] = task
                # Limit completed tasks cache
                if len(self._completed_tasks) > 100:
                    oldest = list(self._completed_tasks.keys())[0]
                    del self._completed_tasks[oldest]
    
    async def start_worker(self, handler: Callable):
        """Start the background worker that processes tasks"""
        if self._worker_running:
            return
        
        self._worker_running = True
        logger.info("Task queue worker started")
        
        async def worker_loop():
            while self._worker_running:
                try:
                    task = await self.dequeue()
                    if task:
                        self._processing_tasks[task.task_id] = task
                        try:
                            result = await handler(task.task_type, task.payload)
                            await self.complete_task(task.task_id, result=result)
                        except Exception as e:
                            logger.error(f"Task {task.task_id} failed: {e}")
                            await self.complete_task(task.task_id, error=str(e))
                    else:
                        # No tasks, wait a bit
                        await asyncio.sleep(0.5)
                except Exception as e:
                    logger.error(f"Worker error: {e}")
                    await asyncio.sleep(1)
        
        self._worker_task = asyncio.create_task(worker_loop())
    
    async def stop_worker(self):
        """Stop the background worker"""
        self._worker_running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("Task queue worker stopped")
    
    @property
    def queue_size(self) -> int:
        """Get current queue size"""
        if self._use_redis:
            return 0  # Would need async call
        return len([t for t in self._memory_queue if t.status == TaskStatus.PENDING.value])


# Global task queue instance
_task_queue: Optional[TaskQueue] = None


async def get_task_queue() -> TaskQueue:
    """Get or initialize the global task queue"""
    global _task_queue
    if _task_queue is None:
        _task_queue = TaskQueue()
        await _task_queue.initialize()
    return _task_queue


async def enqueue_ai_task(task_type: str, payload: Dict[str, Any]) -> str:
    """Convenience function to enqueue an AI task"""
    queue = await get_task_queue()
    return await queue.enqueue(task_type, payload)


async def get_ai_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """Convenience function to get task status"""
    queue = await get_task_queue()
    return await queue.get_task_status(task_id)
