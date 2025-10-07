from config import CATEGORIES

class ExpenseClassifier:
    def __init__(self):
        self.categories = CATEGORIES

    def categorize(self, description, amount):
        """
        Categorize a transaction based on description and amount.

        Args:
            description (str): Transaction description
            amount (float): Transaction amount

        Returns:
            str: Category name

        Raises:
            ValueError: If inputs are invalid
        """
        # Input validation
        if description is None or not isinstance(description, str):
            raise ValueError("Description must be a non-empty string")

        if amount is None or not isinstance(amount, (int, float)):
            raise ValueError("Amount must be a number")

        if amount <= 0:
            raise ValueError("Amount must be positive")

        desc = description.lower().strip()

        if not desc:
            raise ValueError("Description cannot be empty after stripping whitespace")

        # Rule-based classification
        for category, keywords in self.categories.items():
            if any(keyword in desc for keyword in keywords):
                return category

        # Amount-based fallback
        if amount > 300:
            return 'shopping'
        elif amount < 30:
            return 'miscellaneous'

        return 'general'