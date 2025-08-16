"""
Comprehensive Test Suite for AI Agent System

This module tests all components of the AI Agent system:
- Basic agent framework
- Database integration
- Recommendation engine
- Decision making logic
- Automation workflow
- Agent orchestrator
"""

import unittest
import tempfile
import os
import time
import json
from unittest.mock import Mock, patch
import sys
import logging

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from basic_agent_framework import BasicAgent, AgentState
from database_integration import (
    initialize_database, add_product, query_products, 
    update_product_stock, get_product_by_id, delete_product
)
from recommendation_engine_integration import recommend_products, generate_suggestion_text
from decision_making_logic import (
    DecisionTree, DecisionNode, DecisionNodeType,
    MultiCriteriaDecisionMaker, UserRequirementProcessor,
    OptimalSolutionGenerator
)
from automation_workflow import (
    WorkflowEngine, WorkflowBuilder, PerformanceMonitor,
    ErrorRecoveryManager, WorkflowTask, TaskStatus, WorkflowStatus
)
from agent_orchestrator import AgentOrchestrator

class TestBasicAgentFramework(unittest.TestCase):
    """Test the basic agent framework"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = BasicAgent()
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertEqual(self.agent.state, AgentState.IDLE)
        self.assertEqual(len(self.agent.task_queue), 0)
        self.assertEqual(len(self.agent.context), 0)
    
    def test_state_transitions(self):
        """Test agent state transitions"""
        self.agent.update_state(AgentState.PROCESSING)
        self.assertEqual(self.agent.state, AgentState.PROCESSING)
        
        self.agent.update_state(AgentState.WAITING_FOR_INPUT)
        self.assertEqual(self.agent.state, AgentState.WAITING_FOR_INPUT)
    
    def test_task_management(self):
        """Test task management"""
        task = {"type": "test", "content": "test content"}
        self.agent.add_task(task)
        self.assertEqual(len(self.agent.task_queue), 1)
        
        result = self.agent.process_next_task()
        self.assertIsNotNone(result)
        self.assertEqual(len(self.agent.task_queue), 0)
    
    def test_user_input_handling(self):
        """Test user input handling"""
        result = self.agent.handle_user_input("test input")
        self.assertIsNotNone(result)
    
    def test_agent_reset(self):
        """Test agent reset functionality"""
        self.agent.add_task({"type": "test", "content": "test"})
        self.agent.update_context({"test": "value"})
        
        self.agent.reset()
        self.assertEqual(self.agent.state, AgentState.IDLE)
        self.assertEqual(len(self.agent.task_queue), 0)
        self.assertEqual(len(self.agent.context), 0)

class TestDatabaseIntegration(unittest.TestCase):
    """Test database integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        # Initialize the test database
        initialize_database(self.db_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Remove the temporary database
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_database_initialization(self):
        """Test database initialization"""
        # Database should be created and accessible
        products = query_products(db_path=self.db_path)
        self.assertEqual(len(products), 0)
    
    def test_product_operations(self):
        """Test product CRUD operations"""
        # Test adding a product
        product = {
            "name": "Test Server",
            "category": "Compute",
            "price": 1000.0,
            "stock": 5
        }
        
        product_id = add_product(product, self.db_path)
        self.assertIsNotNone(product_id)
        
        # Test retrieving the product
        retrieved_product = get_product_by_id(product_id, self.db_path)
        self.assertIsNotNone(retrieved_product)
        self.assertEqual(retrieved_product["name"], "Test Server")
        
        # Test updating stock
        success = update_product_stock(product_id, 3, self.db_path)
        self.assertTrue(success)
        
        updated_product = get_product_by_id(product_id, self.db_path)
        self.assertEqual(updated_product["stock"], 3)
        
        # Test querying products
        compute_products = query_products(category="Compute", db_path=self.db_path)
        self.assertEqual(len(compute_products), 1)
        
        # Test deleting the product
        success = delete_product(product_id, self.db_path)
        self.assertTrue(success)
        
        deleted_product = get_product_by_id(product_id, self.db_path)
        self.assertIsNone(deleted_product)

class TestRecommendationEngine(unittest.TestCase):
    """Test recommendation engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.products = [
            {"id": 1, "name": "Server A", "category": "Compute", "cpu": 16, "ram": 64, "storage": 1000, "price": 1200.0},
            {"id": 2, "name": "Server B", "category": "Storage", "cpu": 8, "ram": 32, "storage": 4000, "price": 1500.0},
            {"id": 3, "name": "Server C", "category": "Compute", "cpu": 32, "ram": 128, "storage": 2000, "price": 2000.0},
        ]
        
        self.user_prefs = {
            "preferred_category": "Compute",
            "min_cpu": 8,
            "min_ram": 32,
            "max_price": 2000.0
        }
    
    def test_recommendation_generation(self):
        """Test recommendation generation"""
        recommendations = recommend_products(self.products, self.user_prefs, top_n=2)
        self.assertGreater(len(recommendations), 0)
        
        # Check that recommendations meet user preferences
        for rec in recommendations:
            self.assertGreaterEqual(rec["cpu"], self.user_prefs["min_cpu"])
            self.assertGreaterEqual(rec["ram"], self.user_prefs["min_ram"])
            self.assertLessEqual(rec["price"], self.user_prefs["max_price"])
    
    def test_suggestion_generation(self):
        """Test suggestion text generation"""
        product = self.products[0]
        suggestion = generate_suggestion_text(product, self.user_prefs)
        
        self.assertIsInstance(suggestion, str)
        self.assertIn(product["name"], suggestion)
        self.assertIn(str(product["cpu"]), suggestion)
        self.assertIn(str(product["ram"]), suggestion)

class TestDecisionMakingLogic(unittest.TestCase):
    """Test decision making logic"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.decision_tree = DecisionTree()
        self.mcdm = MultiCriteriaDecisionMaker()
        self.requirement_processor = UserRequirementProcessor()
        self.solution_generator = OptimalSolutionGenerator()
    
    def test_decision_tree(self):
        """Test decision tree functionality"""
        # Create a simple decision tree
        root = DecisionNode(
            id="root",
            node_type=DecisionNodeType.CONDITION,
            condition="test_condition",
            children=["action1"]
        )
        
        action1 = DecisionNode(
            id="action1",
            node_type=DecisionNodeType.ACTION,
            action="test_action",
            children=[]
        )
        
        self.decision_tree.add_node(root)
        self.decision_tree.add_node(action1)
        self.decision_tree.set_root("root")
        
        # Test tree evaluation
        context = {"test_condition": True}
        actions = self.decision_tree.evaluate(context)
        self.assertIn("test_action", actions)
    
    def test_multi_criteria_decision_making(self):
        """Test multi-criteria decision making"""
        alternatives = [
            {"cpu_cores": 16, "ram_gb": 64, "storage_gb": 1000, "price": 2000},
            {"cpu_cores": 8, "ram_gb": 32, "storage_gb": 500, "price": 1000},
        ]
        
        criteria = ["cpu_cores", "ram_gb", "storage_gb", "price"]
        weights = {"cpu_cores": 0.3, "ram_gb": 0.3, "storage_gb": 0.2, "price": 0.2}
        
        self.mcdm.set_criteria_weights(weights)
        scored_alternatives = self.mcdm.evaluate_alternatives(alternatives, criteria)
        
        self.assertEqual(len(scored_alternatives), 2)
        self.assertGreater(scored_alternatives[0][1], scored_alternatives[1][1])  # First should have higher score
    
    def test_requirement_processing(self):
        """Test requirement processing"""
        user_input = {
            "cpu_cores": 8,
            "ram_gb": 32,
            "budget": 2000
        }
        
        processed = self.requirement_processor.process_requirements(user_input)
        
        self.assertEqual(processed["cpu_cores"], 8)
        self.assertEqual(processed["ram_gb"], 32)
        self.assertEqual(processed["budget"], 2000)
        self.assertEqual(processed["storage_gb"], 500)  # Default value
        self.assertEqual(processed["priority"], "balanced")  # Default value
    
    def test_solution_generation(self):
        """Test solution generation"""
        user_requirements = {
            "cpu_cores": 8,
            "ram_gb": 32,
            "storage_gb": 1000,
            "budget": 3000,
            "priority": "performance"
        }
        
        available_servers = [
            {"id": 1, "name": "Server A", "cpu_cores": 16, "ram_gb": 64, "storage_gb": 2000, "price": 2800},
            {"id": 2, "name": "Server B", "cpu_cores": 8, "ram_gb": 32, "storage_gb": 1000, "price": 1800},
        ]
        
        solutions = self.solution_generator.generate_solutions(user_requirements, available_servers)
        
        self.assertGreater(len(solutions), 0)
        for solution in solutions:
            self.assertIn("server", solution)
            self.assertIn("score", solution)
            self.assertIn("reasoning", solution)

class TestAutomationWorkflow(unittest.TestCase):
    """Test automation workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.workflow_engine = WorkflowEngine(max_workers=2)
        self.performance_monitor = PerformanceMonitor()
        self.error_recovery_manager = ErrorRecoveryManager()
    
    def test_workflow_creation_and_execution(self):
        """Test workflow creation and execution"""
        # Register a test function
        def test_function(message: str) -> str:
            return f"Processed: {message}"
        
        self.workflow_engine.register_function("test_function", test_function)
        
        # Create a simple workflow
        builder = WorkflowBuilder()
        workflow_tasks = (builder
            .set_workflow_id("test_workflow")
            .add_simple_task("task1", "Test Task", "test_function", {"message": "Hello"})
            .build())
        
        workflow_id = self.workflow_engine.create_workflow("test_workflow", workflow_tasks)
        execution_id = self.workflow_engine.execute_workflow(workflow_id)
        
        # Wait for completion
        time.sleep(2)
        
        execution = self.workflow_engine.get_execution_status(execution_id)
        self.assertIsNotNone(execution)
        self.assertIn(execution.status, [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED])
    
    def test_performance_monitoring(self):
        """Test performance monitoring"""
        self.performance_monitor.record_metric("test_metric", 100)
        self.performance_monitor.record_metric("test_metric", 200)
        
        summary = self.performance_monitor.get_metric_summary("test_metric")
        self.assertEqual(summary["count"], 2)
        self.assertEqual(summary["min"], 100)
        self.assertEqual(summary["max"], 200)
        self.assertEqual(summary["avg"], 150)
    
    def test_error_recovery(self):
        """Test error recovery"""
        def recovery_strategy(task, error):
            return True  # Always recover
        
        self.error_recovery_manager.register_recovery_strategy("ValueError", recovery_strategy)
        
        # Create a mock task
        task = Mock()
        task.retry_count = 0
        task.status = TaskStatus.FAILED
        
        # Test recovery
        success = self.error_recovery_manager.attempt_recovery(task, ValueError("test error"))
        self.assertTrue(success)

class TestAgentOrchestrator(unittest.TestCase):
    """Test agent orchestrator"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        config = {
            'max_workers': 2,
            'database_path': self.db_path
        }
        
        self.orchestrator = AgentOrchestrator(config)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initialization"""
        self.assertIsNotNone(self.orchestrator.agent)
        self.assertIsNotNone(self.orchestrator.workflow_engine)
        self.assertIsNotNone(self.orchestrator.performance_monitor)
    
    def test_orchestrator_lifecycle(self):
        """Test orchestrator start/stop lifecycle"""
        self.orchestrator.start()
        self.assertTrue(self.orchestrator.is_running)
        
        self.orchestrator.stop()
        self.assertFalse(self.orchestrator.is_running)
    
    def test_user_request_processing(self):
        """Test user request processing"""
        self.orchestrator.start()
        
        # Test product search
        response = self.orchestrator.process_user_request("I need a server")
        self.assertIsNotNone(response)
        self.assertIn("type", response)
        
        self.orchestrator.stop()
    
    def test_performance_metrics(self):
        """Test performance metrics collection"""
        self.orchestrator.start()
        
        # Process a request to generate metrics
        self.orchestrator.process_user_request("test request")
        
        metrics = self.orchestrator.get_performance_metrics()
        self.assertIn("agent_state", metrics)
        self.assertIn("metrics", metrics)
        
        self.orchestrator.stop()

def run_performance_tests():
    """Run performance tests"""
    print("\n=== Performance Tests ===")
    
    # Test basic agent performance
    start_time = time.time()
    agent = BasicAgent()
    for i in range(1000):
        agent.add_task({"type": "test", "content": f"task {i}"})
        agent.process_next_task()
    basic_agent_time = time.time() - start_time
    
    print(f"Basic Agent: 1000 tasks in {basic_agent_time:.3f} seconds")
    
    # Test recommendation engine performance
    start_time = time.time()
    products = [{"id": i, "name": f"Server {i}", "category": "Compute", "cpu": i*2, "ram": i*4, "storage": i*100, "price": i*100.0} for i in range(1, 101)]
    user_prefs = {"preferred_category": "Compute", "min_cpu": 10, "min_ram": 20, "max_price": 5000.0}
    
    for _ in range(100):
        recommend_products(products, user_prefs, top_n=10)
    recommendation_time = time.time() - start_time
    
    print(f"Recommendation Engine: 100 recommendations in {recommendation_time:.3f} seconds")
    
    # Test decision making performance
    start_time = time.time()
    solution_generator = OptimalSolutionGenerator()
    user_reqs = {"cpu_cores": 8, "ram_gb": 32, "storage_gb": 1000, "budget": 3000, "priority": "performance"}
    
    for _ in range(100):
        solution_generator.generate_solutions(user_reqs, products[:20])
    decision_time = time.time() - start_time
    
    print(f"Decision Making: 100 solutions in {decision_time:.3f} seconds")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.WARNING)
    
    # Run unit tests
    print("Running AI Agent System Tests...")
    unittest.main(verbosity=2, exit=False)
    
    # Run performance tests
    run_performance_tests()
    
    print("\nAll tests completed!") 