import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import sqlite3
import os
from PIL import Image
import io
import base64

# Page configuration
st.set_page_config(
    page_title="Smart Finance Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2563eb;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 0.5rem;
    }
    .alert-warning {
        background: #fef3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .alert-danger {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .insight-card {
        background: #f0f9ff;
        border-left: 4px solid #2563eb;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

class ExpenseClassifier:
    def __init__(self):
        self.categories = {
            'food': ['restaurant', 'groceries', 'cafe', 'food', 'eat', 'dining', 'supermarket', 'coffee'],
            'transport': ['uber', 'taxi', 'bus', 'train', 'fuel', 'petrol', 'metro', 'transport', 'gas'],
            'entertainment': ['movie', 'netflix', 'concert', 'game', 'entertainment', 'cinema'],
            'shopping': ['mall', 'clothes', 'amazon', 'shopping', 'store', 'fashion'],
            'bills': ['electricity', 'water', 'internet', 'bill', 'utility', 'rent', 'mortgage'],
            'healthcare': ['hospital', 'doctor', 'pharmacy', 'medical', 'health'],
            'education': ['course', 'book', 'tuition', 'school', 'university']
        }
    
    def categorize(self, description, amount):
        desc = description.lower()
        
        # Rule-based classification
        for category, keywords in self.categories.items():
            if any(keyword in desc for keyword in keywords):
                return category
        
        # Amount-based fallback
        if amount > 300: return 'shopping'
        if amount < 30: return 'miscellaneous'
        
        return 'general'

class FinanceDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('finance.db', check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                category TEXT NOT NULL,
                date DATE NOT NULL,
                type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
                currency TEXT DEFAULT 'USD',
                receipt_image TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                month TEXT NOT NULL,
                alerts_enabled BOOLEAN DEFAULT 1
            )
        ''')
        
        self.conn.commit()
    
    def add_transaction(self, description, amount, date, type, category=None, receipt_image=None):
        classifier = ExpenseClassifier()
        if not category:
            category = classifier.categorize(description, amount)
        
        self.conn.execute('''
            INSERT INTO transactions (description, amount, category, date, type, receipt_image)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (description, amount, category, date, type, receipt_image))
        self.conn.commit()
    
    def get_transactions(self, start_date=None, end_date=None, category=None, type=None):
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if category:
            query += " AND category = ?"
            params.append(category)
        if type:
            query += " AND type = ?"
            params.append(type)
        
        query += " ORDER BY date DESC"
        return pd.read_sql_query(query, self.conn, params=params)
    
    def get_spending_insights(self, start_date=None, end_date=None):
        # Get current month if no dates provided
        if not start_date or not end_date:
            today = datetime.now()
            start_date = today.replace(day=1).strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')
        
        df = self.get_transactions(start_date, end_date, type='expense')
        
        if df.empty:
            return {
                'total_spending': 0,
                'category_breakdown': pd.DataFrame(),
                'monthly_trend': pd.DataFrame()
            }
        
        category_breakdown = df.groupby('category').agg({
            'amount': ['sum', 'count']
        }).round(2)
        category_breakdown.columns = ['total', 'count']
        category_breakdown = category_breakdown.reset_index()
        
        # Monthly trend
        df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
        monthly_trend = df.groupby('month')['amount'].sum().reset_index()
        monthly_trend['month'] = monthly_trend['month'].astype(str)
        
        return {
            'total_spending': df['amount'].sum(),
            'category_breakdown': category_breakdown,
            'monthly_trend': monthly_trend
        }

