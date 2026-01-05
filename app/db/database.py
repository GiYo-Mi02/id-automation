"""
Database Connection Manager
===========================
Production-ready database layer with connection pooling and proper resource management.

Security & Performance Fixes Applied:
- [P0] Connection pooling (eliminates 50-100ms overhead per request)
- [P0] Context manager ensures connections are ALWAYS closed (fixes leaks)
- [P0] Removed hardcoded credentials (uses environment variables)
- [P1] Structured error handling with proper exceptions
- [P1] Transaction support with automatic rollback on error
"""

import logging
from typing import Optional, Generator, Any, Dict, List
from contextlib import contextmanager
from datetime import datetime

import mysql.connector
from mysql.connector import Error as MySQLError
from mysql.connector.pooling import MySQLConnectionPool, PooledMySQLConnection

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# =============================================================================
# EXCEPTIONS
# =============================================================================

class DatabaseError(Exception):
    """Base exception for database operations."""
    pass


class ConnectionError(DatabaseError):
    """Failed to establish database connection."""
    pass


class QueryError(DatabaseError):
    """Failed to execute database query."""
    pass


class NotFoundError(DatabaseError):
    """Requested record not found."""
    pass


# =============================================================================
# CONNECTION POOL MANAGER
# =============================================================================

class DatabaseManager:
    """
    Singleton Database Manager with connection pooling.
    
    Features:
    - Connection pooling (configurable pool size)
    - Context manager for automatic cleanup
    - Transaction support with auto-rollback
    - Health check endpoint support
    
    Usage:
        from app.db.database import db_manager
        
        # Simple query
        with db_manager.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM students WHERE id_number = %s", (student_id,))
            result = cursor.fetchone()
        
        # With transaction
        with db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE students SET ...", (...))
            cursor.execute("INSERT INTO history ...", (...))
            # Auto-commits on success, auto-rollback on exception
    """
    
    _instance: Optional["DatabaseManager"] = None
    _pool: Optional[MySQLConnectionPool] = None
    
    def __new__(cls) -> "DatabaseManager":
        """Singleton pattern - only one pool instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize connection pool on first instantiation."""
        if self._pool is None:
            self._initialize_pool()
    
    def _initialize_pool(self) -> None:
        """Create the connection pool."""
        settings = get_settings()
        db_config = settings.database
        
        try:
            self._pool = MySQLConnectionPool(
                pool_name=db_config.pool_name,
                pool_size=db_config.pool_size,
                pool_reset_session=True,
                **db_config.connection_config
            )
            logger.info(
                f"Database pool initialized: {db_config.host}:{db_config.port}/{db_config.database} "
                f"(pool_size={db_config.pool_size})"
            )
        except MySQLError as e:
            # If database doesn't exist, try to create it
            if e.errno == 1049:  # Unknown database
                logger.warning(f"Database '{db_config.database}' not found, attempting to create...")
                self._create_database()
                self._initialize_pool()
            else:
                logger.error(f"Failed to initialize database pool: {e}")
                raise ConnectionError(f"Database connection failed: {e}") from e
    
    def _create_database(self) -> None:
        """Create database if it doesn't exist."""
        settings = get_settings()
        db_config = settings.database
        
        # Connect without specifying database
        config_no_db = db_config.connection_config.copy()
        del config_no_db["database"]
        
        try:
            conn = mysql.connector.connect(**config_no_db)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_config.database}` "
                         f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"Created database: {db_config.database}")
        except MySQLError as e:
            logger.error(f"Failed to create database: {e}")
            raise ConnectionError(f"Cannot create database: {e}") from e
    
    @contextmanager
    def get_connection(self) -> Generator[PooledMySQLConnection, None, None]:
        """
        Get a connection from the pool with automatic cleanup.
        
        Usage:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM students")
                results = cursor.fetchall()
            # Connection automatically returned to pool
        
        Yields:
            MySQL connection from pool
        
        Raises:
            ConnectionError: If pool is unavailable or connection fails
        """
        if self._pool is None:
            raise ConnectionError("Database pool not initialized")
        
        conn: Optional[PooledMySQLConnection] = None
        try:
            conn = self._pool.get_connection()
            yield conn
        except MySQLError as e:
            logger.error(f"Database connection error: {e}")
            raise ConnectionError(f"Failed to get connection: {e}") from e
        finally:
            if conn is not None and conn.is_connected():
                conn.close()
    
    @contextmanager
    def transaction(self) -> Generator[PooledMySQLConnection, None, None]:
        """
        Get a connection with transaction support.
        
        Auto-commits on success, auto-rollback on exception.
        
        Usage:
            with db_manager.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO ...", (...))
                cursor.execute("UPDATE ...", (...))
            # Auto-commits if no exception
        
        Yields:
            MySQL connection with transaction started
        
        Raises:
            QueryError: On query failure (after rollback)
        """
        with self.get_connection() as conn:
            try:
                conn.start_transaction()
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction rolled back: {e}")
                raise QueryError(f"Transaction failed: {e}") from e
    
    def execute_query(
        self,
        query: str,
        params: tuple = None,
        fetch_one: bool = False,
        fetch_all: bool = True,
        dictionary: bool = True
    ) -> Optional[Any]:
        """
        Execute a query and return results.
        
        Convenience method for simple queries. For complex operations,
        use get_connection() or transaction() directly.
        
        Args:
            query: SQL query string with %s placeholders
            params: Tuple of parameters for parameterized query
            fetch_one: Return only first result
            fetch_all: Return all results (default)
            dictionary: Return results as dicts (default) or tuples
        
        Returns:
            Query results or None for INSERT/UPDATE/DELETE
        
        Raises:
            QueryError: On query execution failure
        """
        with self.get_connection() as conn:
            try:
                cursor = conn.cursor(dictionary=dictionary)
                cursor.execute(query, params)
                
                if fetch_one:
                    result = cursor.fetchone()
                elif fetch_all:
                    result = cursor.fetchall()
                else:
                    result = None
                
                # Commit for write operations
                if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                    conn.commit()
                
                cursor.close()
                return result
                
            except MySQLError as e:
                logger.error(f"Query execution failed: {e}\nQuery: {query[:200]}")
                raise QueryError(f"Query failed: {e}") from e
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check database connectivity and return status.
        
        Returns:
            Dict with health status and connection info
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                
                return {
                    "status": "healthy",
                    "pool_name": self._pool.pool_name if self._pool else None,
                    "pool_size": self._pool.pool_size if self._pool else 0,
                    "timestamp": datetime.now().isoformat(),
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
    
    def close(self) -> None:
        """Close all connections in the pool."""
        # Note: mysql-connector-python's pool doesn't have explicit close
        # Connections are closed when returned to pool
        logger.info("Database manager closing...")
        self._pool = None
    
    def init_database(self) -> None:
        """
        Initialize database schema.
        
        Creates tables if they don't exist. Safe to call multiple times.
        """
        with self.transaction() as conn:
            cursor = conn.cursor()
            
            # Students table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id_number VARCHAR(50) PRIMARY KEY,
                    full_name VARCHAR(100) NOT NULL,
                    lrn VARCHAR(50),
                    grade_level VARCHAR(20),
                    section VARCHAR(50),
                    guardian_name VARCHAR(100),
                    address VARCHAR(255),
                    guardian_contact VARCHAR(50),
                    photo_path VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_full_name (full_name),
                    INDEX idx_section (section),
                    INDEX idx_grade_level (grade_level)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Generation history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS generation_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id VARCHAR(50) NOT NULL,
                    full_name VARCHAR(100),
                    section VARCHAR(50),
                    lrn VARCHAR(50),
                    guardian_name VARCHAR(100),
                    address VARCHAR(255),
                    guardian_contact VARCHAR(50),
                    file_path VARCHAR(255),
                    status ENUM('success', 'failed', 'pending') DEFAULT 'success',
                    error_message TEXT,
                    processing_time_ms INT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_student_id (student_id),
                    INDEX idx_timestamp (timestamp)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            cursor.close()
            logger.info("Database schema initialized successfully")


# =============================================================================
# SCHEMA INITIALIZATION
# =============================================================================

def init_database() -> None:
    """
    Initialize database schema.
    
    Creates tables if they don't exist. Safe to call multiple times.
    """
    db = DatabaseManager()
    
    with db.transaction() as conn:
        cursor = conn.cursor()
        
        # Students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id_number VARCHAR(50) PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL,
                lrn VARCHAR(50),
                grade_level VARCHAR(20),
                section VARCHAR(50),
                guardian_name VARCHAR(100),
                address VARCHAR(255),
                guardian_contact VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_full_name (full_name),
                INDEX idx_section (section),
                INDEX idx_grade_level (grade_level)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Generation history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generation_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(50) NOT NULL,
                file_path VARCHAR(255),
                status ENUM('success', 'failed', 'pending') DEFAULT 'success',
                error_message TEXT,
                processing_time_ms INT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_student_id (student_id),
                INDEX idx_timestamp (timestamp),
                FOREIGN KEY (student_id) REFERENCES students(id_number) 
                    ON DELETE CASCADE ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        cursor.close()
        logger.info("Database schema initialized successfully")


# =============================================================================
# MODULE-LEVEL SINGLETON
# =============================================================================

# Global database manager instance
db_manager = DatabaseManager()


def get_db() -> DatabaseManager:
    """
    FastAPI dependency for database access.
    
    Usage in routes:
        @router.get("/students")
        def get_students(db: DatabaseManager = Depends(get_db)):
            with db.get_connection() as conn:
                ...
    """
    return db_manager
