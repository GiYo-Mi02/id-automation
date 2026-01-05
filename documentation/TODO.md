# ID Automation System — Improvement Backlog

## Critical (Security & Stability)

- [ ] Add basic authentication to web interface
- [ ] Restrict CORS to specific origins (remove wildcard)
- [ ] Add file upload size limits (prevent DoS)
- [ ] Validate file types strictly on server side
- [ ] Add connection pooling for MySQL
- [ ] Implement proper error handling in frontend (replace silent catch blocks)

## High Priority (Reliability)

- [ ] Replace `time.sleep(0.5)` with file-size stabilization check
- [ ] Add job queue for processing (prevent concurrent processing issues)
- [ ] Implement atomic file writes (temp file → rename)
- [ ] Add health check endpoints (`/health`, `/health/db`, `/health/models`)
- [ ] Add structured logging with request IDs
- [ ] Implement graceful shutdown for Watchdog observer

## Medium Priority (Operability)

- [ ] Add retry logic for processing failures
- [ ] Implement model pre-download script
- [ ] Add Dockerfile for consistent environment
- [ ] Create database migration system (Alembic or custom)
- [ ] Add admin interface for viewing logs
- [ ] Implement backup/restore utilities

## UI/UX Improvements

- [ ] Show explicit camera permission status
- [ ] Add progress bar for processing steps
- [ ] Validate manual mode inputs with inline feedback
- [ ] Add zoom controls to layout editor
- [ ] Add keyboard shortcuts (arrow keys for nudge)
- [ ] Bundle Tailwind and fonts locally (offline capability)
- [ ] Add accessibility features (ARIA labels, keyboard nav)
- [ ] Implement toast notifications for success/error

## Nice to Have

- [ ] Add unit tests for processing pipeline
- [ ] Add integration tests for API endpoints
- [ ] Support for batch processing
- [ ] Export to PDF or print-ready format
- [ ] Template versioning and history
- [ ] Audit log for operator actions
- [ ] Support for multiple ID types/templates
- [ ] QR code generation and embedding

## Documentation

- [ ] Add architecture diagrams (beyond sequence)
- [ ] Document deployment to production Windows Server
- [ ] Create backup/restore procedures
- [ ] Document troubleshooting for common ML library issues
- [ ] Add performance tuning guide
- [ ] Create security hardening checklist
