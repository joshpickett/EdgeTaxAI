import openai
from typing import Dict, Any
import os
import logging
from datetime import datetime


class AITransactionAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key

    def analyze_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a transaction using artificial intelligence to determine if it's a business expense or income"""
        try:
            # Prepare transaction data for analysis
            prompt = self._create_analysis_prompt(transaction)

            # Call OpenAI application programming interface
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial expert analyzing bank transactions. "
                        "Focus on identifying tax deduction opportunities and categorizing expenses according to IRS guidelines. "
                        "Determine if each transaction is a business expense, business income, "
                        "or personal transaction. Provide category and confidence score.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            # Parse and return analysis
            return self._parse_ai_response(response.choices[0].message["content"])

        except Exception as exception:
            logging.error(
                f"Error in artificial intelligence transaction analysis: {exception}"
            )
            return {
                "is_business_expense": False,
                "is_business_income": False,
                "confidence_score": 0.0,
                "category": "UNKNOWN",
            }

    def _create_analysis_prompt(self, transaction: Dict[str, Any]) -> str:
        """Create prompt for artificial intelligence analysis"""
        return f"""
        Please analyze this transaction:
        Amount: ${transaction['amount']}
        Description: {transaction['description']}
        Merchant: {transaction.get('merchant_name', 'Unknown')}
        Date: {transaction['date']}
        Category (if available): {transaction.get('category', [''])[0]}
        
        Determine if this is:
        1. A business expense
        2. Business income
        3. Personal transaction
        
        Provide:
        - Classification
        - Confidence score (0-1)
        - Suggested category
        - Reasoning
        """

    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse artificial intelligence response into structured data"""
        try:
            # Basic parsing logic - this could be enhanced based on actual response format
            is_expense = "business expense" in response.lower()
            is_income = "business income" in response.lower()

            # Extract confidence score (assuming it's mentioned in the response)
            confidence_score = 0.7  # Default value
            if "confidence: " in response.lower():
                confidence_part = (
                    response.lower().split("confidence: ")[1].split("\n")[0]
                )
                try:
                    confidence_score = float(confidence_part)
                except:
                    pass

            # Extract category
            category = "UNKNOWN"
            if "category: " in response.lower():
                category = (
                    response.lower().split("category: ")[1].split("\n")[0].upper()
                )

            # Enhanced tax-specific analysis
            tax_category = self._determine_tax_category(category, response)
            deduction_potential = self._assess_deduction_potential(response)

            return {
                "is_business_expense": is_expense,
                "is_business_income": is_income,
                "confidence_score": confidence_score,
                "category": category,
                "ai_analysis": response,
            }

        except Exception as exception:
            logging.error(
                f"Error parsing artificial intelligence response: {exception}"
            )
            return {
                "is_business_expense": False,
                "is_business_income": False,
                "confidence_score": 0.0,
                "category": "UNKNOWN",
                "ai_analysis": response,
            }
