import sqlite3
import pandas as pd
from datetime import datetime
from config import DB_PATH
from classifier import ExpenseClassifier
import bcrypt

class FinanceDatabase:
    def __init__(self):
        try:
            self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.create_tables()
        except sqlite3.Error as e:
            raise ConnectionError(f"Failed to connect to database: {e}")

    def _create_tables(self):
        """Create necessary database tables."""
        try:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    category TEXT NOT NULL,
                    date DATE NOT NULL,
                    type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    receipt_image TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')

            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    month TEXT NOT NULL,
                    alerts_enabled BOOLEAN DEFAULT 1,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')

            self.conn.commit()

            # Seed demo user if no users exist
            cursor = self.conn.execute('SELECT COUNT(*) FROM users')
            if cursor.fetchone()[0] == 0:
                hashed = bcrypt.hashpw('password'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                self.conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', ('demo', hashed))
                self.conn.commit()
                # Load sample data for demo user
                cursor = self.conn.execute('SELECT id FROM users WHERE username = ?', ('demo',))
                demo_user_id = cursor.fetchone()[0]
                from config import SAMPLE_DATA
                for desc, amount, date, type_val, category in SAMPLE_DATA:
                    self.add_transaction(demo_user_id, desc, amount, date, type_val, category)
                self.conn.commit()

        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to create tables: {e}")

    def create_tables(self):
        """Create necessary database tables if they don't exist, handling schema migration."""
        try:
            # Check if transactions table exists with old schema (without user_id)
            cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
            if cursor.fetchone():
                cursor = self.conn.execute("PRAGMA table_info(transactions)")
                columns = [row[1] for row in cursor.fetchall()]
                if 'user_id' not in columns:
                    # Old schema detected, reset database
                    self.reset_database()
                    return

            # Create tables with new schema
            self._create_tables()

        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to create tables: {e}")

    def reset_database(self):
        """Reset the database by dropping all tables and recreating them with the new schema."""
        try:
            self.conn.execute("DROP TABLE IF EXISTS budgets")
            self.conn.execute("DROP TABLE IF EXISTS transactions")
            self.conn.execute("DROP TABLE IF EXISTS users")
            self.conn.commit()
            self._create_tables()
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to reset database: {e}")

    def add_transaction(self, user_id, description, amount, date, type, category=None, receipt_image=None):
        """Add a new transaction to the database."""
        # Input validation
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("user_id must be a positive integer")

        if not description or not isinstance(description, str):
            raise ValueError("Description must be a non-empty string")

        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Amount must be a positive number")

        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")

        if type not in ['income', 'expense']:
            raise ValueError("Type must be 'income' or 'expense'")

        if category and not isinstance(category, str):
            raise ValueError("Category must be a string")

        classifier = ExpenseClassifier()
        if not category:
            try:
                category = classifier.categorize(description, amount)
            except ValueError as e:
                raise ValueError(f"Failed to categorize transaction: {e}")

        try:
            self.conn.execute('''
                INSERT INTO transactions (user_id, description, amount, category, date, type, receipt_image)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, description, amount, category, date, type, receipt_image))
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to add transaction: {e}")

    def get_transactions(self, user_id, start_date=None, end_date=None, category=None, type=None):
        """Retrieve transactions with optional filters."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("user_id must be a positive integer")

        # Validate dates if provided
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise ValueError("Start date must be in YYYY-MM-DD format")

        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise ValueError("End date must be in YYYY-MM-DD format")

        if category and not isinstance(category, str):
            raise ValueError("Category must be a string")

        if type and type not in ['income', 'expense']:
            raise ValueError("Type must be 'income' or 'expense'")

        query = "SELECT * FROM transactions WHERE user_id = ?"
        params = [user_id]

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

        try:
            return pd.read_sql_query(query, self.conn, params=params)
        except (sqlite3.Error, pd.errors.DatabaseError) as e:
            raise RuntimeError(f"Failed to retrieve transactions: {e}")

    def get_spending_insights(self, user_id, start_date=None, end_date=None):
        """Calculate spending insights for a given period."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("user_id must be a positive integer")

        # Get current month if no dates provided
        if not start_date or not end_date:
            today = datetime.now()
            start_date = today.replace(day=1).strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')

        try:
            df = self.get_transactions(user_id, start_date, end_date, type='expense')
        except Exception as e:
            raise RuntimeError(f"Failed to get spending insights: {e}")

        if df.empty:
            return {
                'total_spending': 0,
                'category_breakdown': pd.DataFrame(),
                'monthly_trend': pd.DataFrame()
            }

        try:
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
        except Exception as e:
            raise RuntimeError(f"Failed to calculate spending insights: {e}")
    def create_user(self, username, password_hash):
        """Create a new user."""
        if not username or not isinstance(username, str):
            raise ValueError("Username must be a non-empty string")
        if not password_hash or not isinstance(password_hash, str):
            raise ValueError("Password hash must be a non-empty string")

        try:
            self.conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
            self.conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError("Username already exists")
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to create user: {e}")

    def get_user_by_username(self, username):
        """Get user by username."""
        if not username or not isinstance(username, str):
            raise ValueError("Username must be a non-empty string")

        try:
            cursor = self.conn.execute('SELECT id, username, password_hash, created_at FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'username': row[1],
                    'password_hash': row[2],
                    'created_at': row[3]
                }
            return None
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to get user: {e}")
