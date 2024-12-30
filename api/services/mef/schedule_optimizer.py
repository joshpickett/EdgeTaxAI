from typing import List, Dict, Any
import logging
from collections import defaultdict
from decimal import Decimal
from datetime import datetime

class ScheduleOptimizer:
    """Optimize schedule processing order and dependencies"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.dependency_graph = {
            'SCHEDULE_C': ['1040'],
            'SCHEDULE_SE': ['1040', 'SCHEDULE_C'],
            'SCHEDULE_E': ['1040'],
            'SCHEDULE_F': ['1040'],
            'FORM_1116': ['1040'],
            'FORM_2555': ['1040'],
            'FORM_8938': ['1040'],
            'FORM_8621': ['1040'],  # PFIC form
            'FINCEN_114': [],  # FBAR doesn't depend on other forms
            'SCHEDULE_B': ['1040']  # For foreign accounts
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

    async def optimize_foreign_income(self, income_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize foreign income reporting and exclusions"""
        try:
            optimizations = {
                'foreign_earned_income_exclusion': self._calculate_feie(income_data),
                'foreign_housing_exclusion': self._calculate_housing_exclusion(income_data),
                'foreign_tax_credit': self._optimize_foreign_tax_credit(income_data),
                'treaty_benefits': self._analyze_treaty_benefits(income_data)
            }
            
            return {
                'optimizations': optimizations,
                'recommended_forms': self._determine_required_forms(optimizations),
                'total_savings': self._calculate_total_savings(optimizations)
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing foreign income: {str(e)}")
            raise

    def _calculate_feie(self, income_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Foreign Earned Income Exclusion"""
        max_exclusion = Decimal('120000')  # 2023 limit
        foreign_earned_income = Decimal(str(income_data.get('foreign_earned_income', 0)))
        
        exclusion_amount = min(foreign_earned_income, max_exclusion)
        
        return {
            'amount': exclusion_amount,
            'qualifies': self._qualifies_for_feie(income_data),
            'remaining_income': max(foreign_earned_income - exclusion_amount, Decimal('0'))
        }

    def _calculate_housing_exclusion(self, income_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Foreign Housing Exclusion"""
        base_amount = Decimal('17654')  # 2023 base amount
        max_amount = Decimal('33384')   # 2023 maximum
        
        housing_expenses = Decimal(str(income_data.get('foreign_housing_expenses', 0)))
        qualified_expenses = max(housing_expenses - base_amount, Decimal('0'))
        exclusion_amount = min(qualified_expenses, max_amount)
        
        return {
            'amount': exclusion_amount,
            'qualifies': housing_expenses > base_amount,
            'excess_expenses': max(housing_expenses - max_amount, Decimal('0'))
        }

    def _optimize_foreign_tax_credit(self, income_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize Foreign Tax Credit calculations"""
        foreign_taxes = {}
        total_credit = Decimal('0')
        
        for country, data in income_data.get('foreign_taxes', {}).items():
            taxes_paid = Decimal(str(data.get('amount', 0)))
            income = Decimal(str(data.get('income', 0)))
            
            # Calculate effective tax rate
            effective_rate = taxes_paid / income if income > 0 else Decimal('0')
            
            # Check if credit or deduction is more beneficial
            credit_benefit = self._calculate_credit_benefit(taxes_paid)
            deduction_benefit = self._calculate_deduction_benefit(taxes_paid)
            
            optimal_method = 'credit' if credit_benefit > deduction_benefit else 'deduction'
            optimal_amount = max(credit_benefit, deduction_benefit)
            
            foreign_taxes[country] = {
                'optimal_method': optimal_method,
                'optimal_amount': optimal_amount,
                'effective_rate': effective_rate
            }
            
            if optimal_method == 'credit':
                total_credit += taxes_paid
                
        return {
            'country_analysis': foreign_taxes,
            'total_credit': total_credit,
            'recommendations': self._generate_ftc_recommendations(foreign_taxes)
        }

    def _optimize_pfic_calculations(self, pfic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize PFIC (Passive Foreign Investment Company) calculations"""
        try:
            optimizations = {}
            
            for investment, data in pfic_data.items():
                # Calculate QEF election benefit
                qef_benefit = self._calculate_qef_benefit(data)
                
                # Calculate Mark-to-Market election benefit
                mtm_benefit = self._calculate_mtm_benefit(data)
                
                # Calculate Section 1291 fund implications
                section_1291 = self._calculate_1291_implications(data)
                
                optimal_treatment = self._determine_optimal_pfic_treatment(
                    qef_benefit,
                    mtm_benefit,
                    section_1291
                )
                
                optimizations[investment] = {
                    'optimal_treatment': optimal_treatment,
                    'qef_benefit': qef_benefit,
                    'mtm_benefit': mtm_benefit,
                    'section_1291_impact': section_1291,
                    'recommendations': self._generate_pfic_recommendations(
                        optimal_treatment,
                        data
                    )
                }
            
            return {
                'optimizations': optimizations,
                'total_benefit': self._calculate_total_pfic_benefit(optimizations)
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing PFIC calculations: {str(e)}")
            raise

    def _calculate_qef_benefit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate benefit of Qualified Electing Fund election"""
        ordinary_earnings = Decimal(str(data.get('ordinary_earnings', 0)))
        net_capital_gain = Decimal(str(data.get('net_capital_gain', 0)))
        
        return {
            'current_inclusion': ordinary_earnings + net_capital_gain,
            'character_benefit': net_capital_gain,  # Preserves capital gain character
            'basis_adjustment': ordinary_earnings + net_capital_gain
        }

    def _calculate_mtm_benefit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate benefit of Mark-to-Market election"""
        starting_value = Decimal(str(data.get('starting_value', 0)))
        ending_value = Decimal(str(data.get('ending_value', 0)))
        
        unrealized_gain = ending_value - starting_value
        
        return {
            'unrealized_gain': unrealized_gain,
            'ordinary_character': unrealized_gain,  # All gains are ordinary
            'basis_adjustment': unrealized_gain if unrealized_gain > 0 else Decimal('0')
        }

    def _calculate_1291_implications(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate implications of Section 1291 fund treatment"""
        holding_period = data.get('holding_period', 0)
        excess_distributions = Decimal(str(data.get('excess_distributions', 0)))
        
        return {
            'excess_distributions': excess_distributions,
            'deferred_tax': self._calculate_deferred_tax(excess_distributions, holding_period),
            'interest_charge': self._calculate_interest_charge(excess_distributions, holding_period)
        }

    ...rest of the code...
