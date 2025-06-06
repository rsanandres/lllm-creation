"""
Basic Agent Framework

This module implements a basic agent framework with:
- State management
- Decision-making logic
- User interaction handling
- Task planning capabilities

Each class and method is documented to help you understand the purpose and flow of the agent's logic.
"""

from typing import Dict, List, Optional
from enum import Enum
import logging

# Define the possible states the agent can be in
class AgentState(Enum):
    """Possible states of the agent"""
    IDLE = "idle"  # Agent is not doing anything
    PROCESSING = "processing"  # Agent is working on a task
    WAITING_FOR_INPUT = "waiting_for_input"  # Agent is waiting for user input
    ERROR = "error"  # Agent encountered an error

class BasicAgent:
    """
    Basic implementation of an AI agent with:
    - State management
    - Decision making
    - User interaction handling
    - Task planning
    """
    
    def __init__(self):
        """
        Initialize the agent with default state, context, and an empty task queue.
        The logger is used for tracking agent activity.
        """
        self.state = AgentState.IDLE  # Start in the IDLE state
        self.context: Dict = {}  # Context can store any relevant info for the agent
        self.task_queue: List = []  # List of tasks to be processed
        self.logger = logging.getLogger(__name__)

    def update_state(self, new_state: AgentState) -> None:
        """
        Update the agent's state and log the transition.
        Args:
            new_state: The new state to transition to
        """
        self.logger.info(f"State transition: {self.state} -> {new_state}")
        self.state = new_state

    def add_task(self, task: Dict) -> None:
        """
        Add a task to the agent's queue.
        Args:
            task: A dictionary describing the task (e.g., {"type": ..., "content": ...})
        """
        self.task_queue.append(task)
        self.logger.debug(f"Added task: {task}")

    def process_next_task(self) -> Optional[Dict]:
        """
        Process the next task in the queue.
        Returns:
            The result of the task execution, or None if no tasks are available.
        """
        if not self.task_queue:
            return None  # No tasks to process
        
        self.update_state(AgentState.PROCESSING)
        try:
            task = self.task_queue.pop(0)  # Get the next task (FIFO)
            result = self._execute_task(task)  # Execute the task
            self.update_state(AgentState.IDLE)  # Return to IDLE after processing
            return result
        except Exception as e:
            self.logger.error(f"Error processing task: {str(e)}")
            self.update_state(AgentState.ERROR)
            return {"error": str(e)}

    def _execute_task(self, task: Dict) -> Dict:
        """
        Execute a single task. This is a placeholder for actual task logic.
        Args:
            task: The task dictionary to execute
        Returns:
            A dictionary with the result of the task
        """
        # Example: Just echo the task content for demonstration
        self.logger.info(f"Executing task: {task}")
        return {"result": f"Processed task: {task}"}

    def update_context(self, new_context: Dict) -> None:
        """
        Update the agent's context with new information.
        Args:
            new_context: Dictionary of context updates
        """
        self.context.update(new_context)
        self.logger.debug(f"Updated context: {new_context}")

    def handle_user_input(self, user_input: str) -> Dict:
        """
        Handle user input by creating a task and processing it.
        Args:
            user_input: The input string from the user
        Returns:
            The result of processing the user input as a task
        """
        self.update_state(AgentState.WAITING_FOR_INPUT)
        try:
            # Create a task from user input
            task = {"type": "user_input", "content": user_input}
            self.add_task(task)
            # Process the task immediately
            return self.process_next_task() or {}
        finally:
            self.update_state(AgentState.IDLE)

    def reset(self) -> None:
        """
        Reset the agent to its initial state, clearing context and tasks.
        """
        self.state = AgentState.IDLE
        self.context.clear()
        self.task_queue.clear()
        self.logger.info("Agent reset to initial state")
    
    def decision_making(self, task: Dict) -> Dict:
        """
        Placeholder for decision-making logic based on the task.
        Args:
            task: The task dictionary to make a decision on
        Returns:
            The decision or action to take (to be implemented)
        """
        # Example: Not implemented, but could route tasks or choose actions
        raise NotImplementedError("Decision making logic not implemented.")
    
    def handle_error(self, error: Exception) -> Dict:
        """
        Handle an error by logging and returning an error dictionary.
        Args:
            error: The exception to handle
        Returns:
            A dictionary describing the error
        """
        self.logger.error(f"Error: {str(error)}")
        return {"error": str(error)}

# Example usage for learning
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = BasicAgent()
    print("Initial state:", agent.state)
    # Simulate user interaction
    result = agent.handle_user_input("What is the weather today?")
    print("User input result:", result)
    # Add a custom task
    agent.add_task({"type": "custom", "content": "Do something important"})
    print("Processing next task:", agent.process_next_task())
    # Reset the agent
    agent.reset()
    print("State after reset:", agent.state)
