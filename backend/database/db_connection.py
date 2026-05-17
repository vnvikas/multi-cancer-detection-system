import pymysql
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    """Database connection handler"""
    
    def __init__(self):
        self.host = os.environ.get('DB_HOST', 'localhost')
        self.user = os.environ.get('DB_USER', 'root')
        self.password = os.environ.get('DB_PASSWORD', '')
        self.database = os.environ.get('DB_NAME', 'multi_cancer_db')
        self.port = int(os.environ.get('DB_PORT', 3306))
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                cursorclass=pymysql.cursors.DictCursor
            )
            return self.connection
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    @contextmanager
    def get_cursor(self):
        """Get database cursor with context management"""
        conn = self.connect()
        if conn:
            cursor = conn.cursor()
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
                self.disconnect()
        else:
            raise Exception("Database connection failed")
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            return cursor.lastrowid
    
    def execute_many(self, query, params_list):
        """Execute multiple queries"""
        with self.get_cursor() as cursor:
            return cursor.executemany(query, params_list)
    
    def test_connection(self):
        """Test database connection"""
        try:
            result = self.execute_query("SELECT 1")
            return result is not None
        except:
            return False

# Singleton instance
db_connection = DatabaseConnection()

def get_db():
    """Get database connection instance"""
    return db_connection