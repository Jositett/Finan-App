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

    def manage_transactions_ui(self):
        """Comprehensive UI for managing transactions with full CRUD operations."""
        st.header("📊 Manage Transactions")

        # Initialize session state for transaction management
        if "selected_transaction" not in st.session_state:
            st.session_state.selected_transaction = None
        if "edit_mode" not in st.session_state:
            st.session_state.edit_mode = False
        if "delete_confirm" not in st.session_state:
            st.session_state.delete_confirm = False

        # Get all transactions
        try:
            transactions_df = self.db.get_transactions(self.user_id)
        except Exception as e:
            st.error(f"Failed to load transactions: {e}")
            return

        # Create/Edit/Delete Forms Section
        st.subheader("Transaction Operations")

        # Tabs for different operations
        tab1, tab2, tab3 = st.tabs(["➕ Add Transaction", "✏️ Edit Transaction", "🗑️ Delete Transaction"])

        with tab1:
            self._add_transaction_form()

        with tab2:
            self._edit_transaction_form(transactions_df)

        with tab3:
            self._delete_transaction_form(transactions_df)

        # Transactions Table Section
        st.subheader("📋 All Transactions")

        if transactions_df.empty:
            st.info("No transactions found. Add your first transaction above!")
            return

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_category = st.selectbox(
                "Filter by Category",
                ["All"] + sorted(transactions_df['category'].unique().tolist()),
                key="table_category_filter"
            )
        with col2:
            filter_type = st.selectbox(
                "Filter by Type",
                ["All", "income", "expense"],
                key="table_type_filter"
            )
        with col3:
            # Date range filter
            min_date = pd.to_datetime(transactions_df['date']).min().date()
            max_date = pd.to_datetime(transactions_df['date']).max().date()
            date_range = st.date_input(
                "Date Range",
                value=(min_date, max_date),
                key="table_date_filter"
            )

        # Apply filters
        filtered_df = transactions_df.copy()
        if filter_category != "All":
            filtered_df = filtered_df[filtered_df['category'] == filter_category]
        if filter_type != "All":
            filtered_df = filtered_df[filtered_df['type'] == filter_type]
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df['date'] = pd.to_datetime(filtered_df['date'])
            filtered_df = filtered_df[
                (filtered_df['date'].dt.date >= start_date) &
                (filtered_df['date'].dt.date <= end_date)
            ]

        if filtered_df.empty:
            st.info("No transactions match the current filters.")
            return

        # Display statistics
        total_amount = filtered_df['amount'].sum()
        income_total = filtered_df[filtered_df['type'] == 'income']['amount'].sum()
        expense_total = filtered_df[filtered_df['type'] == 'expense']['amount'].sum()
        net_amount = income_total - expense_total

        stat_cols = st.columns(4)
        with stat_cols[0]:
            st.metric("Total Transactions", len(filtered_df))
        with stat_cols[1]:
            st.metric("Total Amount", f"${total_amount:.2f}")
        with stat_cols[2]:
            st.metric("Income", f"${income_total:.2f}", delta=f"+${income_total:.2f}")
        with stat_cols[3]:
            st.metric("Expenses", f"${expense_total:.2f}", delta=f"-${expense_total:.2f}")

        st.metric("Net Flow", f"${net_amount:.2f}", delta=f"${net_amount:.2f}")

        # Prepare display dataframe
        display_df = filtered_df.copy()
        display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d')
        display_df['amount'] = display_df.apply(
            lambda row: f"${row['amount']:.2f}" +
                       (" 🟢" if row['type'] == 'income' else " 🔴"), axis=1
        )
        display_df = display_df[['date', 'description', 'amount', 'category', 'type']]

        # Display data with selection
        event = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        # Handle row selection
        if len(event.selection.rows) > 0:
            selected_idx = event.selection.rows[0]
            selected_transaction = filtered_df.iloc[selected_idx]
            st.session_state.selected_transaction = selected_transaction['id']

            # Show selected transaction details
            st.info(f"Selected transaction: **{selected_transaction['description']}** - ${selected_transaction['amount']:.2f}")

            # Action buttons for selected transaction
            action_col1, action_col2, action_col3 = st.columns(3)
            with action_col1:
                if st.button("✏️ Quick Edit", use_container_width=True):
                    st.session_state.edit_mode = True
                    st.rerun()
            with action_col2:
                if st.button("🗑️ Quick Delete", use_container_width=True):
                    st.session_state.delete_confirm = True
                    st.rerun()
            with action_col3:
                if st.button("📄 View Details", use_container_width=True):
                    self._show_transaction_details(selected_transaction)

            # Render edit and delete forms directly below the action buttons
            # Get the transaction data from the full (unfiltered) dataset to ensure consistency
            selected_transaction_data = transactions_df[transactions_df['id'] == st.session_state.selected_transaction]

            if st.session_state.edit_mode and not selected_transaction_data.empty:
                st.markdown("---")  # Visual separator
                self._inline_edit_transaction_form(selected_transaction_data.iloc[0])

            if st.session_state.delete_confirm and not selected_transaction_data.empty:
                st.markdown("---")  # Visual separator
                self._inline_delete_transaction_form(selected_transaction_data.iloc[0])

        else:
            st.session_state.selected_transaction = None

    def _add_transaction_form(self):
        """Form for adding new transactions."""
        with st.form("add_transaction_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                description = st.text_input("Description", placeholder="e.g., Grocery shopping at Walmart")
                amount = st.number_input("Amount", min_value=0.0, step=0.01, format="%.2f")
                trans_type = st.selectbox("Type", ["expense", "income"], key="add_type")

            with col2:
                date = st.date_input("Date", value=datetime.now(), key="add_date")
                category_options = list(CATEGORIES.keys()) + ['general', 'miscellaneous']
                category = st.selectbox("Category", category_options, key="add_category")
                receipt = st.file_uploader("Receipt (optional)", type=['png', 'jpg', 'jpeg'], key="add_receipt")

            submitted = st.form_submit_button("✅ Add Transaction")

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

    def _edit_transaction_form(self, transactions_df):
        """Form for editing selected transactions in tabs (only when no inline selection)."""
        # Only show tab form if no transaction is selected for inline editing
        if (st.session_state.edit_mode or st.session_state.selected_transaction) and not st.session_state.selected_transaction:
            if st.session_state.selected_transaction:
                try:
                    # Get transaction details
                    transaction = transactions_df[transactions_df['id'] == st.session_state.selected_transaction].iloc[0]

                    st.write("Editing transaction:", f"**{transaction['description']}**")

                    with st.form("edit_transaction_form"):
                        col1, col2 = st.columns(2)

                        with col1:
                            description = st.text_input(
                                "Description",
                                value=transaction['description'],
                                key="edit_description"
                            )
                            amount = st.number_input(
                                "Amount",
                                value=float(transaction['amount']),
                                min_value=0.0,
                                step=0.01,
                                format="%.2f",
                                key="edit_amount"
                            )
                            trans_type = st.selectbox(
                                "Type",
                                ["expense", "income"],
                                index=0 if transaction['type'] == 'expense' else 1,
                                key="edit_type"
                            )

                        with col2:
                            date = st.date_input(
                                "Date",
                                value=pd.to_datetime(transaction['date']),
                                key="edit_date"
                            )
                            category_options = list(CATEGORIES.keys()) + ['general', 'miscellaneous']
                            category_index = category_options.index(transaction['category']) if transaction['category'] in category_options else 0
                            category = st.selectbox(
                                "Category",
                                category_options,
                                index=category_index,
                                key="edit_category"
                            )
                            receipt = st.file_uploader(
                                "Update Receipt (optional)",
                                type=['png', 'jpg', 'jpeg'],
                                key="edit_receipt"
                            )

                        col1, col2 = st.columns(2)
                        with col1:
                            update_submitted = st.form_submit_button("💾 Update Transaction")
                        with col2:
                            cancel_edit = st.form_submit_button("❌ Cancel")

                        if update_submitted:
                            try:
                                # Validation
                                if not description.strip():
                                    st.error("Description is required")
                                    return

                                if amount <= 0:
                                    st.error("Amount must be greater than 0")
                                    return

                                date_str = date.strftime('%Y-%m-%d')

                                receipt_data = transaction['receipt_image']
                                if receipt:
                                    # Validate file size (max 5MB)
                                    if receipt.size > 5 * 1024 * 1024:
                                        st.error("Receipt file size must be less than 5MB")
                                        return
                                    receipt_data = base64.b64encode(receipt.read()).decode()

                                # Update transaction
                                self.db.update_transaction(
                                    user_id=self.user_id,
                                    transaction_id=int(transaction['id']),
                                    description=description.strip(),
                                    amount=amount,
                                    date=date_str,
                                    type=trans_type,
                                    category=category,
                                    receipt_image=receipt_data
                                )
                                st.success("✅ Transaction updated successfully!")

                                # Reset edit mode
                                st.session_state.edit_mode = False
                                st.session_state.selected_transaction = None
                                st.rerun()

                            except ValueError as e:
                                st.error(f"Invalid input: {e}")
                            except Exception as e:
                                st.error(f"Failed to update transaction: {e}")

                        if cancel_edit:
                            st.session_state.edit_mode = False
                            st.session_state.selected_transaction = None
                            st.rerun()

                except IndexError:
                    st.error("Transaction not found. It may have been deleted.")
                    st.session_state.selected_transaction = None
                    st.session_state.edit_mode = False
                except Exception as e:
                    st.error(f"Error loading transaction details: {e}")
                    st.session_state.selected_transaction = None
                    st.session_state.edit_mode = False
            else:
                st.info("Select a transaction from the table below to edit it.")
        else:
            st.info("Select a transaction from the table below or use the '✏️ Quick Edit' button.")

    def _inline_edit_transaction_form(self, transaction):
        """Inline form for editing selected transactions directly below action buttons."""
        try:
            # Transaction is already passed as a single row (Series or dict)
            st.markdown("**Editing Transaction**")
            st.caption(f"Original: {transaction['description']} - ${transaction['amount']:.2f}")

            with st.form("inline_edit_transaction_form"):
                col1, col2 = st.columns(2)

                with col1:
                    description = st.text_input(
                        "Description",
                        value=transaction['description'],
                        key="inline_edit_description"
                    )
                    amount = st.number_input(
                        "Amount",
                        value=float(transaction['amount']),
                        min_value=0.0,
                        step=0.01,
                        format="%.2f",
                        key="inline_edit_amount"
                    )
                    trans_type = st.selectbox(
                        "Type",
                        ["expense", "income"],
                        index=0 if transaction['type'] == 'expense' else 1,
                        key="inline_edit_type"
                    )

                with col2:
                    date = st.date_input(
                        "Date",
                        value=pd.to_datetime(transaction['date']),
                        key="inline_edit_date"
                    )
                    category_options = list(CATEGORIES.keys()) + ['general', 'miscellaneous']
                    category_index = category_options.index(transaction['category']) if transaction['category'] in category_options else 0
                    category = st.selectbox(
                        "Category",
                        category_options,
                        index=category_index,
                        key="inline_edit_category"
                    )
                    receipt = st.file_uploader(
                        "Update Receipt (optional)",
                        type=['png', 'jpg', 'jpeg'],
                        key="inline_edit_receipt"
                    )

                col1, col2 = st.columns(2)
                with col1:
                    update_submitted = st.form_submit_button("💾 Update Transaction")
                with col2:
                    cancel_edit = st.form_submit_button("❌ Cancel")

                if update_submitted:
                    try:
                        # Validation
                        if not description.strip():
                            st.error("Description is required")
                            return

                        if amount <= 0:
                            st.error("Amount must be greater than 0")
                            return

                        date_str = date.strftime('%Y-%m-%d')

                        receipt_data = transaction['receipt_image']
                        if receipt:
                            # Validate file size (max 5MB)
                            if receipt.size > 5 * 1024 * 1024:
                                st.error("Receipt file size must be less than 5MB")
                                return
                            receipt_data = base64.b64encode(receipt.read()).decode()

                        # Update transaction
                        self.db.update_transaction(
                            user_id=self.user_id,
                            transaction_id=int(transaction['id']),
                            description=description.strip(),
                            amount=amount,
                            date=date_str,
                            type=trans_type,
                            category=category,
                            receipt_image=receipt_data
                        )
                        st.success("✅ Transaction updated successfully!")

                        # Reset edit mode
                        st.session_state.edit_mode = False
                        st.session_state.selected_transaction = None
                        st.rerun()

                    except ValueError as e:
                        st.error(f"Invalid input: {e}")
                    except Exception as e:
                        st.error(f"Failed to update transaction: {e}")

                if cancel_edit:
                    st.session_state.edit_mode = False
                    st.session_state.selected_transaction = None
                    st.rerun()

        except IndexError:
            st.error("Transaction not found. It may have been deleted.")
            st.session_state.selected_transaction = None
            st.session_state.edit_mode = False
        except Exception as e:
            st.error(f"Error loading transaction details: {e}")
            st.session_state.selected_transaction = None
            st.session_state.edit_mode = False

    def _inline_delete_transaction_form(self, transaction):
        """Inline form for deleting selected transactions directly below action buttons."""
        try:
            # Transaction is already passed as a single row (Series or dict)
            st.markdown("**Delete Transaction**")
            st.caption(f"Transaction: {transaction['description']} - ${transaction['amount']:.2f}")

            st.warning("Are you sure you want to delete this transaction?")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Yes, Delete Transaction", use_container_width=True, type="primary"):
                    try:
                        self.db.delete_transaction(self.user_id, int(transaction['id']))
                        st.success("✅ Transaction deleted successfully!")

                        # Reset delete confirmation
                        st.session_state.delete_confirm = False
                        st.session_state.selected_transaction = None
                        st.rerun()

                    except Exception as e:
                        st.error(f"Failed to delete transaction: {e}")

            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.delete_confirm = False
                    st.session_state.selected_transaction = None
                    st.rerun()

        except IndexError:
            st.error("Transaction not found. It may have already been deleted.")
            st.session_state.selected_transaction = None
            st.session_state.delete_confirm = False
        except Exception as e:
            st.error(f"Error loading transaction details: {e}")
            st.session_state.selected_transaction = None
            st.session_state.delete_confirm = False

    def _delete_transaction_form(self, transactions_df):
        """Form for deleting selected transactions in tabs (only when no inline selection)."""
        # Only show tab form if no transaction is selected for inline deleting
        if (st.session_state.delete_confirm or st.session_state.selected_transaction) and not st.session_state.selected_transaction:
            if st.session_state.selected_transaction:
                try:
                    transaction = transactions_df[transactions_df['id'] == st.session_state.selected_transaction].iloc[0]

                    st.warning(f"Are you sure you want to delete this transaction?")
                    st.write("**Description:**", transaction['description'])
                    st.write("**Amount:**", f"${transaction['amount']:.2f}")
                    st.write("**Date:**", transaction['date'])
                    st.write("**Type:**", transaction['type'])
                    st.write("**Category:**", transaction['category'])

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🗑️ Yes, Delete Transaction", use_container_width=True, type="primary"):
                            try:
                                self.db.delete_transaction(self.user_id, int(transaction['id']))
                                st.success("✅ Transaction deleted successfully!")

                                # Reset delete confirmation
                                st.session_state.delete_confirm = False
                                st.session_state.selected_transaction = None
                                st.rerun()

                            except Exception as e:
                                st.error(f"Failed to delete transaction: {e}")

                    with col2:
                        if st.button("❌ Cancel", use_container_width=True):
                            st.session_state.delete_confirm = False
                            st.session_state.selected_transaction = None
                            st.rerun()

                except IndexError:
                    st.error("Transaction not found. It may have already been deleted.")
                    st.session_state.selected_transaction = None
                    st.session_state.delete_confirm = False
                except Exception as e:
                    st.error(f"Error loading transaction details: {e}")
                    st.session_state.selected_transaction = None
                    st.session_state.delete_confirm = False
            else:
                st.info("Select a transaction from the table below to delete it.")
        else:
            st.info("Select a transaction from the table below or use the '🗑️ Quick Delete' button.")

    def _show_transaction_details(self, transaction):
        """Show detailed view of a transaction."""
        with st.expander("Transaction Details", expanded=True):
            det_col1, det_col2 = st.columns(2)

            with det_col1:
                st.write("**ID:**", transaction['id'])
                st.write("**Description:**", transaction['description'])
                st.write("**Amount:**", f"${transaction['amount']:.2f}")
                st.write("**Type:**", transaction['type'].title())

            with det_col2:
                st.write("**Date:**", transaction['date'])
                st.write("**Category:**", transaction['category'].title())
                st.write("**Created:**", transaction['created_at'])

            if transaction['receipt_image']:
                st.subheader("📄 Receipt")
                try:
                    receipt_data = base64.b64decode(transaction['receipt_image'])
                    st.image(receipt_data, caption="Transaction Receipt", use_column_width=True)
                except Exception as e:
                    st.error("Could not display receipt image.")

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
