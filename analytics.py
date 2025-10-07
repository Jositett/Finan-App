import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import streamlit as st
from config import CUSTOM_CSS
from database import FinanceDatabase

class Analytics:
    def __init__(self, db: FinanceDatabase, user_id: int):
        self.db = db
        self.user_id = user_id

    def get_spending_insights(self, user_id=None, start_date=None, end_date=None):
        """Get spending insights with error handling."""
        try:
            return self.db.get_spending_insights(user_id or self.user_id, start_date, end_date)
        except Exception as e:
            st.error(f"Failed to get spending insights: {e}")
            return {
                'total_spending': 0,
                'category_breakdown': pd.DataFrame(),
                'monthly_trend': pd.DataFrame()
            }

    def generate_monthly_trend_chart(self, insights):
        """Generate monthly spending trend chart."""
        if insights['monthly_trend'].empty:
            st.info("No data available for monthly trend")
            return None

        try:
            fig = px.line(insights['monthly_trend'],
                         x='month', y='amount',
                         title="Monthly Spending Trend",
                         labels={'amount': 'Amount ($)', 'month': 'Month'})
            fig.update_traces(line=dict(color='#2563eb', width=3))
            return fig
        except Exception as e:
            st.error(f"Failed to generate monthly trend chart: {e}")
            return None

    def generate_category_pie_chart(self, insights):
        """Generate category breakdown pie chart."""
        if insights['category_breakdown'].empty:
            st.info("No category data available")
            return None

        try:
            fig = px.pie(insights['category_breakdown'],
                         values='total', names='category',
                         title="Spending by Category",
                         color_discrete_sequence=px.colors.qualitative.Set3)
            return fig
        except Exception as e:
            st.error(f"Failed to generate category pie chart: {e}")
            return None

    def display_ai_insights(self, insights):
        """Display AI insights with error handling."""
        st.markdown("### 💡 AI Insights")

        if insights['total_spending'] <= 0:
            st.info("Add some transactions to see AI insights")
            return

        try:
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

            # Average per category
            if len(insights['category_breakdown']) > 0:
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
        except Exception as e:
            st.error(f"Failed to display AI insights: {e}")

def show_advanced_analytics(db: FinanceDatabase, user_id: int):
    """Show advanced analytics page."""
    st.header("📊 Advanced Analytics")

    try:
        # Get all transactions
        transactions = db.get_transactions(user_id)

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
                try:
                    fig = px.bar(daily_spending, x='date', y='amount',
                                 title="Daily Spending Pattern")
                    st.plotly_chart(fig, width='stretch')
                except Exception as e:
                    st.error(f"Failed to generate daily spending chart: {e}")

        with col2:
            # Category trend over time
            category_trend = transactions[transactions['type'] == 'expense']
            if not category_trend.empty:
                try:
                    category_trend['month'] = category_trend['date'].dt.to_period('M')
                    monthly_category = category_trend.groupby(['month', 'category'])['amount'].sum().reset_index()
                    monthly_category['month'] = monthly_category['month'].astype(str)

                    fig = px.line(monthly_category, x='month', y='amount', color='category',
                                  title="Category Trends Over Time")
                    st.plotly_chart(fig, width='stretch')
                except Exception as e:
                    st.error(f"Failed to generate category trend chart: {e}")

        # Predictive insights
        st.subheader("Predictive Insights")

        if len(transactions) > 10:
            try:
                # Simple prediction based on average
                avg_monthly_spending = transactions[transactions['type'] == 'expense'].groupby(
                    transactions['date'].dt.to_period('M')
                )['amount'].sum().mean()

                if pd.isna(avg_monthly_spending):
                    avg_monthly_spending = 0

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
                elif current_spending > 0:
                    st.markdown("""
                    <div class="insight-card">
                        <strong>Monthly Comparison:</strong><br>
                        No spending data available for last month
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Failed to generate predictive insights: {e}")
    except Exception as e:
        st.error(f"Failed to load advanced analytics: {e}")
