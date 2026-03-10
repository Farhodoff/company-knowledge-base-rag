# Backend Coding Standards

## Location

This document is maintained in the Engineering wiki: `docs/engineering/backend-standards.md`

## Code Style

- Use Python 3.11+ or Node.js 20 LTS
- Follow PEP 8 (Python) or ESLint (TypeScript)
- Maximum line length: 100 characters
- Use type hints in Python

## API Design

- RESTful endpoints
- Use kebab-case for URLs: `/api/user-profiles`
- Return JSON with snake_case keys
- Include version in path: `/api/v1/`

## Database

- Use migrations for schema changes
- Never commit raw SQL for DDL in application code
- Use connection pooling
