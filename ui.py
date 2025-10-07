import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import base64
import io
from config import CATEGORIES
from database import FinanceDatabase
from analytics import Analytics
from classifier import ExpenseClassifier

class FinanceUI:
    def __init__(self, db: FinanceDatabase, analytics: Analytics, user_id: int):
        self.db = db
        self.analytics = analytics
        self.user_id = user_id
        self.classifier = ExpenseClassifier()

    def add_transaction_ui(self):
        """UI for adding new transactions with improved validation."""
        st.header("➕ Add New Transaction")

        with st.form("transaction_form"):
            col1, col2 = st.columns(2)

            with col1:
                description = st.text_input("Description", placeholder="e.g., Grocery shopping at Walmart")
                amount = st.number_input("Amount", min_value=0.0, step=0.01, format="%.2f")
                trans_type = st.selectbox("Type", ["expense", "income"])

            with col2:
                date = st.date_input("Date", value=datetime.now())
                category_options = list(CATEGORIES.keys()) + ['general', 'miscellaneous']
                category = st.selectbox("Category", category_options)
                receipt = st.file_uploader("Receipt (optional)", type=['png', 'jpg', 'jpeg'])

            submitted = st.form_submit_button("Add Transaction")

            if submitted:
                try:
                    # Validation
                    if not description.strip():
                        st.error("Description is required")
                        return

                    if amount <= 0:
                        st.error("Amount must be greater than 0")
                        return

                    date_str = date.strftime('%Y-%m-%d')

                    receipt_data = None
                    if receipt:
                        # Validate file size (max 5MB)
                        if receipt.size > 5 * 1024 * 1024:
                            st.error("Receipt file size must be less than 5MB")
                            return
                        receipt_data = base64.b64encode(receipt.read()).decode()

                    # Add transaction
                    self.db.add_transaction(
                        user_id=self.user_id,
                        description=description.strip(),
                        amount=amount,
                        date=date_str,
                        type=trans_type,
                        category=category,
                        receipt_image=receipt_data
                    )
                    st.success("✅ Transaction added successfully!")
                    st.rerun()
                except ValueError as e:
                    st.error(f"Invalid input: {e}")
                except Exception as e:
                    st.error(f"Failed to add transaction: {e}")

    def display_dashboard(self):
        """Display the main dashboard with improved error handling."""
        st.markdown('<h1 class="main-header">💰 Smart Finance Tracker</h1>', unsafe_allow_html=True)

        # Date filters
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            start_date = st.date_input("Start Date",
                value=(datetime.now() - timedelta(days=365)).replace(day=1))
        with col2:
            end_date = st.date_input("End Date",
                value=datetime.now())

        # Validate date range
        if start_date > end_date:
            st.error("Start date cannot be after end date")
            return

        # Get insights
        insights = self.analytics.get_spending_insights(
            self.user_id,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

        # Key metrics with error handling
        st.subheader("📊 Financial Overview")
        metric_cols = st.columns(4)

        try:
            total_spent = insights['total_spending']

            with metric_cols[0]:
                st.metric("Total Spent", f"${total_spent:,.2f}")

            with metric_cols[1]:
                total_income_df = self.db.get_transactions(
                    self.user_id,
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
                days = (end_date - start_date).days + 1
                avg_daily = total_spent / days if total_spent > 0 and days > 0 else 0
                st.metric("Avg Daily Spend", f"${avg_daily:.2f}")
        except Exception as e:
            st.error(f"Failed to calculate metrics: {e}")

        # Charts row
        st.subheader("📈 Spending Analytics")
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            fig = self.analytics.generate_monthly_trend_chart(insights)
            if fig:
                st.plotly_chart(fig, width='stretch')

        with chart_col2:
            fig = self.analytics.generate_category_pie_chart(insights)
            if fig:
                st.plotly_chart(fig, width='stretch')

        # AI Insights and Recent Transactions
        st.subheader("🤖 AI Insights & Recent Activity")
        insight_col, transaction_col = st.columns([1, 2])

        with insight_col:
            self.analytics.display_ai_insights(insights)

        with transaction_col:
            self.display_recent_transactions()

    def display_recent_transactions(self):
        """Display recent transactions with filters."""
        st.markdown("### 📋 Recent Transactions")

        try:
            # Filters
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                filter_category_options = ["All"] + list(CATEGORIES.keys()) + ['general', 'miscellaneous']
                filter_category = st.selectbox("Filter Category", filter_category_options)
            with filter_col2:
                filter_type = st.selectbox("Filter Type", ["All", "expense", "income"])

            # Get filtered transactions
            filters = {}
            if filter_category != "All":
                filters['category'] = filter_category
            if filter_type != "All":
                filters['type'] = filter_type

            transactions = self.db.get_transactions(self.user_id, **filters)

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
        except Exception as e:
            st.error(f"Failed to display recent transactions: {e}")

    def bulk_actions_ui(self):
        """UI for bulk import/export transactions."""
        st.header("🔄 Bulk Actions")

        tab1, tab2 = st.tabs(["Import Transactions", "Export Transactions"])

        with tab1:
            self.bulk_import_ui()

        with tab2:
            self.bulk_export_ui()

    def bulk_import_ui(self):
        """UI for bulk importing transactions."""
        st.subheader("📥 Import Transactions")

        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])

        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.write("Preview of uploaded data:")
                st.dataframe(df.head())

                if st.button("Import Transactions"):
                    # Validate CSV columns
                    required_columns = ['description', 'amount', 'date', 'type']
                    if not all(col in df.columns for col in required_columns):
                        st.error(f"CSV must contain columns: {', '.join(required_columns)}")
                        return

                    imported_count = 0
                    errors = []

                    for index, row in df.iterrows():
                        try:
                            # Validate each row
                            desc = str(row['description']).strip()
                            if not desc:
                                errors.append(f"Row {index+1}: Description is empty")
                                continue

                            amount = float(row['amount'])
                            if amount <= 0:
                                errors.append(f"Row {index+1}: Amount must be positive")
                                continue

                            date_str = str(row['date'])
                            datetime.strptime(date_str, '%Y-%m-%d')  # Validate date format

                            trans_type = str(row['type']).lower()
                            if trans_type not in ['income', 'expense']:
                                errors.append(f"Row {index+1}: Type must be 'income' or 'expense'")
                                continue

                            # Add transaction
                            self.db.add_transaction(
                                user_id=self.user_id,
                                description=desc,
                                amount=amount,
                                date=date_str,
                                type=trans_type
                            )
                            imported_count += 1

                        except Exception as e:
                            errors.append(f"Row {index+1}: {str(e)}")
                            continue

                    if imported_count > 0:
                        st.success(f"✅ Successfully imported {imported_count} transactions!")

                    if errors:
                        st.warning("Some rows had errors:")
                        for error in errors[:5]:  # Show first 5 errors
                            st.write(f"- {error}")
                        if len(errors) > 5:
                            st.write(f"... and {len(errors) - 5} more errors")

            except Exception as e:
                st.error(f"Error reading CSV file: {e}")

    def bulk_export_ui(self):
        """UI for bulk exporting transactions."""
        st.subheader("📤 Export Transactions")

        # Date range for export
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=(datetime.now() - timedelta(days=365)).replace(day=1))
        with col2:
            end_date = st.date_input("End Date", value=datetime.now())

        # Export format options
        export_type = st.selectbox("Export format", ["CSV", "JSON"])

        if st.button("Export Transactions"):
            try:
                transactions = self.db.get_transactions(
                    self.user_id,
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d')
                )

                if transactions.empty:
                    st.info("No transactions found in the selected date range")
                    return

                if export_type == "CSV":
                    csv_data = transactions[['description', 'amount', 'date', 'type', 'category']].to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=f"transactions_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                    st.success(f"✅ Prepared {len(transactions)} transactions for CSV export")
                else:  # JSON
                    json_data = transactions[['description', 'amount', 'date', 'type', 'category']].to_json(orient='records')
                    st.download_button(
                        label="Download JSON",
                        data=json_data,
                        file_name=f"transactions_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.json",
                        mime="application/json"
                    )
                    st.success(f"✅ Prepared {len(transactions)} transactions for JSON export")

            except Exception as e:
                st.error(f"Failed to export transactions: {e}")
