import streamlit as st
from config import PAGE_CONFIG, CUSTOM_CSS

# Page configuration
st.set_page_config(**PAGE_CONFIG)

# Custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def main():
    """Main application function with authentication and modular components."""
    try:
        from auth import check_auth, login_page, show_auth_status

        if not check_auth():
            login_page()
            return

        from database import FinanceDatabase
        from analytics import Analytics
        from ui import FinanceUI

        db = FinanceDatabase()
        user_id = st.session_state.user_id
        analytics = Analytics(db, user_id)
        ui = FinanceUI(db, analytics, user_id)

        # Sidebar navigation
        show_auth_status()
        st.sidebar.title("Navigation")
        page = st.sidebar.radio(
            "Choose a page",
            ["Dashboard", "Add Transaction", "Bulk Actions", "Advanced Analytics"]
        )
        st.sidebar.markdown("---")

        # Sample data initialization
        if st.sidebar.button("Load Sample Data"):
            load_sample_data(db, user_id)
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
            ui.display_dashboard()
        elif page == "Add Transaction":
            ui.add_transaction_ui()
        elif page == "Bulk Actions":
            ui.bulk_actions_ui()
        elif page == "Advanced Analytics":
            from analytics import show_advanced_analytics
            show_advanced_analytics(db, user_id)

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.error("Please refresh the page or contact support if the problem persists.")

def load_sample_data(db, user_id):
    """Load sample transactions for demonstration."""
    from config import SAMPLE_DATA

    try:
        for desc, amount, date, type_val, category in SAMPLE_DATA:
            db.add_transaction(user_id, desc, amount, date, type_val, category)
    except Exception as e:
        st.error(f"Failed to load sample data: {e}")

if __name__ == "__main__":
    main()
