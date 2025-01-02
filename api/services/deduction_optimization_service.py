class DeductionOptimizationService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.calculator = TaxCalculator()
        self.deduction_limits = {
            # Add farm-specific deduction limits
            "farm_deductions": Decimal("100000"),
            "home_office": {
                "max_percentage": Decimal("0.25"),
                "min_area": 100
            },
            "vehicle": {
                "mileage_rate": Decimal("0.655")
            }
        }

    def analyze_deductions(self, tax_data: Dict[str, Any]) -> Dict[str, Any]:
        deductions = {
            "business": self._analyze_business_deductions(tax_data),
            "vehicle": self._analyze_vehicle_deductions(tax_data),
            "farm": self._analyze_farm_deductions(tax_data),
            "home_office": self._analyze_home_office_deductions(tax_data)
        }

        return deductions

    def _analyze_farm_deductions(self, tax_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze farm-related deductions"""
        try:
            farm_expenses = Decimal(str(tax_data.get("farm_expenses", 0)))
            equipment_costs = Decimal(str(tax_data.get("farm_equipment_costs", 0)))
            supply_costs = Decimal(str(tax_data.get("farm_supply_costs", 0)))
            labor_costs = Decimal(str(tax_data.get("farm_labor_costs", 0)))

            # Calculate total deductions
            total_deductions = min(
                farm_expenses + equipment_costs + supply_costs + labor_costs,
                self.deduction_limits["farm_deductions"]
            )

            # Calculate optimization opportunities
            opportunities = []
            if equipment_costs > 0:
                opportunities.append({
                    "type": "depreciation",
                    "description": "Consider Section 179 depreciation for farm equipment",
                    "potential_savings": equipment_costs * Decimal("0.25")
                })

            return {
                "total_deductions": total_deductions,
                "equipment_costs": equipment_costs,
                "supply_costs": supply_costs,
                "labor_costs": labor_costs,
                "opportunities": opportunities
            }

        except Exception as e:
            self.logger.error(f"Error analyzing farm deductions: {str(e)}")
            raise

    # ...rest of the code...