class FinanceTracker:
    def __init__(self):
        self.db = FinanceDatabase()
        self.classifier = ExpenseClassifier()
    
    def add_transaction_ui(self):
        st.header("➕ Add New Transaction")
        
        with st.form("transaction_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                description = st.text_input("Description", placeholder="e.g., Grocery shopping at Walmart")
                amount = st.number_input("Amount", min_value=0.0, step=0.01, format="%.2f")
                trans_type = st.selectbox("Type", ["expense", "income"])
            
            with col2:
                date = st.date_input("Date", value=datetime.now())
                category = st.selectbox("Category", 
                    list(self.classifier.categories.keys()) + ['general', 'miscellaneous'])
                receipt = st.file_uploader("Receipt (optional)", type=['png', 'jpg', 'jpeg'])
            
            submitted = st.form_submit_button("Add Transaction")
            
            if submitted:
                if description and amount > 0:
                    receipt_data = None
                    if receipt:
                        receipt_data = base64.b64encode(receipt.read()).decode()
                    
                    self.db.add_transaction(
                        description=description,
                        amount=amount,
                        date=date.strftime('%Y-%m-%d'),
                        type=trans_type,
                        category=category,
                        receipt_image=receipt_data
                    )
                    st.success("✅ Transaction added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields")
    
    def display_dashboard(self):
        st.markdown('<h1 class="main-header">💰 Smart Finance Tracker</h1>', unsafe_allow_html=True)
        
        # Date filters
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            start_date = st.date_input("Start Date", 
                value=datetime.now().replace(day=1))
        with col2:
            end_date = st.date_input("End Date", 
                value=datetime.now())
        
        # Get insights
        insights = self.db.get_spending_insights(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        # Key metrics
        st.subheader("📊 Financial Overview")
        metric_cols = st.columns(4)
        
        with metric_cols[0]:
            total_spent = insights['total_spending']
            st.metric("Total Spent", f"${total_spent:,.2f}")
        
        with metric_cols[1]:
            total_income_df = self.db.get_transactions(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                type='income'
            )
            total_income = total_income_df['amount'].sum() if not total_income_df.empty else 0
            st.metric("Total Income", f"${total_income:,.2f}")
        
        with metric_cols[2]:
            net_flow = total_income - total_spent
            st.metric("Net Cash Flow", f"${net_flow:,.2f}", 
                     delta=f"${net_flow:,.2f}")
        
        with metric_cols[3]:
            avg_daily = total_spent / ((end_date - start_date).days + 1) if total_spent > 0 else 0
            st.metric("Avg Daily Spend", f"${avg_daily:.2f}")
        
        # Charts row
        st.subheader("📈 Spending Analytics")
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Monthly trend chart
            if not insights['monthly_trend'].empty:
                fig = px.line(insights['monthly_trend'], 
                            x='month', y='amount',
                            title="Monthly Spending Trend",
                            labels={'amount': 'Amount ($)', 'month': 'Month'})
                fig.update_traces(line=dict(color='#2563eb', width=3))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No spending data available for the selected period")
        
        with chart_col2:
            # Category breakdown
            if not insights['category_breakdown'].empty:
                fig = px.pie(insights['category_breakdown'], 
                            values='total', names='category',
                            title="Spending by Category",
                            color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No category data available")
        
        # AI Insights and Recent Transactions
        st.subheader("🤖 AI Insights & Recent Activity")
        insight_col, transaction_col = st.columns([1, 2])
        
        with insight_col:
            self.display_ai_insights(insights)
        
        with transaction_col:
            self.display_recent_transactions()
    
    def display_ai_insights(self, insights):
        st.markdown("### 💡 AI Insights")
        
        if insights['total_spending'] > 0:
            # Biggest expense
            if not insights['category_breakdown'].empty:
                biggest_expense = insights['category_breakdown'].loc[
                    insights['category_breakdown']['total'].idxmax()
                ]
                
                st.markdown(f"""
                <div class="insight-card">
                    <strong>Top Spending Category:</strong><br>
                    {biggest_expense['category'].title()} - ${biggest_expense['total']:.2f}
                </div>
                """, unsafe_allow_html=True)
            
            # Spending pattern insights
            avg_transaction = insights['total_spending'] / len(insights['category_breakdown'])
            st.markdown(f"""
            <div class="insight-card">
                <strong>Average per Category:</strong><br>
                ${avg_transaction:.2f}
            </div>
            """, unsafe_allow_html=True)
            
            # Budget alerts simulation
            if insights['total_spending'] > 1000:
                st.markdown("""
                <div class="alert-warning">
                    ⚠️ <strong>High Spending Alert:</strong> Consider reviewing your budget
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Add some transactions to see AI insights")
    
    def display_recent_transactions(self):
        st.markdown("### 📋 Recent Transactions")
        
        # Filters
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            filter_category = st.selectbox("Filter Category", 
                ["All"] + list(self.classifier.categories.keys()) + ['general', 'miscellaneous'])
        with filter_col2:
            filter_type = st.selectbox("Filter Type", ["All", "expense", "income"])
        
        # Get filtered transactions
        filters = {}
        if filter_category != "All":
            filters['category'] = filter_category
        if filter_type != "All":
            filters['type'] = filter_type
        
        transactions = self.db.get_transactions(**filters)
        
        if not transactions.empty:
            # Display as a nice table
            display_df = transactions[['date', 'description', 'amount', 'category', 'type']].head(10)
            display_df['amount'] = display_df['amount'].apply(lambda x: f"${x:.2f}")
            display_df['type'] = display_df['type'].apply(
                lambda x: f"🟢 {x}" if x == 'income' else f"🔴 {x}"
            )
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Quick stats
            st.markdown(f"**Showing {len(display_df)} most recent transactions**")
        else:
            st.info("No transactions found with the current filters")
    
    def bulk_import_ui(self):
        st.header("📥 Bulk Import Transactions")
        
        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.write("Preview of uploaded data:")
                st.dataframe(df.head())
                
                if st.button("Import Transactions"):
                    # Simple CSV import logic
                    required_columns = ['description', 'amount', 'date', 'type']
                    if all(col in df.columns for col in required_columns):
                        for _, row in df.iterrows():
                            self.db.add_transaction(
                                description=row['description'],
                                amount=row['amount'],
                                date=row['date'],
                                type=row['type']
                            )
                        st.success(f"✅ Successfully imported {len(df)} transactions!")
                    else:
                        st.error("CSV must contain columns: description, amount, date, type")
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")

def main():
    tracker = FinanceTracker()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "Add Transaction", "Bulk Import", "Advanced Analytics"]
    )
    
    # Sample data initialization
    if st.sidebar.button("Load Sample Data"):
        load_sample_data(tracker.db)
        st.sidebar.success("Sample data loaded!")
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 Tips")
    st.sidebar.info("""
    - Use descriptive transaction names for better AI categorization
    - Upload receipts for better expense tracking
    - Set monthly budgets to get spending alerts
    """)
    
    # Page routing
    if page == "Dashboard":
        tracker.display_dashboard()
    elif page == "Add Transaction":
        tracker.add_transaction_ui()
    elif page == "Bulk Import":
        tracker.bulk_import_ui()
    elif page == "Advanced Analytics":
        show_advanced_analytics(tracker.db)

def load_sample_data(db):
    """Load sample transactions for demonstration"""
    sample_data = [
        ("Groceries at Walmart", 85.50, "2024-01-15", "expense", "food"),
        ("Uber ride to airport", 45.00, "2024-01-16", "expense", "transport"),
        ("Netflix subscription", 15.99, "2024-01-17", "expense", "entertainment"),
        ("Salary deposit", 2500.00, "2024-01-15", "income", "general"),
        ("Amazon shopping", 120.75, "2024-01-18", "expense", "shopping"),
        ("Electricity bill", 85.00, "2024-01-19", "expense", "bills"),
        ("Dinner at restaurant", 65.25, "2024-01-20", "expense", "food"),
        ("Gas station", 45.50, "2024-01-21", "expense", "transport"),
    ]
    
    for desc, amount, date, type, category in sample_data:
        db.add_transaction(desc, amount, date, type, category)

def show_advanced_analytics(db):
    st.header("📊 Advanced Analytics")
    
    # Get all transactions
    transactions = db.get_transactions()
    
    if transactions.empty:
        st.info("No transaction data available for analytics")
        return
    
    # Convert to datetime
    transactions['date'] = pd.to_datetime(transactions['date'])
    
    # Spending patterns analysis
    st.subheader("Spending Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily spending heatmap
        daily_spending = transactions[transactions['type'] == 'expense'].groupby(
            transactions['date'].dt.date
        )['amount'].sum().reset_index()
        
        if not daily_spending.empty:
            fig = px.bar(daily_spending, x='date', y='amount',
                        title="Daily Spending Pattern")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Category trend over time
        category_trend = transactions[transactions['type'] == 'expense']
        if not category_trend.empty:
            category_trend['month'] = category_trend['date'].dt.to_period('M')
            monthly_category = category_trend.groupby(['month', 'category'])['amount'].sum().reset_index()
            monthly_category['month'] = monthly_category['month'].astype(str)
            
            fig = px.line(monthly_category, x='month', y='amount', color='category',
                         title="Category Trends Over Time")
            st.plotly_chart(fig, use_container_width=True)
    
    # Predictive insights
    st.subheader("Predictive Insights")
    
    if len(transactions) > 10:
        # Simple prediction based on average
        avg_monthly_spending = transactions[transactions['type'] == 'expense'].groupby(
            transactions['date'].dt.to_period('M')
        )['amount'].sum().mean()
        
        next_month = (datetime.now() + timedelta(days=30)).strftime('%B %Y')
        
        st.markdown(f"""
        <div class="insight-card">
            <strong>Next Month Prediction:</strong><br>
            Based on your spending patterns, we predict you'll spend approximately 
            <strong>${avg_monthly_spending:.2f}</strong> in {next_month}
        </div>
        """, unsafe_allow_html=True)
        
        # Spending comparison
        current_month = datetime.now().strftime('%Y-%m')
        last_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')
        
        current_spending = transactions[
            (transactions['type'] == 'expense') & 
            (transactions['date'].dt.to_period('M') == current_month)
        ]['amount'].sum()
        
        last_spending = transactions[
            (transactions['type'] == 'expense') & 
            (transactions['date'].dt.to_period('M') == last_month)
        ]['amount'].sum()
        
        if last_spending > 0:
            change_pct = ((current_spending - last_spending) / last_spending) * 100
            trend = "up" if change_pct > 0 else "down"
            
            st.markdown(f"""
            <div class="insight-card">
                <strong>Monthly Comparison:</strong><br>
                Your spending is <strong>{abs(change_pct):.1f}% {trend}</strong> compared to last month
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()