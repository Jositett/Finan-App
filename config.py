# Configuration constants for the Finance Tracker app

# Database configuration
DB_PATH = 'finance.db'
DEFAULT_CURRENCY = 'USD'

# Categories for expense classification
CATEGORIES = {
    'food': ['restaurant', 'groceries', 'cafe', 'food', 'eat', 'dining', 'supermarket', 'coffee'],
    'transport': ['uber', 'taxi', 'bus', 'train', 'fuel', 'petrol', 'metro', 'transport', 'gas'],
    'entertainment': ['movie', 'netflix', 'concert', 'game', 'entertainment', 'cinema'],
    'shopping': ['mall', 'clothes', 'amazon', 'shopping', 'store', 'fashion'],
    'bills': ['electricity', 'water', 'internet', 'bill', 'utility', 'rent', 'mortgage'],
    'healthcare': ['hospital', 'doctor', 'pharmacy', 'medical', 'health'],
    'education': ['course', 'book', 'tuition', 'school', 'university'],
    'miscellaneous': ['misc', 'other', 'miscellaneous', 'gift', 'donation']
}


# Page configuration
PAGE_CONFIG = {
    "page_title": "Smart Finance Tracker",
    "page_icon": "💰",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Custom CSS for styling
CUSTOM_CSS = """
<style>
    :root {
        --primary-blue: #2563eb;
        --secondary-purple: #7c3aed;
        --accent-purple: #a855f7;
        --light-bg: #f8fafc;
        --card-bg: #ffffff;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --border-radius: 12px;
        --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }

    * {
        font-family: var(--font-family);
    }

    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-blue), var(--secondary-purple));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
    }

    .metric-card {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-md);
        margin: 0.75rem;
        border: 1px solid rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }

    .alert-warning {
        background: linear-gradient(135deg, #fef3cd, #fef7e0);
        border: 1px solid #f59e0b;
        border-radius: var(--border-radius);
        padding: 1rem;
        margin: 0.75rem 0;
        box-shadow: var(--shadow-sm);
        color: #92400e;
    }

    .alert-danger {
        background: linear-gradient(135deg, #fef2f2, #fee2e2);
        border: 1px solid #ef4444;
        border-radius: var(--border-radius);
        padding: 1rem;
        margin: 0.75rem 0;
        box-shadow: var(--shadow-sm);
        color: #991b1b;
    }

    .insight-card {
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        border-left: 4px solid var(--primary-blue);
        padding: 1.25rem;
        margin: 0.75rem 0;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-sm);
        color: #1e40af;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-blue), var(--accent-purple));
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, var(--secondary-purple), var(--accent-purple));
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }

    /* Form elements */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stNumberInput > div > div > input {
        border: 2px solid rgba(0, 0, 0, 0.1);
        border-radius: 8px;
        padding: 0.75rem;
        font-size: 0.95rem;
        transition: border-color 0.2s ease;
    }

    /* Fix dropdown truncation */
    .stSelectbox > div > div > div {
        min-height: 45px !important;
        height: auto !important;
        line-height: normal !important;
        display: flex !important;
        align-items: center !important;
        overflow: visible !important;
    }

    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary-blue);
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        outline: none;
    }

    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
            margin-bottom: 1.5rem;
        }

        .metric-card {
            padding: 1rem;
            margin: 0.5rem;
        }

        .alert-warning,
        .alert-danger,
        .insight-card {
            padding: 0.75rem;
            margin: 0.5rem 0;
        }

        .stButton > button {
            padding: 0.6rem 1.2rem;
            font-size: 0.9rem;
        }
    }

    /* Typography hierarchy */
    h1 { font-size: 2.25rem; font-weight: 700; margin-bottom: 1rem; }
    h2 { font-size: 1.875rem; font-weight: 600; margin-bottom: 0.875rem; }
    h3 { font-size: 1.5rem; font-weight: 600; margin-bottom: 0.75rem; }
    p { line-height: 1.6; margin-bottom: 1rem; }

    /* General body improvements */
    body {
        background: var(--light-bg);
        color: #374151;
    }
</style>
"""

# Sample data for demonstration
SAMPLE_DATA = [
    ("Groceries at Walmart", 85.50, "2025-09-15", "expense", "food"),
    ("Uber ride to airport", 45.00, "2025-09-16", "expense", "transport"),
    ("Netflix subscription", 15.99, "2025-09-17", "expense", "entertainment"),
    ("Salary deposit", 2500.00, "2025-09-15", "income", "general"),
    ("Amazon shopping", 120.75, "2025-09-18", "expense", "shopping"),
    ("Electricity bill", 85.00, "2025-08-19", "expense", "bills"),
    ("Dinner at restaurant", 65.25, "2025-08-20", "expense", "food"),
    ("Gas station", 45.50, "2025-08-21", "expense", "transport"),
    ("Coffee at Starbucks", 4.50, "2023-01-05", "expense", "food"),
    ("Bus ticket", 2.75, "2023-01-10", "expense", "transport"),
    ("Movie tickets", 28.00, "2023-01-15", "expense", "entertainment"),
    ("Book purchase", 15.99, "2023-01-20", "expense", "education"),
    ("Doctor visit", 150.00, "2023-01-25", "expense", "healthcare"),
    ("Groceries", 120.00, "2023-02-05", "expense", "food"),
    ("Uber ride", 12.00, "2023-02-10", "expense", "transport"),
    ("Spotify subscription", 9.99, "2023-02-15", "expense", "entertainment"),
    ("Online course", 49.99, "2023-02-20", "expense", "education"),
    ("Pharmacy", 25.00, "2023-02-25", "expense", "healthcare"),
    ("Rent payment", 1200.00, "2023-03-01", "expense", "bills"),
    ("Grocery shopping", 95.50, "2023-03-05", "expense", "food"),
    ("Train ticket", 15.00, "2023-03-10", "expense", "transport"),
    ("Concert tickets", 85.00, "2023-03-15", "expense", "entertainment"),
    ("Clothes from H&M", 60.00, "2023-03-20", "expense", "shopping"),
    ("Freelance payment", 500.00, "2023-03-25", "income", "general"),
    ("Water bill", 35.00, "2023-04-01", "expense", "bills"),
    ("Restaurant dinner", 75.00, "2023-04-05", "expense", "food"),
    ("Gas for car", 50.00, "2023-04-10", "expense", "transport"),
    ("Netflix subscription", 15.99, "2023-04-15", "expense", "entertainment"),
    ("Online shopping", 45.00, "2023-04-20", "expense", "shopping"),
    ("Dividend income", 200.00, "2023-04-25", "income", "general"),
    ("Internet bill", 60.00, "2023-05-01", "expense", "bills"),
    ("Cafe lunch", 12.50, "2023-05-05", "expense", "food"),
    ("Taxi ride", 20.00, "2023-05-10", "expense", "transport"),
    ("Video game", 59.99, "2023-05-15", "expense", "entertainment"),
    ("Gift for friend", 30.00, "2023-05-20", "expense", "miscellaneous"),
    ("Salary", 2500.00, "2023-05-25", "income", "general"),
    ("Electricity bill", 90.00, "2023-06-01", "expense", "bills"),
    ("Supermarket", 110.00, "2023-06-05", "expense", "food"),
    ("Fuel", 55.00, "2023-06-10", "expense", "transport"),
    ("Movie rental", 5.99, "2023-06-15", "expense", "entertainment"),
    ("Books for study", 40.00, "2023-06-20", "expense", "education"),
    ("Medical checkup", 100.00, "2023-06-25", "expense", "healthcare"),
    ("Side hustle", 300.00, "2023-07-05", "income", "general"),
    ("Groceries", 80.00, "2023-07-10", "expense", "food"),
    ("Bus pass", 25.00, "2023-07-15", "expense", "transport"),
    ("Concert", 120.00, "2023-07-20", "expense", "entertainment"),
    ("Shopping mall", 150.00, "2023-07-25", "expense", "shopping"),
    ("Rent", 1200.00, "2023-08-01", "expense", "bills"),
    ("Restaurant", 55.00, "2023-08-05", "expense", "food"),
    ("Uber", 18.00, "2023-08-10", "expense", "transport"),
    ("Streaming service", 12.99, "2023-08-15", "expense", "entertainment"),
    ("Tuition fee", 500.00, "2023-08-20", "expense", "education"),
    ("Dentist", 200.00, "2023-08-25", "expense", "healthcare"),
    ("Bonus payment", 1000.00, "2023-09-01", "income", "general"),
    ("Groceries", 105.00, "2023-09-05", "expense", "food"),
    ("Train ride", 8.50, "2023-09-10", "expense", "transport"),
    ("Gaming subscription", 14.99, "2023-09-15", "expense", "entertainment"),
    ("Online course", 79.99, "2023-09-20", "expense", "education"),
    ("Prescription", 15.00, "2023-09-25", "expense", "healthcare"),
    ("Water bill", 30.00, "2023-10-01", "expense", "bills"),
    ("Dinner out", 70.00, "2023-10-05", "expense", "food"),
    ("Gas station", 48.00, "2023-10-10", "expense", "transport"),
    ("Theater tickets", 40.00, "2023-10-15", "expense", "entertainment"),
    ("Clothing", 80.00, "2023-10-20", "expense", "shopping"),
    ("Freelance work", 400.00, "2023-10-25", "income", "general"),
    ("Internet", 65.00, "2023-11-01", "expense", "bills"),
    ("Cafe", 6.00, "2023-11-05", "expense", "food"),
    ("Metro", 3.00, "2023-11-10", "expense", "transport"),
    ("Movie", 12.00, "2023-11-15", "expense", "entertainment"),
    ("Book", 25.00, "2023-11-20", "expense", "education"),
    ("Doctor", 120.00, "2023-11-25", "expense", "healthcare"),
    ("Salary", 2500.00, "2023-12-01", "income", "general"),
    ("Christmas gifts", 200.00, "2023-12-10", "expense", "miscellaneous"),
    ("Groceries", 130.00, "2023-12-15", "expense", "food"),
    ("Rental car", 150.00, "2023-12-20", "expense", "transport"),
    ("Holiday entertainment", 50.00, "2023-12-25", "expense", "entertainment"),
    ("Electricity", 95.00, "2024-01-01", "expense", "bills"),
    ("New Year dinner", 80.00, "2024-01-05", "expense", "food"),
    ("Taxi", 22.00, "2024-01-10", "expense", "transport"),
    ("Subscription", 9.99, "2024-01-15", "expense", "entertainment"),
    ("Course fee", 99.99, "2024-01-20", "expense", "education"),
    ("Pharmacy", 20.00, "2024-01-25", "expense", "healthcare"),
    ("Dividend", 150.00, "2024-02-01", "income", "general"),
    ("Groceries", 90.00, "2024-02-05", "expense", "food"),
    ("Bus", 2.50, "2024-02-10", "expense", "transport"),
    ("Concert", 100.00, "2024-02-15", "expense", "entertainment"),
    ("Online shopping", 65.00, "2024-02-20", "expense", "shopping"),
    ("Water bill", 32.00, "2024-03-01", "expense", "bills"),
    ("Restaurant", 60.00, "2024-03-05", "expense", "food"),
    ("Fuel", 52.00, "2024-03-10", "expense", "transport"),
    ("Video game", 49.99, "2024-03-15", "expense", "entertainment"),
    ("Bookstore", 35.00, "2024-03-20", "expense", "education"),
    ("Medical", 180.00, "2024-03-25", "expense", "healthcare"),
    ("Freelance", 350.00, "2024-04-01", "income", "general"),
    ("Supermarket", 115.00, "2024-04-05", "expense", "food"),
    ("Uber", 14.00, "2024-04-10", "expense", "transport"),
    ("Streaming", 11.99, "2024-04-15", "expense", "entertainment"),
    ("Tuition", 600.00, "2024-04-20", "expense", "education"),
    ("Hospital", 250.00, "2024-04-25", "expense", "healthcare"),
    ("Rent", 1200.00, "2024-05-01", "expense", "bills"),
    ("Dinner", 55.00, "2024-05-05", "expense", "food"),
    ("Train", 10.00, "2024-05-10", "expense", "transport"),
    ("Movie tickets", 25.00, "2024-05-15", "expense", "entertainment"),
    ("Clothes", 75.00, "2024-05-20", "expense", "shopping"),
    ("Salary", 2600.00, "2024-05-25", "income", "general"),
    ("Electricity", 88.00, "2024-06-01", "expense", "bills"),
    ("Groceries", 100.00, "2024-06-05", "expense", "food"),
    ("Gas", 47.00, "2024-06-10", "expense", "transport"),
    ("Game", 39.99, "2024-06-15", "expense", "entertainment"),
    ("Course", 59.99, "2024-06-20", "expense", "education"),
    ("Pharmacy", 18.00, "2024-06-25", "expense", "healthcare"),
    ("Bonus", 800.00, "2024-07-01", "income", "general"),
    ("Cafe", 5.50, "2024-07-05", "expense", "food"),
    ("Bus pass", 30.00, "2024-07-10", "expense", "transport"),
    ("Concert", 95.00, "2024-07-15", "expense", "entertainment"),
    ("Shopping", 140.00, "2024-07-20", "expense", "shopping"),
    ("Internet", 62.00, "2024-08-01", "expense", "bills"),
    ("Restaurant", 72.00, "2024-08-05", "expense", "food"),
    ("Uber", 16.00, "2024-08-10", "expense", "transport"),
    ("Subscription", 13.99, "2024-08-15", "expense", "entertainment"),
    ("Books", 45.00, "2024-08-20", "expense", "education"),
    ("Doctor visit", 110.00, "2024-08-25", "expense", "healthcare"),
    ("Dividends", 180.00, "2024-09-01", "income", "general"),
    ("Groceries", 125.00, "2024-09-05", "expense", "food"),
    ("Taxi", 19.00, "2024-09-10", "expense", "transport"),
    ("Theater", 35.00, "2024-09-15", "expense", "entertainment"),
    ("Mall shopping", 90.00, "2024-09-20", "expense", "shopping"),
    ("Water", 28.00, "2024-10-01", "expense", "bills"),
    ("Dinner", 65.00, "2024-10-05", "expense", "food"),
    ("Fuel", 53.00, "2024-10-10", "expense", "transport"),
    ("Movie", 14.00, "2024-10-15", "expense", "entertainment"),
    ("Online course", 89.99, "2024-10-20", "expense", "education"),
    ("Medical", 140.00, "2024-10-25", "expense", "healthcare"),
    ("Freelance", 450.00, "2024-11-01", "income", "general"),
    ("Supermarket", 110.00, "2024-11-05", "expense", "food"),
    ("Bus", 2.75, "2024-11-10", "expense", "transport"),
    ("Concert", 110.00, "2024-11-15", "expense", "entertainment"),
    ("Clothing", 55.00, "2024-11-20", "expense", "shopping"),
    ("Electricity", 92.00, "2024-12-01", "expense", "bills"),
    ("Cafe", 7.00, "2024-12-05", "expense", "food"),
    ("Uber", 13.00, "2024-12-10", "expense", "transport"),
    ("Gift", 40.00, "2024-12-15", "expense", "miscellaneous"),
    ("Salary", 2700.00, "2024-12-20", "income", "general"),
    ("Holiday shopping", 120.00, "2024-12-25", "expense", "shopping"),
    ("New Year party", 60.00, "2024-12-30", "expense", "entertainment"),
]
