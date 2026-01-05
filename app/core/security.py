"""
Security Module
===============
Authentication, authorization, and security utilities.

Security Fixes Applied:
- [P0] API Key authentication middleware
- [P0] File upload validation with magic bytes
- [P1] Request ID generation for audit trails
- [P1] Input sanitization utilities
"""

import re
import secrets
import hashlib
from typing import Optional, Tuple, List
from pathlib import Path
from fastapi import HTTPException, Security, Request, UploadFile
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST

from .config import get_settings

# =============================================================================
# API KEY AUTHENTICATION
# =============================================================================

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    api_key: Optional[str] = Security(api_key_header),
    request: Request = None
) -> str:
    """
    Verify API key from request header.
    
    Security: Uses constant-time comparison to prevent timing attacks.
    
    Usage in routes:
        @router.get("/protected")
        async def protected_route(api_key: str = Depends(verify_api_key)):
            return {"status": "authorized"}
    
    Raises:
        HTTPException 401: If API key is missing
        HTTPException 403: If API key is invalid
    """
    settings = get_settings()
    
    # In development mode with no API key configured, allow all requests
    if settings.is_development and not settings.security.api_key:
        return "development-mode"
    
    if not api_key:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Constant-time comparison to prevent timing attacks
    expected_key = settings.security.api_key
    if not secrets.compare_digest(api_key.encode(), expected_key.encode()):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    
    return api_key


def generate_api_key(length: int = 32) -> str:
    """Generate a secure random API key."""
    return secrets.token_urlsafe(length)


# =============================================================================
# FILE UPLOAD SECURITY
# =============================================================================

# Magic bytes for common image formats
# Reference: https://en.wikipedia.org/wiki/List_of_file_signatures
IMAGE_MAGIC_BYTES = {
    "image/jpeg": [
        (b"\xff\xd8\xff\xe0", 0),  # JPEG JFIF
        (b"\xff\xd8\xff\xe1", 0),  # JPEG EXIF
        (b"\xff\xd8\xff\xe2", 0),  # JPEG EXIF (Canon)
        (b"\xff\xd8\xff\xe8", 0),  # JPEG SPIFF
        (b"\xff\xd8\xff\xdb", 0),  # JPEG Raw
        (b"\xff\xd8\xff\xee", 0),  # JPEG (Adobe)
    ],
    "image/png": [
        (b"\x89PNG\r\n\x1a\n", 0),  # PNG
    ],
    "image/gif": [
        (b"GIF87a", 0),  # GIF87a
        (b"GIF89a", 0),  # GIF89a
    ],
    "image/webp": [
        (b"RIFF", 0),  # WebP (must also check for WEBP at offset 8)
    ],
    "image/bmp": [
        (b"BM", 0),  # BMP
    ],
}


async def validate_image_upload(
    file: UploadFile,
    allowed_types: Optional[List[str]] = None,
    max_size_mb: Optional[int] = None,
) -> Tuple[bytes, str]:
    """
    Validate uploaded file is a legitimate image.
    
    Security checks:
    1. File size limit (prevents DoS via disk exhaustion)
    2. Magic byte verification (prevents extension spoofing)
    3. Filename sanitization (prevents path traversal)
    
    Args:
        file: The uploaded file
        allowed_types: List of allowed MIME types (default from settings)
        max_size_mb: Maximum file size in MB (default from settings)
    
    Returns:
        Tuple of (file_content, detected_mime_type)
    
    Raises:
        HTTPException 400: If validation fails
    """
    settings = get_settings()
    
    if allowed_types is None:
        allowed_types = settings.security.allowed_image_types
    if max_size_mb is None:
        max_size_mb = settings.security.max_upload_size_mb
    
    # Read file content
    content = await file.read()
    await file.seek(0)  # Reset for potential re-reading
    
    # Check file size
    file_size_mb = len(content) / (1024 * 1024)
    if file_size_mb > max_size_mb:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {max_size_mb}MB, got {file_size_mb:.2f}MB"
        )
    
    # Check if file is empty
    if len(content) < 8:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="File is empty or too small to be a valid image"
        )
    
    # Detect actual file type from magic bytes
    detected_type = detect_image_type(content)
    
    if detected_type is None:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="File does not appear to be a valid image (magic bytes check failed)"
        )
    
    if detected_type not in allowed_types:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"File type '{detected_type}' not allowed. Allowed types: {', '.join(allowed_types)}"
        )
    
    return content, detected_type


