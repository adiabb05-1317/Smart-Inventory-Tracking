import psycopg2
from psycopg2 import pool
from typing import Any, Optional, List, Tuple
import os


class DBManager:
    """Database manager with connection pooling for PostgreSQL."""
    
    def __init__(self, min_conn: Optional[int] = None, max_conn: Optional[int] = None):
        self.connection_pool: Optional[pool.ThreadedConnectionPool] = None
        self.min_conn = min_conn or int(os.getenv("DB_MIN_CONNECTIONS", "2"))
        self.max_conn = max_conn or int(os.getenv("DB_MAX_CONNECTIONS", "10"))
    
    def initialize_pool(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None
    ) -> None:
        """
        Initialize the connection pool.
        Parameters default to environment variables if not provided.
        """
        db_host = host or os.getenv("DB_HOST", "localhost")
        db_port = port or int(os.getenv("DB_PORT", "5432"))
        db_name = database or os.getenv("DB_NAME", "inventory_db")
        db_user = user or os.getenv("DB_USER", "kubo_user")
        db_password = password or os.getenv("DB_PASSWORD", "password")
        
        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                self.min_conn,
                self.max_conn,
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password
            )
            print(f"Connection pool created successfully (host={db_host}, database={db_name})")
        except (Exception, psycopg2.Error) as error:
            print(f"Error while connecting to PostgreSQL: {error}")
            raise
    
    def get_connection(self):
        """Get a connection from the pool."""
        if self.connection_pool:
            return self.connection_pool.getconn()
        raise Exception("Connection pool is not initialized")
    
    def return_connection(self, connection) -> None:
        """Return a connection back to the pool."""
        if self.connection_pool:
            self.connection_pool.putconn(connection)
    
    def execute_query(
        self,
        query: str,
        params: Optional[Tuple] = None,
        fetch: bool = False
    ) -> Optional[Any]:
        """
        Execute a query and optionally fetch results.
        Returns lastrowid for INSERT operations when fetch=False.
        """
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
                connection.commit()
                return result
            else:
                connection.commit()
                # Return the last inserted id for INSERT operations
                if query.strip().upper().startswith('INSERT'):
                    return cursor.lastrowid if cursor.lastrowid else None
                return None
        except (Exception, psycopg2.Error) as error:
            if connection:
                connection.rollback()
            print(f"Error executing query: {error}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.return_connection(connection)
    
    def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Tuple]:
        """Execute a query and fetch one result."""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result
        except (Exception, psycopg2.Error) as error:
            print(f"Error fetching one: {error}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.return_connection(connection)
    
    def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[Tuple]:
        """Execute a query and fetch all results."""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            return results
        except (Exception, psycopg2.Error) as error:
            print(f"Error fetching all: {error}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.return_connection(connection)
    
    def close_pool(self) -> None:
        """Close all connections in the pool."""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("Connection pool closed successfully")

