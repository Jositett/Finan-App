# Smart Finance Tracker

## Description

A comprehensive finance tracking application built with Streamlit that provides AI-powered categorization, interactive dashboards, and advanced analytics for managing personal finances. This application helps users track income and expenses, visualize spending patterns, and gain insights into their financial habits through automatic transaction categorization and predictive analytics.

## Key Features Implemented

### Core Features
- **AI-powered categorization**: Automatically categorizes transactions based on descriptions using rule-based classification
- **Interactive dashboards**: Real-time financial overview with metrics, charts, and spending analytics
- **Receipt upload**: Support for image upload and storage of transaction receipts
- **Transaction management**: Add, view, and filter transactions by date, category, and type
- **Sample data**: Load sample transactions for demonstration purposes

### Analytics & Insights
- **Spending insights**: Category breakdowns, monthly trends, and spending patterns
- **Predictive analytics**: Monthly spending predictions based on historical data
- **Comparative analysis**: Month-over-month spending comparisons
- **Interactive filters**: Date range and category filtering for customized views
- **Budget alerts**: Warnings for high spending amounts

### Data Management
- **Bulk import**: CSV import functionality for batch transaction uploads
- **Database storage**: SQLite-based persistent storage for all transaction data
- **Multi-currency support**: Ready for international use (currently set to USD default)
- **Data export**: Built-in data retrieval and display capabilities

## Installation Instructions

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Dependencies
Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

The application requires the following dependencies:
- `streamlit`: Web application framework
- `pandas`: Data manipulation and analysis
- `plotly`: Interactive charts and visualizations
- `numpy`: Numerical computing
- `pillow`: Image processing for receipt uploads

## How to Run the Application

1. Ensure you have Python 3.8+ installed on your system
2. Clone or download the project files to your local machine
3. Open a terminal and navigate to the project directory (`Finan-App`)
4. Install the dependencies as shown above
5. Run the Streamlit application:

```bash
streamlit run app.py
```

6. The application will automatically open in your default web browser at `http://localhost:8501`
7. If it doesn't open automatically, manually navigate to the URL in your browser

### Getting Started
- Use the sidebar to navigate between different sections (Dashboard, Add Transaction, Bulk Import, Advanced Analytics)
- Click "Load Sample Data" to populate the app with example transactions for testing
- Start adding your own transactions or import them via CSV

## Project Structure

```
Finan-App/
├── app.py                 # Main Streamlit application file containing all UI and logic
├── requirements.txt       # Python package dependencies
├── README.md             # This documentation file
└── finance.db            # SQLite database (created automatically on first run)
```

### File Descriptions
- **`app.py`**: The main application file containing:
  - `ExpenseClassifier`: Class for AI-powered transaction categorization
  - `FinanceDatabase`: SQLite database management and queries
  - `FinanceTracker`: Main application logic and UI components
  - Streamlit page layouts and navigation

- **`requirements.txt`**: Lists all Python packages required to run the application

- **`finance.db`**: SQLite database file that stores:
  - Transaction records (description, amount, category, date, type)
  - Budget information (future implementation)
  - Receipt images (base64 encoded)

## Deployment Notes

**Deployment has not yet been implemented** for this project. The application currently runs only in local development mode using Streamlit's built-in server.

### Future Deployment Options
When deployment is implemented, possible platforms include:
- **Streamlit Cloud**: One-click deployment for Streamlit apps
- **Heroku**: Cloud platform supporting Python applications
- **AWS/GCP/Azure**: Major cloud providers for scalable deployment
- **Docker**: Containerization for consistent deployment across environments

### Deployment Requirements
Future deployment will require:
- Database migration (from local SQLite to cloud database)
- Environment variable configuration
- Security considerations for data storage
- CDN setup for static assets (if any)
- Monitoring and logging setup