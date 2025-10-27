import psycopg2
from psycopg2 import pool
from typing import Any, Optional, List, Tuple


class DBManager:
    """Database manager with connection pooling for PostgreSQL."""
    
    def __init__(self, min_conn: int = 1, max_conn: int = 10):
        self.connection_pool: Optional[pool.SimpleConnectionPool] = None
        self.min_conn = min_conn
        self.max_conn = max_conn
    
    def initialize_pool(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "inventory_db",
        user: str = "kubo_user",
        password: str = "password"
    ) -> None:
        """Initialize the connection pool."""
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                self.min_conn,
                self.max_conn,
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            print(f"Connection pool created successfully")
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

