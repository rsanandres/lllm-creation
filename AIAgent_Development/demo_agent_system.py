#!/usr/bin/env python3
"""
AI Agent System Demo

This script demonstrates the full capabilities of the AI Agent system:
- Interactive agent conversations
- Product search and recommendations
- Decision making and workflow automation
- Performance monitoring and metrics
- Real-world server selection scenarios

Run this script to see the AI Agent in action!
"""

import time
import json
import logging
from datetime import datetime
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
from agent_orchestrator import AgentOrchestrator

class AgentSystemDemo:
    """
    Interactive demo of the AI Agent system
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        
        # Initialize components
        self.initialize_demo_data()
        self.orchestrator = AgentOrchestrator({
            'max_workers': 4,
            'database_path': 'demo_products.db'
        })
        
        # Demo scenarios
        self.demo_scenarios = [
            "Basic Agent Operations",
            "Product Search and Recommendations",
            "Decision Making and Optimization",
            "Workflow Automation",
            "Performance Monitoring",
            "Interactive Conversation",
            "Exit"
        ]
    
    def setup_logging(self):
        """Set up logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('demo.log'),
                logging.StreamHandler()
            ]
        )
    
    def initialize_demo_data(self):
        """Initialize demo database with sample products"""
        initialize_database('demo_products.db')
        
        # Add sample products
        sample_products = [
            {
                "name": "Enterprise Server Pro",
                "category": "Compute",
                "price": 4500.0,
                "stock": 3
            },
            {
                "name": "Mid-Range Server",
                "category": "Compute",
                "price": 2800.0,
                "stock": 8
            },
            {
                "name": "Budget Server",
                "category": "Compute",
                "price": 1200.0,
                "stock": 15
            },
            {
                "name": "High-Capacity Storage Server",
                "category": "Storage",
                "price": 3200.0,
                "stock": 5
            },
            {
                "name": "Network Storage Array",
                "category": "Storage",
                "price": 1800.0,
                "stock": 12
            },
            {
                "name": "GPU Computing Server",
                "category": "Compute",
                "price": 5500.0,
                "stock": 2
            }
        ]
        
        for product in sample_products:
            add_product(product, 'demo_products.db')
        
        self.logger.info(f"Initialized demo database with {len(sample_products)} products")
    
    def run_demo(self):
        """Run the main demo loop"""
        print("\n" + "="*60)
        print("🤖 AI AGENT SYSTEM DEMO")
        print("="*60)
        print("Welcome to the AI Agent System demonstration!")
        print("This system showcases intelligent server selection and automation.")
        print("="*60)
        
        while True:
            self.show_menu()
            choice = input("\nSelect a demo scenario (1-7): ").strip()
            
            if choice == '1':
                self.demo_basic_agent()
            elif choice == '2':
                self.demo_product_search()
            elif choice == '3':
                self.demo_decision_making()
            elif choice == '4':
                self.demo_workflow_automation()
            elif choice == '5':
                self.demo_performance_monitoring()
            elif choice == '6':
                self.demo_interactive_conversation()
            elif choice == '7':
                print("\n👋 Thank you for trying the AI Agent System!")
                break
            else:
                print("❌ Invalid choice. Please select 1-7.")
            
            input("\nPress Enter to continue...")
    
    def show_menu(self):
        """Display the demo menu"""
        print("\n" + "-"*40)
        print("📋 DEMO SCENARIOS")
        print("-"*40)
        for i, scenario in enumerate(self.demo_scenarios, 1):
            print(f"{i}. {scenario}")
        print("-"*40)
    
    def demo_basic_agent(self):
        """Demonstrate basic agent operations"""
        print("\n🔧 BASIC AGENT OPERATIONS")
        print("-" * 40)
        
        # Create and demonstrate basic agent
        agent = BasicAgent()
        print(f"✅ Agent created with initial state: {agent.state.value}")
        
        # Demonstrate state transitions
        print("\n🔄 State Transitions:")
        agent.update_state(AgentState.PROCESSING)
        print(f"   → Processing: {agent.state.value}")
        
        agent.update_state(AgentState.WAITING_FOR_INPUT)
        print(f"   → Waiting for input: {agent.state.value}")
        
        agent.update_state(AgentState.IDLE)
        print(f"   → Back to idle: {agent.state.value}")
        
        # Demonstrate task management
        print("\n📋 Task Management:")
        agent.add_task({"type": "demo", "content": "Sample task"})
        print(f"   → Added task to queue. Queue length: {len(agent.task_queue)}")
        
        result = agent.process_next_task()
        print(f"   → Processed task result: {result}")
        print(f"   → Queue length after processing: {len(agent.task_queue)}")
        
        # Demonstrate context management
        print("\n🧠 Context Management:")
        agent.update_context({"user_id": "demo_user", "session": "demo_session"})
        print(f"   → Updated context: {agent.context}")
        
        # Reset agent
        agent.reset()
        print(f"   → Agent reset. State: {agent.state.value}, Context: {len(agent.context)}")
    
    def demo_product_search(self):
        """Demonstrate product search and recommendations"""
        print("\n🔍 PRODUCT SEARCH & RECOMMENDATIONS")
        print("-" * 40)
        
        # Show available products
        products = query_products(db_path='demo_products.db')
        print(f"✅ Available products in database: {len(products)}")
        
        # Demonstrate search by category
        print("\n📊 Search by Category:")
        compute_servers = query_products(category="Compute", db_path='demo_products.db')
        print(f"   → Compute servers: {len(compute_servers)}")
        for server in compute_servers:
            print(f"     - {server['name']}: ${server['price']:.2f}")
        
        storage_servers = query_products(category="Storage", db_path='demo_products.db')
        print(f"   → Storage servers: {len(storage_servers)}")
        for server in storage_servers:
            print(f"     - {server['name']}: ${server['price']:.2f}")
        
        # Demonstrate recommendations
        print("\n💡 Smart Recommendations:")
        user_prefs = {
            "preferred_category": "Compute",
            "min_cpu": 8,
            "min_ram": 32,
            "max_price": 3000.0
        }
        
        recommendations = recommend_products(products, user_prefs, top_n=3)
        print(f"   → Recommendations for budget-conscious compute needs:")
        for i, rec in enumerate(recommendations, 1):
            suggestion = generate_suggestion_text(rec, user_prefs)
            print(f"     {i}. {suggestion}")
    
    def demo_decision_making(self):
        """Demonstrate decision making and optimization"""
        print("\n🧠 DECISION MAKING & OPTIMIZATION")
        print("-" * 40)
        
        # Initialize decision making components
        solution_generator = OptimalSolutionGenerator()
        requirement_processor = UserRequirementProcessor()
        
        # Demonstrate requirement processing
        print("📝 Requirement Processing:")
        raw_requirements = {
            "cpu_cores": 16,
            "ram_gb": 64,
            "budget": 4000
        }
        
        processed_reqs = requirement_processor.process_requirements(raw_requirements)
        print(f"   → Raw requirements: {raw_requirements}")
        print(f"   → Processed requirements: {processed_reqs}")
        
        # Demonstrate solution generation
        print("\n🎯 Solution Generation:")
        available_servers = [
            {"id": 1, "name": "Enterprise Server Pro", "cpu_cores": 32, "ram_gb": 128, "storage_gb": 4000, "price": 4500},
            {"id": 2, "name": "Mid-Range Server", "cpu_cores": 16, "ram_gb": 64, "storage_gb": 2000, "price": 2800},
            {"id": 3, "name": "GPU Computing Server", "cpu_cores": 24, "ram_gb": 96, "storage_gb": 3000, "price": 5500},
        ]
        
        solutions = solution_generator.generate_solutions(processed_reqs, available_servers)
        print(f"   → Generated {len(solutions)} solutions:")
        
        for i, solution in enumerate(solutions, 1):
            server = solution['server']
            print(f"     {i}. {server['name']}")
            print(f"        Score: {solution['score']:.3f}")
            print(f"        Reasoning: {solution['reasoning']}")
            print(f"        Requirements met: {solution['requirements_met']}")
    
    def demo_workflow_automation(self):
        """Demonstrate workflow automation"""
        print("\n⚙️ WORKFLOW AUTOMATION")
        print("-" * 40)
        
        # Initialize workflow components
        workflow_engine = WorkflowEngine(max_workers=2)
        performance_monitor = PerformanceMonitor()
        
        # Register demo functions
        def demo_task(message: str, delay: float = 0.5) -> str:
            time.sleep(delay)
            return f"✅ {message} completed"
        
        workflow_engine.register_function("demo_task", demo_task)
        
        # Create and execute workflow
        print("🔄 Creating workflow...")
        builder = WorkflowBuilder()
        workflow_tasks = (builder
            .set_workflow_id("demo_workflow")
            .add_simple_task("task1", "Initialize System", "demo_task", {"message": "System initialization", "delay": 0.5})
            .add_simple_task("task2", "Load Data", "demo_task", {"message": "Data loading", "delay": 0.3}, ["task1"])
            .add_simple_task("task3", "Process Requests", "demo_task", {"message": "Request processing", "delay": 0.4}, ["task2"])
            .add_simple_task("task4", "Generate Report", "demo_task", {"message": "Report generation", "delay": 0.2}, ["task3"])
            .build())
        
        workflow_id = workflow_engine.create_workflow("demo_workflow", workflow_tasks)
        execution_id = workflow_engine.execute_workflow(workflow_id)
        
        print(f"   → Workflow created: {workflow_id}")
        print(f"   → Execution started: {execution_id}")
        
        # Monitor workflow execution
        print("\n📊 Workflow Execution:")
        while True:
            execution = workflow_engine.get_execution_status(execution_id)
            if execution.status in ['completed', 'failed', 'cancelled']:
                break
            
            print(f"   → Status: {execution.status}")
            for task in execution.tasks:
                print(f"     - {task.name}: {task.status}")
            
            time.sleep(0.5)
        
        # Show final results
        final_execution = workflow_engine.get_execution_status(execution_id)
        print(f"\n🎉 Final Status: {final_execution.status}")
        print(f"   → Total execution time: {final_execution.total_execution_time:.2f} seconds")
        
        for task in final_execution.tasks:
            print(f"   → {task.name}: {task.status}")
            if task.result:
                print(f"     Result: {task.result}")
        
        # Record performance metrics
        performance_monitor.record_metric("workflow_demo_time", final_execution.total_execution_time)
        print(f"\n📈 Performance metric recorded: workflow_demo_time = {final_execution.total_execution_time:.2f}s")
    
    def demo_performance_monitoring(self):
        """Demonstrate performance monitoring"""
        print("\n📊 PERFORMANCE MONITORING")
        print("-" * 40)
        
        # Initialize performance monitor
        monitor = PerformanceMonitor()
        
        # Record various metrics
        print("📝 Recording Metrics:")
        monitor.record_metric("response_time", 0.15)
        monitor.record_metric("response_time", 0.22)
        monitor.record_metric("response_time", 0.18)
        monitor.record_metric("response_time", 0.25)
        
        monitor.record_metric("requests_per_minute", 45)
        monitor.record_metric("requests_per_minute", 52)
        monitor.record_metric("requests_per_minute", 48)
        
        monitor.record_metric("memory_usage_mb", 128)
        monitor.record_metric("memory_usage_mb", 135)
        monitor.record_metric("memory_usage_mb", 142)
        
        print("   → Response time metrics recorded")
        print("   → Request rate metrics recorded")
        print("   → Memory usage metrics recorded")
        
        # Show metric summaries
        print("\n📊 Metric Summaries:")
        metrics = ["response_time", "requests_per_minute", "memory_usage_mb"]
        
        for metric_name in metrics:
            summary = monitor.get_metric_summary(metric_name)
            if summary:
                print(f"   → {metric_name}:")
                print(f"     Count: {summary.get('count', 0)}")
                print(f"     Min: {summary.get('min', 'N/A')}")
                print(f"     Max: {summary.get('max', 'N/A')}")
                print(f"     Average: {summary.get('avg', 'N/A'):.2f}")
                print(f"     Latest: {summary.get('latest', 'N/A')}")
        
        # Export metrics
        export_file = "demo_metrics.json"
        monitor.export_metrics(export_file)
        print(f"\n💾 Metrics exported to: {export_file}")
    
    def demo_interactive_conversation(self):
        """Demonstrate interactive conversation with the agent"""
        print("\n💬 INTERACTIVE CONVERSATION")
        print("-" * 40)
        
        # Start the orchestrator
        self.orchestrator.start()
        print("✅ Agent Orchestrator started")
        
        # Sample conversation
        conversation_examples = [
            "I need a server for my web hosting business",
            "What's the best server for data analysis?",
            "I have a budget of $3000, what can you recommend?",
            "Show me storage servers with high capacity",
            "I need help choosing between different server options"
        ]
        
        print("\n🤖 Agent Responses:")
        for i, user_input in enumerate(conversation_examples, 1):
            print(f"\n   User {i}: {user_input}")
            
            response = self.orchestrator.process_user_request(user_input)
            
            if response.get("type") == "product_search_results":
                print(f"   🤖 Agent: Found {response['count']} products matching your criteria")
                for product in response['results'][:2]:  # Show first 2 results
                    print(f"      - {product['name']}: ${product['price']:.2f}")
            
            elif response.get("type") == "recommendations":
                print(f"   🤖 Agent: Here are {response['count']} personalized recommendations")
                for rec in response['recommendations'][:2]:  # Show first 2 recommendations
                    print(f"      - {rec['suggestion']}")
            
            elif response.get("type") == "order_placed":
                print(f"   🤖 Agent: {response['message']}")
                print(f"      Order ID: {response['order_id']}")
            
            elif response.get("type") == "support_request":
                print(f"   🤖 Agent: {response['message']}")
                print(f"      Request ID: {response['request_id']}")
            
            else:
                print(f"   🤖 Agent: {response.get('message', 'Processing your request...')}")
            
            time.sleep(0.5)  # Small delay for readability
        
        # Show performance metrics
        print("\n📊 Conversation Performance:")
        metrics = self.orchestrator.get_performance_metrics()
        print(f"   → Agent State: {metrics['agent_state']}")
        print(f"   → Active Workflows: {metrics['active_workflows']}")
        print(f"   → Conversation History Length: {metrics['conversation_history_length']}")
        
        # Export conversation history
        export_file = "demo_conversation.json"
        self.orchestrator.export_conversation_history(export_file)
        print(f"   → Conversation exported to: {export_file}")
        
        # Stop the orchestrator
        self.orchestrator.stop()
        print("   → Agent Orchestrator stopped")

def main():
    """Main function to run the demo"""
    try:
        demo = AgentSystemDemo()
        demo.run_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        logging.error(f"Demo error: {e}", exc_info=True)
    finally:
        print("\n🧹 Cleaning up...")
        # Clean up demo database
        if os.path.exists('demo_products.db'):
            os.remove('demo_products.db')
        print("✅ Demo cleanup completed")

if __name__ == "__main__":
    main() 