"""
Structured Logging Configuration
================================
Centralized logging setup with JSON formatting for production.

Features:
- Structured JSON logging for production
- Human-readable console logging for development
- Configurable log levels
- Request ID tracking support
"""

import logging
import sys
from typing import Optional


class StructuredFormatter(logging.Formatter):
    """
    JSON-structured log formatter for production environments.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        import json
        from datetime import datetime
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add location info
        if record.pathname:
            log_entry["location"] = {
                "file": record.filename,
                "line": record.lineno,
                "function": record.funcName
            }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add any extra fields
        for key, value in record.__dict__.items():
            if key not in (
                'name', 'msg', 'args', 'created', 'filename', 'funcName',
                'levelname', 'levelno', 'lineno', 'module', 'msecs',
                'pathname', 'process', 'processName', 'relativeCreated',
                'stack_info', 'exc_info', 'exc_text', 'thread', 'threadName',
                'getMessage', 'message'
            ):
                log_entry[key] = value
        
        return json.dumps(log_entry)


class ConsoleFormatter(logging.Formatter):
    """
    Human-readable console formatter for development.
    """
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, '')
        
        # Format: [TIME] LEVEL logger: message
        timestamp = self.formatTime(record, '%H:%M:%S')
        level = f"{color}{record.levelname:8}{self.RESET}"
        
        message = f"[{timestamp}] {level} {record.name}: {record.getMessage()}"
        
        if record.exc_info:
            message += "\n" + self.formatException(record.exc_info)
        
        return message


def setup_logging(
    level: str = "INFO",
    json_format: bool = False,
    log_file: Optional[str] = None
):
    """
    Configure application logging.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON structured logging (for production)
        log_file: Optional file path for logging
    """
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    if json_format:
        console_handler.setFormatter(StructuredFormatter())
    else:
        console_handler.setFormatter(ConsoleFormatter())
    
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(file_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("watchdog").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("mysql.connector").setLevel(logging.WARNING)
    
    # Log startup
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured: level={level}, json={json_format}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger instance.
    
    Usage:
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.info("Something happened", extra={"user_id": 123})
    """
    return logging.getLogger(name)


class LogContext:
    """
    Context manager for adding structured context to logs.
    
    Usage:
        with LogContext(request_id="abc123", user_id=42):
            logger.info("Processing request")  # Will include request_id and user_id
    """
    
    _context = {}
    
    def __init__(self, **kwargs):
        self.context = kwargs
        self._previous = {}
    
    def __enter__(self):
        self._previous = LogContext._context.copy()
        LogContext._context.update(self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        LogContext._context = self._previous
        return False


class ContextFilter(logging.Filter):
    """
    Filter that adds context variables to log records.
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        for key, value in LogContext._context.items():
            setattr(record, key, value)
        return True
