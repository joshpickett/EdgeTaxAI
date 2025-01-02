class FormIntegrationService:
    def __init__(self):
        self.tax_review = TaxReviewService()
        self.tax_optimizer = TaxOptimizationService()

    async def calculateScheduleE(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Schedule E totals and validations"""
        try:
            # Calculate totals across all properties
            total_rents = sum(
                p.get("income", {}).get("rents", 0) for p in data.get("properties", [])
            )
            total_expenses = sum(
                sum(e for e in p.get("expenses", {}).values())
                for p in data.get("properties", [])
            )

            return {
                "totalRents": total_rents,
                "totalExpenses": total_expenses,
                "netIncome": total_rents - total_expenses,
                "propertyCount": len(data.get("properties", [])),
                "totalDays": sum(
                    p.get("daysRented", 0) for p in data.get("properties", [])
                ),
            }
        except Exception as e:
            self.logger.error(f"Error calculating Schedule E: {str(e)}")
            raise
