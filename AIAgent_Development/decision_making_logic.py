"""
Decision Making Logic for AI Agent

This module implements advanced decision-making capabilities including:
- Decision trees for server selection
- Complex scenario handling
- User requirement processing
- Optimal solution generation
- Multi-criteria decision analysis
"""

from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import logging
from dataclasses import dataclass
import json

# --- Decision Tree Components ---

class DecisionNodeType(Enum):
    """Types of decision nodes in the decision tree"""
    CONDITION = "condition"
    ACTION = "action"
    LEAF = "leaf"

@dataclass
class DecisionNode:
    """Represents a node in the decision tree"""
    id: str
    node_type: DecisionNodeType
    condition: Optional[str] = None
    action: Optional[str] = None
    children: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.metadata is None:
            self.metadata = {}

class DecisionTree:
    """
    Implements a decision tree for server selection and configuration
    """
    
    def __init__(self):
        self.nodes: Dict[str, DecisionNode] = {}
        self.root_id: Optional[str] = None
        self.logger = logging.getLogger(__name__)
    
    def add_node(self, node: DecisionNode) -> None:
        """Add a node to the decision tree"""
        self.nodes[node.id] = node
        if self.root_id is None:
            self.root_id = node.id
    
    def set_root(self, node_id: str) -> None:
        """Set the root node of the decision tree"""
        if node_id in self.nodes:
            self.root_id = node_id
        else:
            raise ValueError(f"Node {node_id} not found in tree")
    
    def evaluate(self, context: Dict[str, Any]) -> List[str]:
        """
        Evaluate the decision tree based on current context
        Returns list of actions to take
        """
        if not self.root_id:
            return []
        
        actions = []
        self._evaluate_node(self.root_id, context, actions)
        return actions
    
    def _evaluate_node(self, node_id: str, context: Dict[str, Any], actions: List[str]) -> None:
        """Recursively evaluate a node in the decision tree"""
        if node_id not in self.nodes:
            return
        
        node = self.nodes[node_id]
        
        if node.node_type == DecisionNodeType.LEAF:
            if node.action:
                actions.append(node.action)
            return
        
        if node.node_type == DecisionNodeType.CONDITION:
            if self._evaluate_condition(node.condition, context):
                # Condition met, evaluate children
                for child_id in node.children:
                    self._evaluate_node(child_id, context, actions)
            return
        
        if node.node_type == DecisionNodeType.ACTION:
            if node.action:
                actions.append(node.action)
            # Continue to children
            for child_id in node.children:
                self._evaluate_node(child_id, context, actions)
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a condition string against the context"""
        try:
            # Simple condition evaluation - in production, use a proper expression parser
            if "budget" in condition and "price" in condition:
                return context.get("budget", 0) >= context.get("price", 0)
            elif "cpu_requirement" in condition:
                return context.get("cpu_cores", 0) >= context.get("cpu_requirement", 0)
            elif "ram_requirement" in condition:
                return context.get("ram_gb", 0) >= context.get("ram_requirement", 0)
            elif "storage_requirement" in condition:
                return context.get("storage_gb", 0) >= context.get("storage_requirement", 0)
            return True
        except Exception as e:
            self.logger.error(f"Error evaluating condition {condition}: {e}")
            return False

# --- Multi-Criteria Decision Analysis ---

class MultiCriteriaDecisionMaker:
    """
    Implements multi-criteria decision analysis for server selection
    """
    
    def __init__(self):
        self.criteria_weights: Dict[str, float] = {}
        self.logger = logging.getLogger(__name__)
    
    def set_criteria_weights(self, weights: Dict[str, float]) -> None:
        """Set the weights for different decision criteria"""
        total_weight = sum(weights.values())
        if total_weight != 0:
            self.criteria_weights = {k: v/total_weight for k, v in weights.items()}
        else:
            self.logger.warning("Total weight is 0, using equal weights")
            self.criteria_weights = {k: 1.0/len(weights) for k in weights.keys()}
    
    def evaluate_alternatives(self, alternatives: List[Dict[str, Any]], criteria: List[str]) -> List[Tuple[Dict[str, Any], float]]:
        """
        Evaluate alternatives using weighted criteria
        Returns list of (alternative, score) tuples sorted by score
        """
        if not alternatives or not criteria:
            return []
        
        scored_alternatives = []
        
        for alternative in alternatives:
            score = self._calculate_score(alternative, criteria)
            scored_alternatives.append((alternative, score))
        
        # Sort by score (higher is better)
        scored_alternatives.sort(key=lambda x: x[1], reverse=True)
        return scored_alternatives
    
    def _calculate_score(self, alternative: Dict[str, Any], criteria: List[str]) -> float:
        """Calculate weighted score for an alternative"""
        total_score = 0.0
        
        for criterion in criteria:
            if criterion in self.criteria_weights and criterion in alternative:
                # Normalize the criterion value (assuming 0-1 scale)
                normalized_value = self._normalize_criterion(criterion, alternative[criterion])
                total_score += self.criteria_weights[criterion] * normalized_value
        
        return total_score
    
    def _normalize_criterion(self, criterion: str, value: Any) -> float:
        """Normalize a criterion value to 0-1 scale"""
        try:
            if isinstance(value, (int, float)):
                # Simple normalization - in production, use more sophisticated methods
                if criterion == "price":
                    # Lower price is better, so invert
                    return max(0, 1 - (value / 10000))  # Assuming max price is 10k
                elif criterion in ["cpu_cores", "ram_gb", "storage_gb"]:
                    # Higher is better
                    return min(1, value / 100)  # Assuming max is 100
                else:
                    return min(1, max(0, value / 100))
            return 0.5  # Default neutral score
        except Exception as e:
            self.logger.error(f"Error normalizing criterion {criterion}: {e}")
            return 0.5

# --- User Requirement Processor ---

class UserRequirementProcessor:
    """
    Processes and validates user requirements for server selection
    """
    
    def __init__(self):
        self.required_fields = ["cpu_cores", "ram_gb", "storage_gb", "budget"]
        self.logger = logging.getLogger(__name__)
    
    def process_requirements(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and validate user requirements
        Returns processed requirements with defaults and validation
        """
        processed = {}
        
        # Set defaults for missing fields
        defaults = {
            "cpu_cores": 4,
            "ram_gb": 16,
            "storage_gb": 500,
            "budget": 2000,
            "priority": "balanced"
        }
        
        for field, default_value in defaults.items():
            processed[field] = user_input.get(field, default_value)
        
        # Validate requirements
        validation_result = self._validate_requirements(processed)
        if not validation_result["valid"]:
            self.logger.warning(f"Validation warnings: {validation_result['warnings']}")
        
        return processed
    
    def _validate_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user requirements and return validation result"""
        warnings = []
        
        # Check minimum values
        if requirements["cpu_cores"] < 1:
            warnings.append("CPU cores should be at least 1")
            requirements["cpu_cores"] = 1
        
        if requirements["ram_gb"] < 4:
            warnings.append("RAM should be at least 4GB")
            requirements["ram_gb"] = 4
        
        if requirements["storage_gb"] < 100:
            warnings.append("Storage should be at least 100GB")
            requirements["storage_gb"] = 100
        
        if requirements["budget"] < 500:
            warnings.append("Budget should be at least $500")
            requirements["budget"] = 500
        
        return {
            "valid": len(warnings) == 0,
            "warnings": warnings
        }

# --- Optimal Solution Generator ---

class OptimalSolutionGenerator:
    """
    Generates optimal server configurations based on requirements and constraints
    """
    
    def __init__(self):
        self.decision_tree = DecisionTree()
        self.mcdm = MultiCriteriaDecisionMaker()
        self.requirement_processor = UserRequirementProcessor()
        self.logger = logging.getLogger(__name__)
        self._build_decision_tree()
    
    def _build_decision_tree(self):
        """Build the decision tree for server selection"""
        # Root node - check budget
        root = DecisionNode(
            id="budget_check",
            node_type=DecisionNodeType.CONDITION,
            condition="budget >= price",
            children=["cpu_check"]
        )
        self.decision_tree.add_node(root)
        
        # CPU requirement check
        cpu_check = DecisionNode(
            id="cpu_check",
            node_type=DecisionNodeType.CONDITION,
            condition="cpu_requirement <= cpu_cores",
            children=["ram_check"]
        )
        self.decision_tree.add_node(cpu_check)
        
        # RAM requirement check
        ram_check = DecisionNode(
            id="ram_check",
            node_type=DecisionNodeType.CONDITION,
            condition="ram_requirement <= ram_gb",
            children=["storage_check"]
        )
        self.decision_tree.add_node(ram_check)
        
        # Storage requirement check
        storage_check = DecisionNode(
            id="storage_check",
            node_type=DecisionNodeType.CONDITION,
            condition="storage_requirement <= storage_gb",
            children=["recommend_server"]
        )
        self.decision_tree.add_node(storage_check)
        
        # Final recommendation
        recommend = DecisionNode(
            id="recommend_server",
            node_type=DecisionNodeType.ACTION,
            action="recommend_server",
            children=[]
        )
        self.decision_tree.add_node(recommend)
        
        self.decision_tree.set_root("budget_check")
    
    def generate_solutions(self, user_requirements: Dict[str, Any], available_servers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate optimal solutions based on user requirements and available servers
        """
        # Process user requirements
        processed_reqs = self.requirement_processor.process_requirements(user_requirements)
        
        # Set criteria weights based on user priority
        weights = self._get_criteria_weights(processed_reqs.get("priority", "balanced"))
        self.mcdm.set_criteria_weights(weights)
        
        # Filter servers based on basic requirements
        filtered_servers = self._filter_servers(available_servers, processed_reqs)
        
        # Evaluate alternatives using multi-criteria decision analysis
        criteria = ["cpu_cores", "ram_gb", "storage_gb", "price"]
        scored_servers = self.mcdm.evaluate_alternatives(filtered_servers, criteria)
        
        # Generate solution recommendations
        solutions = []
        for server, score in scored_servers[:5]:  # Top 5 recommendations
            solution = {
                "server": server,
                "score": score,
                "reasoning": self._generate_reasoning(server, processed_reqs),
                "requirements_met": self._check_requirements_met(server, processed_reqs)
            }
            solutions.append(solution)
        
        return solutions
    
    def _get_criteria_weights(self, priority: str) -> Dict[str, float]:
        """Get criteria weights based on user priority"""
        if priority == "performance":
            return {"cpu_cores": 0.4, "ram_gb": 0.3, "storage_gb": 0.2, "price": 0.1}
        elif priority == "budget":
            return {"cpu_cores": 0.2, "ram_gb": 0.2, "storage_gb": 0.2, "price": 0.4}
        elif priority == "storage":
            return {"cpu_cores": 0.2, "ram_gb": 0.2, "storage_gb": 0.4, "price": 0.2}
        else:  # balanced
            return {"cpu_cores": 0.25, "ram_gb": 0.25, "storage_gb": 0.25, "price": 0.25}
    
    def _filter_servers(self, servers: List[Dict[str, Any]], requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter servers based on basic requirements"""
        filtered = []
        
        for server in servers:
            if (server.get("cpu_cores", 0) >= requirements["cpu_cores"] and
                server.get("ram_gb", 0) >= requirements["ram_gb"] and
                server.get("storage_gb", 0) >= requirements["storage_gb"] and
                server.get("price", float('inf')) <= requirements["budget"]):
                filtered.append(server)
        
        return filtered
    
    def _generate_reasoning(self, server: Dict[str, Any], requirements: Dict[str, Any]) -> str:
        """Generate reasoning for why a server was recommended"""
        reasons = []
        
        if server.get("cpu_cores", 0) > requirements["cpu_cores"]:
            reasons.append(f"Exceeds CPU requirement ({server['cpu_cores']} vs {requirements['cpu_cores']})")
        
        if server.get("ram_gb", 0) > requirements["ram_gb"]:
            reasons.append(f"Exceeds RAM requirement ({server['ram_gb']}GB vs {requirements['ram_gb']}GB)")
        
        if server.get("storage_gb", 0) > requirements["storage_gb"]:
            reasons.append(f"Exceeds storage requirement ({server['storage_gb']}GB vs {requirements['storage_gb']}GB)")
        
        if server.get("price", 0) < requirements["budget"]:
            reasons.append(f"Under budget (${server['price']} vs ${requirements['budget']})")
        
        return "; ".join(reasons) if reasons else "Meets all requirements"
    
    def _check_requirements_met(self, server: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, bool]:
        """Check which requirements are met by the server"""
        return {
            "cpu": server.get("cpu_cores", 0) >= requirements["cpu_cores"],
            "ram": server.get("ram_gb", 0) >= requirements["ram_gb"],
            "storage": server.get("storage_gb", 0) >= requirements["storage_gb"],
            "budget": server.get("price", float('inf')) <= requirements["budget"]
        }

# --- Example Usage ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize the solution generator
    generator = OptimalSolutionGenerator()
    
    # Example user requirements
    user_reqs = {
        "cpu_cores": 8,
        "ram_gb": 32,
        "storage_gb": 1000,
        "budget": 3000,
        "priority": "performance"
    }
    
    # Example available servers
    available_servers = [
        {"id": 1, "name": "Server A", "cpu_cores": 16, "ram_gb": 64, "storage_gb": 2000, "price": 2800},
        {"id": 2, "name": "Server B", "cpu_cores": 8, "ram_gb": 32, "storage_gb": 1000, "price": 1800},
        {"id": 3, "name": "Server C", "cpu_cores": 32, "ram_gb": 128, "storage_gb": 4000, "price": 4500},
        {"id": 4, "name": "Server D", "cpu_cores": 4, "ram_gb": 16, "storage_gb": 500, "price": 800},
    ]
    
    # Generate solutions
    solutions = generator.generate_solutions(user_reqs, available_servers)
    
    print("User Requirements:", user_reqs)
    print("\nAvailable Servers:", available_servers)
    print("\nGenerated Solutions:")
    
    for i, solution in enumerate(solutions, 1):
        print(f"\n{i}. {solution['server']['name']}")
        print(f"   Score: {solution['score']:.3f}")
        print(f"   Reasoning: {solution['reasoning']}")
        print(f"   Requirements Met: {solution['requirements_met']}") 