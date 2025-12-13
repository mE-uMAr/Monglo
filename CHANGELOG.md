# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Flask adapter implementation
- Django adapter implementation
- GridFS file support
- Real-time collaboration features
- GraphQL API support
- Role-based access control (RBAC)
- Audit logging system
- Data migration tools

## [0.1.0] - 2025-11-20

### Added
- Initial project structure
- Core package layout (`monglo/`)
- Framework-agnostic core architecture
- Module structure for:
  - Core engine components (engine, registry, config, introspection, relationships, query_builder)
  - Operations (CRUD, search, aggregations, pagination, export)
  - Views system (base, table_view, document_view, relationship_view)
  - Framework adapters (FastAPI, Flask, Django, Starlette)
  - Field type system (primitives, references, embedded, files, custom)
  - Widget definitions (inputs, selects, displays, custom)
  - Serializers (JSON, table, document)
  - Authentication system (base, simple)
  - Utilities (validators, formatters, index_analyzer)
- UI package structure (`monglo_ui/`)
- Comprehensive test suite structure
  - Unit tests
  - Integration tests
  - Adapter tests
  - End-to-end tests
- Example projects for multiple frameworks
- Documentation structure
- Benchmarking setup
- GitHub workflows for CI/CD
- MIT License
- Professional README with project overview
- Development configuration files
  - pyproject.toml with build system setup
  - .gitignore for Python projects

### Documentation
- Project structure documentation
- README with installation and quick start guide
- LICENSE file (MIT)
- CHANGELOG file

[Unreleased]: https://github.com/me-umar/monglo/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/me-umar/monglo/releases/tag/v0.1.0