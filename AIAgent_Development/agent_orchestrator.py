"""
Agent Orchestrator

This module integrates all AI Agent components into a unified system:
- Basic agent framework
- Database integration
- Recommendation engine
- Decision making logic
- Automation workflow
- Performance monitoring
"""

from typing import List, Dict, Any, Optional, Union
import logging
import json
import time
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Import our custom modules
from basic_agent_framework import BasicAgent, AgentState
from database_integration import (
    initialize_database, add_product, query_products, 
    update_product_stock, get_product_by_id
)
from recommendation_engine_integration import recommend_products, generate_suggestion_text
from decision_making_logic import OptimalSolutionGenerator, UserRequirementProcessor
from automation_workflow import (
    WorkflowEngine, WorkflowBuilder, PerformanceMonitor, 
    ErrorRecoveryManager, WorkflowTask, TaskStatus
)

class AgentOrchestrator:
    """
    Main orchestrator that coordinates all AI Agent components
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.agent = BasicAgent()
        self.workflow_engine = WorkflowEngine(max_workers=self.config.get('max_workers', 4))
        self.performance_monitor = PerformanceMonitor()
        self.error_recovery_manager = ErrorRecoveryManager()
        self.solution_generator = OptimalSolutionGenerator()
        self.requirement_processor = UserRequirementProcessor()
        
        # Initialize database
        self.db_path = self.config.get('database_path', 'products.db')
        initialize_database(self.db_path)
        
        # Register workflow functions
        self._register_workflow_functions()
        
        # Agent state
        self.is_running = False
        self.active_workflows = {}
        self.conversation_history = []
        
        self.logger.info("Agent Orchestrator initialized successfully")
    
    def _register_workflow_functions(self):
        """Register functions that can be called by workflows"""
        self.workflow_engine.register_function("search_products", self._workflow_search_products)
        self.workflow_engine.register_function("generate_recommendations", self._workflow_generate_recommendations)
        self.workflow_engine.register_function("process_order", self._workflow_process_order)
        self.workflow_engine.register_function("update_inventory", self._workflow_update_inventory)
        self.workflow_engine.register_function("customer_support", self._workflow_customer_support)
    
    def start(self):
        """Start the agent orchestrator"""
        self.is_running = True
        self.agent.update_state(AgentState.IDLE)
        self.logger.info("Agent Orchestrator started")
        
        # Start performance monitoring
        self.performance_monitor.record_metric("agent_start_time", datetime.now().isoformat())
    
    def stop(self):
        """Stop the agent orchestrator"""
        self.is_running = False
        self.agent.update_state(AgentState.IDLE)
        
        # Cancel all active workflows
        for execution_id in list(self.active_workflows.keys()):
            self.workflow_engine.cancel_execution(execution_id)
        
        self.logger.info("Agent Orchestrator stopped")
    
    def process_user_request(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a user request and generate appropriate response
        """
        if not self.is_running:
            return {"error": "Agent is not running"}
        
        start_time = time.time()
        
        try:
            # Update agent state
            self.agent.update_state(AgentState.PROCESSING)
            
            # Parse user input and determine intent
            intent = self._parse_user_intent(user_input)
            
            # Process based on intent
            if intent == "search_products":
                result = self._handle_product_search(user_input, context)
            elif intent == "get_recommendations":
                result = self._handle_recommendations(user_input, context)
            elif intent == "place_order":
                result = self._handle_order_placement(user_input, context)
            elif intent == "customer_support":
                result = self._handle_customer_support(user_input, context)
            else:
                result = self._handle_general_inquiry(user_input, context)
            
            # Record conversation
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "intent": intent,
                "response": result,
                "processing_time": time.time() - start_time
            })
            
            # Update performance metrics
            self.performance_monitor.record_metric("request_processing_time", time.time() - start_time)
            self.performance_monitor.record_metric("requests_processed", 1)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing user request: {e}")
            self.agent.update_state(AgentState.ERROR)
            return {"error": f"An error occurred: {str(e)}"}
        
        finally:
            self.agent.update_state(AgentState.IDLE)
    
    def _parse_user_intent(self, user_input: str) -> str:
        """Parse user input to determine intent"""
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ["search", "find", "look for", "show"]):
            return "search_products"
        elif any(word in user_input_lower for word in ["recommend", "suggestion", "best", "suitable"]):
            return "get_recommendations"
        elif any(word in user_input_lower for word in ["buy", "order", "purchase", "checkout"]):
            return "place_order"
        elif any(word in user_input_lower for word in ["help", "support", "issue", "problem"]):
            return "customer_support"
        else:
            return "general_inquiry"
    
    def _handle_product_search(self, user_input: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle product search requests"""
        # Extract search criteria from user input
        search_criteria = self._extract_search_criteria(user_input)
        
        # Query database
        products = query_products(category=search_criteria.get('category'), db_path=self.db_path)
        
        # Filter based on additional criteria
        if search_criteria.get('max_price'):
            products = [p for p in products if p.get('price', 0) <= search_criteria['max_price']]
        
        if search_criteria.get('min_cpu'):
            products = [p for p in products if p.get('cpu', 0) >= search_criteria['min_cpu']]
        
        return {
            "type": "product_search_results",
            "query": user_input,
            "criteria": search_criteria,
            "results": products,
            "count": len(products)
        }
    
    def _handle_recommendations(self, user_input: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle recommendation requests"""
        # Extract requirements from user input
        requirements = self._extract_requirements(user_input)
        
        # Get available products
        available_products = query_products(db_path=self.db_path)
        
        # Generate recommendations
        recommendations = recommend_products(available_products, requirements, top_n=5)
        
        # Generate personalized suggestions
        suggestions = []
        for product in recommendations:
            suggestion = generate_suggestion_text(product, requirements)
            suggestions.append({
                "product": product,
                "suggestion": suggestion
            })
        
        return {
            "type": "recommendations",
            "requirements": requirements,
            "recommendations": suggestions,
            "count": len(suggestions)
        }
    
    def _handle_order_placement(self, user_input: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle order placement requests"""
        # Extract order details from user input
        order_details = self._extract_order_details(user_input)
        
        # Validate product availability
        product = get_product_by_id(order_details.get('product_id'), self.db_path)
        if not product:
            return {"error": "Product not found"}
        
        if product.get('stock', 0) < order_details.get('quantity', 1):
            return {"error": "Insufficient stock"}
        
        # Create workflow for order processing
        workflow_id = self._create_order_workflow(order_details)
        execution_id = self.workflow_engine.execute_workflow(workflow_id)
        self.active_workflows[execution_id] = workflow_id
        
        return {
            "type": "order_placed",
            "order_id": execution_id,
            "status": "processing",
            "estimated_time": "2-3 minutes"
        }
    
    def _handle_customer_support(self, user_input: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle customer support requests"""
        # Create support workflow
        workflow_id = self._create_support_workflow(user_input)
        execution_id = self.workflow_engine.execute_workflow(workflow_id)
        self.active_workflows[execution_id] = workflow_id
        
        return {
            "type": "support_request",
            "request_id": execution_id,
            "status": "processing",
            "message": "Your support request has been received and is being processed."
        }
    
    def _handle_general_inquiry(self, user_input: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle general inquiries"""
        return {
            "type": "general_response",
            "message": "I can help you with product searches, recommendations, orders, and customer support. How can I assist you today?",
            "capabilities": [
                "Search for servers and hardware",
                "Get personalized recommendations",
                "Place orders",
                "Customer support"
            ]
        }
    
    def _extract_search_criteria(self, user_input: str) -> Dict[str, Any]:
        """Extract search criteria from user input"""
        criteria = {}
        user_input_lower = user_input.lower()
        
        # Extract category
        if "server" in user_input_lower:
            criteria['category'] = "Server"
        elif "storage" in user_input_lower:
            criteria['category'] = "Storage"
        elif "compute" in user_input_lower:
            criteria['category'] = "Compute"
        
        # Extract price range
        if "budget" in user_input_lower or "price" in user_input_lower:
            # Simple price extraction - in production, use NLP
            if "under" in user_input_lower:
                criteria['max_price'] = 2000  # Default max price
            elif "cheap" in user_input_lower or "affordable" in user_input_lower:
                criteria['max_price'] = 1000
        
        # Extract performance requirements
        if "high performance" in user_input_lower or "powerful" in user_input_lower:
            criteria['min_cpu'] = 16
            criteria['min_ram'] = 64
        
        return criteria
    
    def _extract_requirements(self, user_input: str) -> Dict[str, Any]:
        """Extract requirements from user input"""
        requirements = {}
        user_input_lower = user_input.lower()
        
        # Set defaults
        requirements['preferred_category'] = 'Compute'
        requirements['min_cpu'] = 8
        requirements['min_ram'] = 32
        requirements['max_price'] = 3000
        
        # Override based on user input
        if "budget" in user_input_lower:
            requirements['max_price'] = 1500
        if "high performance" in user_input_lower:
            requirements['min_cpu'] = 16
            requirements['min_ram'] = 64
        
        return requirements
    
    def _extract_order_details(self, user_input: str) -> Dict[str, Any]:
        """Extract order details from user input"""
        # Simple extraction - in production, use more sophisticated NLP
        return {
            'product_id': 1,  # Default product
            'quantity': 1,
            'customer_info': 'Default Customer'
        }
    
    def _create_order_workflow(self, order_details: Dict[str, Any]) -> str:
        """Create a workflow for processing orders"""
        builder = WorkflowBuilder()
        workflow_tasks = (builder
            .set_workflow_id("order_processing")
            .add_simple_task("validate_order", "Validate Order", "validate_order", order_details)
            .add_simple_task("check_inventory", "Check Inventory", "check_inventory", order_details, ["validate_order"])
            .add_simple_task("process_payment", "Process Payment", "process_payment", order_details, ["check_inventory"])
            .add_simple_task("update_inventory", "Update Inventory", "update_inventory", order_details, ["process_payment"])
            .add_simple_task("send_confirmation", "Send Confirmation", "send_confirmation", order_details, ["update_inventory"])
            .build())
        
        return self.workflow_engine.create_workflow("order_processing", workflow_tasks)
    
    def _create_support_workflow(self, user_input: str) -> str:
        """Create a workflow for customer support"""
        builder = WorkflowBuilder()
        workflow_tasks = (builder
            .set_workflow_id("customer_support")
            .add_simple_task("analyze_request", "Analyze Request", "customer_support", {"input": user_input})
            .add_simple_task("generate_response", "Generate Response", "generate_response", {"input": user_input}, ["analyze_request"])
            .build())
        
        return self.workflow_engine.create_workflow("customer_support", workflow_tasks)
    
    # Workflow function implementations
    def _workflow_search_products(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Workflow function for searching products"""
        return query_products(db_path=self.db_path)
    
    def _workflow_generate_recommendations(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Workflow function for generating recommendations"""
        products = query_products(db_path=self.db_path)
        return recommend_products(products, requirements, top_n=5)
    
    def _workflow_process_order(self, order_details: Dict[str, Any]) -> Dict[str, Any]:
        """Workflow function for processing orders"""
        # Simulate order processing
        time.sleep(1)
        return {"status": "processed", "order_id": f"ORD_{int(time.time())}"}
    
    def _workflow_update_inventory(self, product_id: int, quantity: int) -> bool:
        """Workflow function for updating inventory"""
        current_product = get_product_by_id(product_id, self.db_path)
        if current_product:
            new_stock = current_product.get('stock', 0) - quantity
            return update_product_stock(product_id, new_stock, self.db_path)
        return False
    
    def _workflow_customer_support(self, request: str) -> str:
        """Workflow function for customer support"""
        # Simple response generation - in production, use LLM
        if "server" in request.lower():
            return "I can help you with server selection. What are your requirements?"
        elif "price" in request.lower():
            return "Our servers range from $500 to $5000. What's your budget?"
        else:
            return "How can I assist you with your server needs?"
    
    def get_workflow_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a workflow execution"""
        execution = self.workflow_engine.get_execution_status(execution_id)
        if execution:
            return {
                "execution_id": execution.id,
                "status": execution.status.value,
                "start_time": execution.start_time.isoformat(),
                "end_time": execution.end_time.isoformat() if execution.end_time else None,
                "total_execution_time": execution.total_execution_time,
                "tasks": [
                    {
                        "id": task.id,
                        "name": task.name,
                        "status": task.status.value,
                        "result": task.result,
                        "error": task.error
                    }
                    for task in execution.tasks
                ]
            }
        return None
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics summary"""
        metrics = {}
        for metric_name in ["request_processing_time", "requests_processed", "workflow_execution_time"]:
            summary = self.performance_monitor.get_metric_summary(metric_name)
            if summary:
                metrics[metric_name] = summary
        
        return {
            "agent_state": self.agent.state.value,
            "active_workflows": len(self.active_workflows),
            "conversation_history_length": len(self.conversation_history),
            "metrics": metrics
        }
    
    def export_conversation_history(self, filepath: str) -> None:
        """Export conversation history to a file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.conversation_history, f, indent=2, default=str)
            self.logger.info(f"Conversation history exported to {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to export conversation history: {e}")

# --- Example Usage ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize the orchestrator
    config = {
        'max_workers': 4,
        'database_path': 'products.db'
    }
    
    orchestrator = AgentOrchestrator(config)
    
    # Start the orchestrator
    orchestrator.start()
    
    # Example interactions
    print("=== AI Agent Orchestrator Demo ===\n")
    
    # Test product search
    print("1. Product Search:")
    response = orchestrator.process_user_request("I need a server with high performance")
    print(f"Response: {response}\n")
    
    # Test recommendations
    print("2. Recommendations:")
    response = orchestrator.process_user_request("Recommend a server for my business needs")
    print(f"Response: {response}\n")
    
    # Test order placement
    print("3. Order Placement:")
    response = orchestrator.process_user_request("I want to buy a server")
    print(f"Response: {response}\n")
    
    # Test customer support
    print("4. Customer Support:")
    response = orchestrator.process_user_request("I need help choosing a server")
    print(f"Response: {response}\n")
    
    # Wait for workflows to complete
    print("Waiting for workflows to complete...")
    time.sleep(5)
    
    # Show performance metrics
    print("\n5. Performance Metrics:")
    metrics = orchestrator.get_performance_metrics()
    print(json.dumps(metrics, indent=2))
    
    # Stop the orchestrator
    orchestrator.stop()
    
    print("\nDemo completed!") 