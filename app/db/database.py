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
                    birth_date DATE,
                    blood_type VARCHAR(10),
                    emergency_contact VARCHAR(100),
                    emergency_contact_number VARCHAR(50),
                    school_year VARCHAR(20) DEFAULT '2025-2026',
                    status ENUM('active', 'inactive', 'graduated', 'transferred') DEFAULT 'active',
                    school VARCHAR(100) DEFAULT '',
                    entry_type VARCHAR(20) DEFAULT 'import',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_full_name (full_name),
                    INDEX idx_section (section),
                    INDEX idx_grade_level (grade_level),
                    INDEX idx_students_created_at (created_at DESC),
                    INDEX idx_students_school (school)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Teachers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teachers (
                    employee_id VARCHAR(50) PRIMARY KEY,
                    full_name VARCHAR(100) NOT NULL,
                    department VARCHAR(100),
                    position VARCHAR(100),
                    specialization VARCHAR(150),
                    contact_number VARCHAR(50),
                    emergency_contact_name VARCHAR(100),
                    emergency_contact_number VARCHAR(50),
                    address VARCHAR(255),
                    birth_date DATE,
                    blood_type VARCHAR(10),
                    photo_path VARCHAR(255),
                    hire_date DATE,
                    employment_status ENUM('active', 'inactive', 'on_leave') DEFAULT 'active',
                    school VARCHAR(100) DEFAULT '',
                    entry_type VARCHAR(20) DEFAULT 'import',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_full_name (full_name),
                    INDEX idx_department (department),
                    INDEX idx_position (position),
                    INDEX idx_status (employment_status),
                    INDEX idx_teachers_school (school)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Staff table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS staff (
                    id INT AUTO_INCREMENT,
                    id_number VARCHAR(50) NOT NULL,
                    employee_id VARCHAR(50) NOT NULL,
                    full_name VARCHAR(200) NOT NULL,
                    department VARCHAR(100),
                    position VARCHAR(100),
                    contact_number VARCHAR(50),
                    emergency_contact_name VARCHAR(200),
                    emergency_contact_number VARCHAR(50),
                    address TEXT,
                    birth_date DATE,
                    blood_type VARCHAR(10),
                    photo_path VARCHAR(255),
                    school VARCHAR(100) DEFAULT '',
                    entry_type VARCHAR(20) DEFAULT 'import',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (id),
                    UNIQUE KEY uk_staff_id_number (id_number),
                    UNIQUE KEY uk_staff_employee_id (employee_id),
                    INDEX idx_staff_school (school)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # ID Templates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS id_templates (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    template_type ENUM('student', 'teacher', 'staff', 'visitor') NOT NULL DEFAULT 'student',
                    school_level ENUM('elementary', 'junior_high', 'senior_high', 'college', 'all') DEFAULT 'all',
                    is_active BOOLEAN DEFAULT FALSE,
                    is_active_for_students BOOLEAN DEFAULT FALSE,
                    is_active_for_teachers BOOLEAN DEFAULT FALSE,
                    is_active_for_staff BOOLEAN DEFAULT FALSE,
                    thumbnail LONGTEXT,
                    canvas JSON COMMENT 'Canvas dimensions and background settings',
                    front_layers JSON COMMENT 'Array of layer objects for front side',
                    back_layers JSON COMMENT 'Array of layer objects for back side',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_type_level (template_type, school_level),
                    INDEX idx_active (is_active),
                    INDEX idx_templates_active_students (is_active_for_students),
                    INDEX idx_templates_active_teachers (is_active_for_teachers),
                    INDEX idx_templates_active_staff (is_active_for_staff)
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
            
            # Teacher generation history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teacher_generation_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    employee_id VARCHAR(50) NOT NULL,
                    full_name VARCHAR(100),
                    department VARCHAR(100),
                    position VARCHAR(100),
                    file_path VARCHAR(255),
                    status ENUM('success', 'failed', 'pending') DEFAULT 'success',
                    error_message TEXT,
                    processing_time_ms INT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_employee_id (employee_id),
                    INDEX idx_timestamp (timestamp)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Teacher history (unified format)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teacher_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    teacher_id VARCHAR(50),
                    full_name VARCHAR(200),
                    department VARCHAR(100),
                    position VARCHAR(100),
                    file_path VARCHAR(255),
                    template_id INT,
                    status ENUM('success', 'failed') DEFAULT 'success',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_teacher_history_teacher_id (teacher_id),
                    INDEX idx_teacher_history_timestamp (timestamp)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Staff history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS staff_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    staff_id VARCHAR(50),
                    full_name VARCHAR(200),
                    department VARCHAR(100),
                    position VARCHAR(100),
                    file_path VARCHAR(255),
                    template_id INT,
                    status ENUM('success', 'failed') DEFAULT 'success',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_staff_history_staff_id (staff_id),
                    INDEX idx_staff_history_timestamp (timestamp)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # School settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS school_settings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    setting_key VARCHAR(100) UNIQUE NOT NULL,
                    setting_value TEXT,
                    setting_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Active templates view
            cursor.execute("""
                CREATE OR REPLACE VIEW v_active_templates AS
                SELECT 
                    id,
                    name,
                    template_type,
                    school_level,
                    canvas,
                    front_layers,
                    back_layers,
                    created_at,
                    updated_at
                FROM id_templates
                WHERE is_active = TRUE
            """)
            
            # Default Settings Insert
            cursor.execute("""
                INSERT INTO school_settings (setting_key, setting_value, setting_type, description) VALUES
                    ('school_name', 'Sample School', 'string', 'Official school name'),
                    ('school_address', '123 School Street, City', 'string', 'School address'),
                    ('school_contact', '(02) 123-4567', 'string', 'School contact number'),
                    ('principal_name', 'Dr. Juan Dela Cruz', 'string', 'Principal name'),
                    ('principal_signature_path', '', 'string', 'Path to principal signature image'),
                    ('school_year', '2025-2026', 'string', 'Current school year'),
                    ('school_logo_path', '', 'string', 'Path to school logo image')
                ON DUPLICATE KEY UPDATE setting_key = setting_key
            """)
            
            # Check and insert default templates if empty
            cursor.execute("SELECT COUNT(*) as c FROM id_templates")
            template_count = cursor.fetchone()[0]
            
            if template_count == 0:
                student_canvas = '{"width": 591, "height": 1004, "backgroundColor": "#FFFFFF", "backgroundImage": null}'
                student_front = '{"layers": [{"id": "photo-1", "type": "image", "name": "Photo", "field": "photo", "x": 196, "y": 180, "width": 200, "height": 250, "zIndex": 1, "visible": true, "locked": false, "objectFit": "cover", "borderRadius": 8}, {"id": "name-1", "type": "text", "name": "Full Name", "field": "full_name", "text": "STUDENT NAME", "x": 50, "y": 460, "width": 491, "height": 40, "zIndex": 2, "visible": true, "locked": false, "fontSize": 28, "fontFamily": "Arial", "fontWeight": "bold", "color": "#000000", "textAlign": "center", "wordWrap": false, "uppercase": true}, {"id": "id-1", "type": "text", "name": "ID Number", "field": "id_number", "text": "2024-001", "x": 50, "y": 510, "width": 491, "height": 30, "zIndex": 3, "visible": true, "locked": false, "fontSize": 22, "fontFamily": "Arial", "fontWeight": "normal", "color": "#333333", "textAlign": "center", "wordWrap": false}, {"id": "grade-1", "type": "text", "name": "Grade & Section", "field": "grade_level", "text": "Grade 7 - Einstein", "x": 50, "y": 550, "width": 491, "height": 25, "zIndex": 4, "visible": true, "locked": false, "fontSize": 18, "fontFamily": "Arial", "fontWeight": "normal", "color": "#555555", "textAlign": "center", "wordWrap": false}]}'
                student_back = '{"layers": [{"id": "lrn-1", "type": "text", "name": "LRN", "field": "lrn", "text": "LRN: 123456789012", "x": 50, "y": 100, "width": 491, "height": 30, "zIndex": 1, "visible": true, "locked": false, "fontSize": 16, "fontFamily": "Arial", "fontWeight": "normal", "color": "#000000", "textAlign": "left", "wordWrap": false}, {"id": "guardian-1", "type": "text", "name": "Guardian", "field": "guardian_name", "text": "Guardian: PARENT NAME", "x": 50, "y": 140, "width": 491, "height": 30, "zIndex": 2, "visible": true, "locked": false, "fontSize": 14, "fontFamily": "Arial", "fontWeight": "normal", "color": "#333333", "textAlign": "left", "wordWrap": true}, {"id": "address-1", "type": "text", "name": "Address", "field": "address", "text": "Address Line Here", "x": 50, "y": 180, "width": 491, "height": 50, "zIndex": 3, "visible": true, "locked": false, "fontSize": 12, "fontFamily": "Arial", "fontWeight": "normal", "color": "#333333", "textAlign": "left", "wordWrap": true}, {"id": "contact-1", "type": "text", "name": "Emergency Contact", "field": "emergency_contact", "text": "Emergency: 09171234567", "x": 50, "y": 240, "width": 491, "height": 25, "zIndex": 4, "visible": true, "locked": false, "fontSize": 14, "fontFamily": "Arial", "fontWeight": "normal", "color": "#333333", "textAlign": "left", "wordWrap": false}, {"id": "qr-1", "type": "qr_code", "name": "QR Code", "field": "lrn", "x": 220, "y": 700, "width": 150, "height": 150, "zIndex": 5, "visible": true, "locked": false, "backgroundColor": "#FFFFFF", "foregroundColor": "#000000"}]}'
                
                teacher_canvas = '{"width": 591, "height": 1004, "backgroundColor": "#FFFFFF", "backgroundImage": null}'
                teacher_front = '{"layers": [{"id": "photo-1", "type": "image", "name": "Photo", "field": "photo", "x": 196, "y": 180, "width": 200, "height": 250, "zIndex": 1, "visible": true, "locked": false, "objectFit": "cover", "borderRadius": 8}, {"id": "name-1", "type": "text", "name": "Full Name", "field": "full_name", "text": "TEACHER NAME", "x": 50, "y": 460, "width": 491, "height": 40, "zIndex": 2, "visible": true, "locked": false, "fontSize": 28, "fontFamily": "Arial", "fontWeight": "bold", "color": "#000000", "textAlign": "center", "wordWrap": false, "uppercase": true}, {"id": "position-1", "type": "text", "name": "Position", "field": "position", "text": "Teacher", "x": 50, "y": 510, "width": 491, "height": 30, "zIndex": 3, "visible": true, "locked": false, "fontSize": 22, "fontFamily": "Arial", "fontWeight": "normal", "color": "#333333", "textAlign": "center", "wordWrap": false}]}'
                teacher_back = '{"layers": [{"id": "contact-1", "type": "text", "name": "Emergency Contact", "field": "emergency_contact_number", "text": "Emergency: 09171234567", "x": 50, "y": 240, "width": 491, "height": 25, "zIndex": 1, "visible": true, "locked": false, "fontSize": 14, "fontFamily": "Arial", "fontWeight": "normal", "color": "#333333", "textAlign": "left", "wordWrap": false}, {"id": "qr-1", "type": "qr_code", "name": "QR Code", "field": "employee_id", "x": 220, "y": 700, "width": 150, "height": 150, "zIndex": 2, "visible": true, "locked": false, "backgroundColor": "#FFFFFF", "foregroundColor": "#000000"}]}'
                
                insert_template_query = """
                    INSERT INTO id_templates (
                        name, template_type, school_level, is_active, 
                        is_active_for_students, is_active_for_teachers, is_active_for_staff,
                        canvas, front_layers, back_layers
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_template_query, (
                    'Default Student Template', 'student', 'junior_high', True,
                    True, False, False,
                    student_canvas, student_front, student_back
                ))
                cursor.execute(insert_template_query, (
                    'Default Teacher Template', 'teacher', 'all', True,
                    False, True, False,
                    teacher_canvas, teacher_front, teacher_back
                ))
            
            # Migration: Update existing student templates to use 'lrn' instead of 'id_number' for QR layers
            try:
                import json
                cursor.execute("SELECT id, front_layers, back_layers FROM id_templates WHERE template_type = 'student'")
                student_templates = cursor.fetchall()
                for row in student_templates:
                    tid = row[0]
                    front_str = row[1]
                    back_str = row[2]
                    
                    updated = False
                    
                    # Process front layers
                    if front_str:
                        try:
                            front_data = json.loads(front_str)
                            layers = front_data.get('layers', [])
                            for layer in layers:
                                if layer.get('type') == 'qr_code' and layer.get('field') == 'id_number':
                                    layer['field'] = 'lrn'
                                    updated = True
                            if updated:
                                front_str = json.dumps(front_data)
                        except Exception as e:
                            logger.error(f"Error parsing front_layers for template {tid}: {e}")
                            
                    # Process back layers
                    if back_str:
                        try:
                            back_data = json.loads(back_str)
                            layers = back_data.get('layers', [])
                            for layer in layers:
                                if layer.get('type') == 'qr_code' and layer.get('field') == 'id_number':
                                    layer['field'] = 'lrn'
                                    updated = True
                            if updated:
                                back_str = json.dumps(back_data)
                        except Exception as e:
                            logger.error(f"Error parsing back_layers for template {tid}: {e}")
                            
                    if updated:
                        cursor.execute(
                            "UPDATE id_templates SET front_layers = %s, back_layers = %s WHERE id = %s",
                            (front_str, back_str, tid)
                        )
                        logger.info(f"Migrated template {tid} to use 'lrn' for student QR code layer")
            except Exception as e:
                logger.error(f"Error migrating student templates: {e}")
            
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
    db.init_database()


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
