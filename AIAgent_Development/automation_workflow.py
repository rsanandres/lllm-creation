"""
Automation Workflow for AI Agent

This module implements comprehensive workflow automation including:
- Task automation patterns
- Error recovery mechanisms
- Performance monitoring
- Workflow orchestration
- State persistence
"""

from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import logging
import time
import json
import asyncio
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- Workflow Components ---

class WorkflowStatus(Enum):
    """Possible statuses of a workflow"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class TaskStatus(Enum):
    """Possible statuses of individual tasks"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class WorkflowTask:
    """Represents a task within a workflow"""
    id: str
    name: str
    description: str
    function: str  # Name of the function to call
    parameters: Dict[str, Any]
    dependencies: List[str]  # Task IDs this task depends on
    timeout: int = 300  # Timeout in seconds
    retry_count: int = 0
    max_retries: int = 3
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time: Optional[float] = None

@dataclass
class WorkflowExecution:
    """Represents a workflow execution instance"""
    id: str
    workflow_id: str
    status: WorkflowStatus
    tasks: List[WorkflowTask]
    start_time: datetime
    end_time: Optional[datetime] = None
    total_execution_time: Optional[float] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

# --- Workflow Engine ---

class WorkflowEngine:
    """
    Main workflow engine that orchestrates task execution
    """
    
    def __init__(self, max_workers: int = 4):
        self.workflows: Dict[str, List[WorkflowTask]] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.registered_functions: Dict[str, Callable] = {}
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.logger = logging.getLogger(__name__)
        self.monitor_thread = None
        self.monitoring = False
    
    def register_function(self, name: str, func: Callable) -> None:
        """Register a function that can be called by workflows"""
        self.registered_functions[name] = func
        self.logger.info(f"Registered function: {name}")
    
    def create_workflow(self, workflow_id: str, tasks: List[WorkflowTask]) -> str:
        """Create a new workflow definition"""
        self.workflows[workflow_id] = tasks
        self.logger.info(f"Created workflow: {workflow_id} with {len(tasks)} tasks")
        return workflow_id
    
    def execute_workflow(self, workflow_id: str, execution_id: Optional[str] = None) -> str:
        """Execute a workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if execution_id is None:
            execution_id = f"{workflow_id}_{int(time.time())}"
        
        # Create execution instance
        execution = WorkflowExecution(
            id=execution_id,
            workflow_id=workflow_id,
            status=WorkflowStatus.RUNNING,
            tasks=[task for task in self.workflows[workflow_id]],
            start_time=datetime.now()
        )
        
        self.executions[execution_id] = execution
        
        # Start execution in background
        threading.Thread(target=self._execute_workflow_async, args=(execution_id,)).start()
        
        return execution_id
    
    def _execute_workflow_async(self, execution_id: str) -> None:
        """Execute workflow asynchronously"""
        execution = self.executions[execution_id]
        
        try:
            # Execute tasks in dependency order
            completed_tasks = set()
            running_tasks = {}
            
            while len(completed_tasks) < len(execution.tasks):
                # Find tasks ready to run
                for task in execution.tasks:
                    if (task.status == TaskStatus.PENDING and 
                        task.id not in running_tasks and
                        all(dep in completed_tasks for dep in task.dependencies)):
                        
                        # Submit task for execution
                        future = self.executor.submit(self._execute_task, task)
                        running_tasks[task.id] = future
                        task.status = TaskStatus.RUNNING
                        task.start_time = datetime.now()
                
                # Check completed tasks
                for task_id, future in list(running_tasks.items()):
                    if future.done():
                        try:
                            result = future.result()
                            task = next(t for t in execution.tasks if t.id == task_id)
                            task.status = TaskStatus.COMPLETED
                            task.result = result
                            task.end_time = datetime.now()
                            task.execution_time = (task.end_time - task.start_time).total_seconds()
                            completed_tasks.add(task_id)
                            del running_tasks[task_id]
                        except Exception as e:
                            task = next(t for t in execution.tasks if t.id == task_id)
                            task.status = TaskStatus.FAILED
                            task.error = str(e)
                            task.end_time = datetime.now()
                            completed_tasks.add(task_id)
                            del running_tasks[task_id]
                
                time.sleep(0.1)  # Small delay to prevent busy waiting
            
            # Check if all tasks completed successfully
            failed_tasks = [t for t in execution.tasks if t.status == TaskStatus.FAILED]
            if failed_tasks:
                execution.status = WorkflowStatus.FAILED
                self.logger.error(f"Workflow {execution_id} failed: {len(failed_tasks)} tasks failed")
            else:
                execution.status = WorkflowStatus.COMPLETED
                self.logger.info(f"Workflow {execution_id} completed successfully")
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            self.logger.error(f"Workflow {execution_id} execution error: {e}")
        
        finally:
            execution.end_time = datetime.now()
            execution.total_execution_time = (execution.end_time - execution.start_time).total_seconds()
    
    def _execute_task(self, task: WorkflowTask) -> Any:
        """Execute a single task"""
        if task.function not in self.registered_functions:
            raise ValueError(f"Function {task.function} not registered")
        
        func = self.registered_functions[task.function]
        return func(**task.parameters)
    
    def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get the status of a workflow execution"""
        return self.executions.get(execution_id)
    
    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running workflow execution"""
        if execution_id in self.executions:
            execution = self.executions[execution_id]
            if execution.status == WorkflowStatus.RUNNING:
                execution.status = WorkflowStatus.CANCELLED
                self.logger.info(f"Cancelled workflow execution: {execution_id}")
                return True
        return False

# --- Error Recovery Manager ---

class ErrorRecoveryManager:
    """
    Manages error recovery strategies for failed tasks
    """
    
    def __init__(self):
        self.recovery_strategies: Dict[str, Callable] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_recovery_strategy(self, error_type: str, strategy: Callable) -> None:
        """Register a recovery strategy for a specific error type"""
        self.recovery_strategies[error_type] = strategy
        self.logger.info(f"Registered recovery strategy for: {error_type}")
    
    def attempt_recovery(self, task: WorkflowTask, error: Exception) -> bool:
        """Attempt to recover from a task failure"""
        error_type = type(error).__name__
        
        if error_type in self.recovery_strategies:
            try:
                strategy = self.recovery_strategies[error_type]
                result = strategy(task, error)
                if result:
                    task.status = TaskStatus.PENDING
                    task.retry_count += 1
                    task.error = None
                    self.logger.info(f"Recovery successful for task {task.id}")
                    return True
            except Exception as recovery_error:
                self.logger.error(f"Recovery strategy failed for task {task.id}: {recovery_error}")
        
        return False
    
    def should_retry(self, task: WorkflowTask) -> bool:
        """Determine if a task should be retried"""
        return (task.status == TaskStatus.FAILED and 
                task.retry_count < task.max_retries)

# --- Performance Monitor ---

class PerformanceMonitor:
    """
    Monitors and tracks workflow performance metrics
    """
    
    def __init__(self):
        self.metrics: Dict[str, List[Dict[str, Any]]] = {}
        self.logger = logging.getLogger(__name__)
    
    def record_metric(self, metric_name: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record a performance metric"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        metric_record = {
            "timestamp": datetime.now().isoformat(),
            "value": value,
            "metadata": metadata or {}
        }
        
        self.metrics[metric_name].append(metric_record)
        self.logger.debug(f"Recorded metric {metric_name}: {value}")
    
    def get_metric_summary(self, metric_name: str, time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get summary statistics for a metric"""
        if metric_name not in self.metrics:
            return {}
        
        records = self.metrics[metric_name]
        
        if time_window:
            cutoff = datetime.now() - time_window
            records = [r for r in records if datetime.fromisoformat(r["timestamp"]) > cutoff]
        
        if not records:
            return {}
        
        values = [r["value"] for r in records if isinstance(r["value"], (int, float))]
        
        if not values:
            return {"count": len(records)}
        
        return {
            "count": len(records),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1] if values else None
        }
    
    def export_metrics(self, filepath: str) -> None:
        """Export metrics to a JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.metrics, f, indent=2, default=str)
            self.logger.info(f"Metrics exported to {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to export metrics: {e}")

# --- Workflow Builder ---

class WorkflowBuilder:
    """
    Builder pattern for creating workflows
    """
    
    def __init__(self):
        self.tasks: List[WorkflowTask] = []
        self.workflow_id: Optional[str] = None
    
    def set_workflow_id(self, workflow_id: str) -> 'WorkflowBuilder':
        """Set the workflow ID"""
        self.workflow_id = workflow_id
        return self
    
    def add_task(self, task: WorkflowTask) -> 'WorkflowBuilder':
        """Add a task to the workflow"""
        self.tasks.append(task)
        return self
    
    def add_simple_task(self, task_id: str, name: str, function: str, 
                       parameters: Dict[str, Any], dependencies: List[str] = None) -> 'WorkflowBuilder':
        """Add a simple task with basic configuration"""
        task = WorkflowTask(
            id=task_id,
            name=name,
            description=f"Task {name}",
            function=function,
            parameters=parameters,
            dependencies=dependencies or []
        )
        return self.add_task(task)
    
    def build(self) -> List[WorkflowTask]:
        """Build the workflow task list"""
        if not self.workflow_id:
            raise ValueError("Workflow ID must be set before building")
        return self.tasks.copy()

# --- Example Usage and Testing ---

def example_task_function(message: str, delay: float = 1.0) -> str:
    """Example task function for testing"""
    time.sleep(delay)
    return f"Task completed: {message}"

def example_error_task_function() -> None:
    """Example task function that raises an error"""
    raise ValueError("This is a test error")

def example_recovery_strategy(task: WorkflowTask, error: Exception) -> bool:
    """Example recovery strategy"""
    if task.retry_count < 2:
        time.sleep(1)  # Wait before retry
        return True
    return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize components
    engine = WorkflowEngine(max_workers=2)
    recovery_manager = ErrorRecoveryManager()
    performance_monitor = PerformanceMonitor()
    
    # Register functions
    engine.register_function("example_task", example_task_function)
    engine.register_function("error_task", example_error_task_function)
    
    # Register recovery strategy
    recovery_manager.register_recovery_strategy("ValueError", example_recovery_strategy)
    
    # Build workflow
    builder = WorkflowBuilder()
    workflow_tasks = (builder
        .set_workflow_id("example_workflow")
        .add_simple_task("task1", "First Task", "example_task", {"message": "Hello", "delay": 1.0})
        .add_simple_task("task2", "Second Task", "example_task", {"message": "World", "delay": 0.5}, ["task1"])
        .add_simple_task("task3", "Error Task", "error_task", {}, ["task2"])
        .build())
    
    # Create and execute workflow
    workflow_id = engine.create_workflow("example_workflow", workflow_tasks)
    execution_id = engine.execute_workflow(workflow_id)
    
    print(f"Started workflow execution: {execution_id}")
    
    # Monitor execution
    while True:
        execution = engine.get_execution_status(execution_id)
        if execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
            break
        
        print(f"Workflow status: {execution.status}")
        for task in execution.tasks:
            print(f"  Task {task.id}: {task.status}")
        
        time.sleep(1)
    
    # Final status
    final_execution = engine.get_execution_status(execution_id)
    print(f"\nFinal workflow status: {final_execution.status}")
    print(f"Total execution time: {final_execution.total_execution_time:.2f} seconds")
    
    for task in final_execution.tasks:
        print(f"Task {task.id}: {task.status}")
        if task.error:
            print(f"  Error: {task.error}")
        if task.result:
            print(f"  Result: {task.result}")
    
    # Record performance metrics
    performance_monitor.record_metric("workflow_execution_time", final_execution.total_execution_time)
    performance_monitor.record_metric("tasks_completed", len([t for t in final_execution.tasks if t.status == TaskStatus.COMPLETED]))
    performance_monitor.record_metric("tasks_failed", len([t for t in final_execution.tasks if t.status == TaskStatus.FAILED]))
    
    # Show metrics summary
    print("\nPerformance Metrics:")
    for metric_name in ["workflow_execution_time", "tasks_completed", "tasks_failed"]:
        summary = performance_monitor.get_metric_summary(metric_name)
        print(f"{metric_name}: {summary}") 