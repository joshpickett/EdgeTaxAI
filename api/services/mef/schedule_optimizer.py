from typing import List, Dict, Any
import logging
from collections import defaultdict

class ScheduleOptimizer:
    """Optimize schedule processing order and dependencies"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.dependency_graph = {
            'SCHEDULE_C': ['1040'],
            'SCHEDULE_SE': ['1040', 'SCHEDULE_C'],
            'SCHEDULE_E': ['1040'],
            'SCHEDULE_F': ['1040']
        }

    async def optimize(self, schedules: List[str]) -> List[str]:
        """Optimize schedule processing order"""
        try:
            # Create dependency graph
            graph = self._build_dependency_graph(schedules)
            
            # Perform topological sort
            ordered_schedules = self._topological_sort(graph)
            
            # Validate optimization result
            if not self._validate_optimization(ordered_schedules):
                raise ValueError("Invalid schedule optimization result")
                
            return ordered_schedules
            
        except Exception as e:
            self.logger.error(f"Error optimizing schedules: {str(e)}")
            raise

    def _build_dependency_graph(self, schedules: List[str]) -> Dict[str, List[str]]:
        """Build graph of schedule dependencies"""
        graph = defaultdict(list)
        
        for schedule in schedules:
            dependencies = self.dependency_graph.get(schedule, [])
            for dep in dependencies:
                if dep in schedules:
                    graph[schedule].append(dep)
                    
        return graph

    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        """Perform topological sort on schedule dependency graph"""
        visited = set()
        temp = set()
        order = []
        
        def visit(node: str):
            if node in temp:
                raise ValueError("Circular dependency detected")
            if node in visited:
                return
                
            temp.add(node)
            
            for dependency in graph.get(node, []):
                visit(dependency)
                
            temp.remove(node)
            visited.add(node)
            order.append(node)
            
        try:
            for node in graph:
                if node not in visited:
                    visit(node)
                    
            return order
            
        except Exception as e:
            self.logger.error(f"Error in topological sort: {str(e)}")
            raise

    def _validate_optimization(self, ordered_schedules: List[str]) -> bool:
        """Validate optimization result"""
        # Check for circular dependencies
        seen = set()
        for schedule in ordered_schedules:
            if schedule in seen:
                return False
            seen.add(schedule)
            
        # Validate dependencies are met
        for i, schedule in enumerate(ordered_schedules):
            dependencies = self.dependency_graph.get(schedule, [])
            for dep in dependencies:
                if dep in ordered_schedules:
                    if ordered_schedules.index(dep) > i:
                        return False
                        
        return True

    def analyze_dependencies(self, schedules: List[str]) -> Dict[str, Any]:
        """Analyze schedule dependencies"""
        analysis = {
            'direct_dependencies': defaultdict(list),
            'indirect_dependencies': defaultdict(list),
            'dependency_chains': defaultdict(list)
        }
        
        for schedule in schedules:
            # Direct dependencies
            analysis['direct_dependencies'][schedule] = self.dependency_graph.get(schedule, [])
            
            # Find indirect dependencies
            indirect = set()
            for dep in analysis['direct_dependencies'][schedule]:
                indirect.update(self.dependency_graph.get(dep, []))
            analysis['indirect_dependencies'][schedule] = list(indirect)
            
            # Build dependency chains
            analysis['dependency_chains'][schedule] = self._build_dependency_chain(schedule)
            
        return dict(analysis)

    def _build_dependency_chain(self, schedule: str, chain: List[str] = None) -> List[str]:
        """Build complete dependency chain for a schedule"""
        if chain is None:
            chain = []
            
        if schedule in chain:
            return chain
            
        chain.append(schedule)
        for dep in self.dependency_graph.get(schedule, []):
            self._build_dependency_chain(dep, chain)
            
        return chain