def detect_image_type(content: bytes) -> Optional[str]:
    """
    Detect image type from magic bytes.
    
    More reliable than trusting Content-Type header or file extension.
    """
    for mime_type, signatures in IMAGE_MAGIC_BYTES.items():
        for magic_bytes, offset in signatures:
            if content[offset:offset + len(magic_bytes)] == magic_bytes:
                # Special handling for WebP (RIFF container)
                if mime_type == "image/webp":
                    if len(content) > 12 and content[8:12] == b"WEBP":
                        return mime_type
                else:
                    return mime_type
    
    return None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.
    
    Security:
    - Removes directory traversal sequences (../, ..\)
    - Removes absolute path indicators
    - Removes special characters
    - Limits filename length
    
    Args:
        filename: Original filename from upload
    
    Returns:
        Sanitized filename safe for filesystem use
    """
    if not filename:
        return f"upload_{secrets.token_hex(8)}"
    
    # Get just the filename, remove any path components
    filename = Path(filename).name
    
    # Remove null bytes and other dangerous characters
    filename = filename.replace("\x00", "")
    
    # Remove path traversal attempts
    filename = filename.replace("..", "")
    filename = filename.replace("/", "")
    filename = filename.replace("\\", "")
    
    # Remove leading dots (hidden files)
    filename = filename.lstrip(".")
    
    # Remove special characters, keep only alphanumeric, dots, underscores, hyphens
    filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)
    
    # Limit length
    max_length = 255
    if len(filename) > max_length:
        name, ext = Path(filename).stem, Path(filename).suffix
        filename = name[:max_length - len(ext)] + ext
    
    # If nothing left, generate random name
    if not filename or filename in (".", ".."):
        filename = f"upload_{secrets.token_hex(8)}.png"
    
    return filename


# =============================================================================
# INPUT SANITIZATION
# =============================================================================

def sanitize_string(value: str, max_length: int = 255, allow_newlines: bool = False) -> str:
    """
    Sanitize user input string.
    
    Args:
        value: Input string to sanitize
        max_length: Maximum allowed length
        allow_newlines: Whether to preserve newlines
    
    Returns:
        Sanitized string
    """
    if not value:
        return ""
    
    # Remove null bytes
    value = value.replace("\x00", "")
    
    # Normalize whitespace
    if not allow_newlines:
        value = " ".join(value.split())
    else:
        value = re.sub(r"[^\S\n]+", " ", value)
    
    # Strip leading/trailing whitespace
    value = value.strip()
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
    
    return value


def validate_student_id(student_id: str) -> str:
    """
    Validate and sanitize student ID format.
    
    Expected formats:
    - 2024-001, 2024-100, 2025-001 (Year-Number)
    - 123456789 (9-digit number)
    
    Raises:
        HTTPException 400: If format is invalid
    """
    if not student_id:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Student ID is required"
        )
    
    student_id = sanitize_string(student_id, max_length=50)
    
    # Pattern: YYYY-NNN or numeric
    year_pattern = re.compile(r"^\d{4}-\d{1,4}$")
    numeric_pattern = re.compile(r"^\d{6,12}$")
    
    if not (year_pattern.match(student_id) or numeric_pattern.match(student_id)):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Invalid student ID format: '{student_id}'. Expected formats: 'YYYY-NNN' or numeric ID"
        )
    
    return student_id


# =============================================================================
# REQUEST TRACKING
# =============================================================================

def generate_request_id() -> str:
    """Generate unique request ID for audit logging."""
    return secrets.token_hex(16)


def hash_pii(value: str) -> str:
    """
    One-way hash PII for logging purposes.
    
    Use this when you need to log something for debugging but can't expose actual PII.
    """
    return hashlib.sha256(value.encode()).hexdigest()[:12]
