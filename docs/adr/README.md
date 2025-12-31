# Architecture Decision Records

This directory contains records of architectural decisions made during the development of DIAL AI Chat Completions.

## ADR Format

Each ADR follows this structure:

```markdown
# ADR-NNN: Title

**Status**: Proposed | Accepted | Rejected | Superseded | Deprecated

**Date**: YYYY-MM-DD

**Context**: Background and problem statement

**Decision**: What was decided

**Consequences**: Trade-offs and implications

**Alternatives Considered**: Other options evaluated
```

## Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-001](./ADR-001-dual-client-implementation.md) | Dual Client Implementation Strategy | Accepted | 2025-12-31 |
| [ADR-002](./ADR-002-dataclass-for-models.md) | Use Dataclasses for Data Models | Accepted | 2025-12-31 |
| [ADR-003](./ADR-003-ephemeral-state-management.md) | Ephemeral State Management | Accepted | 2025-12-31 |
| [ADR-004](./ADR-004-manual-sse-parsing.md) | Manual SSE Parsing in CustomDialClient | Accepted | 2025-12-31 |

## Creating New ADRs

When making significant architectural decisions:

1. **Number**: Use next sequential number (ADR-005, ADR-006, etc.)
2. **File Name**: `ADR-XXX-kebab-case-title.md`
3. **Initial Status**: Start with "Proposed"
4. **Review**: Discuss with team before marking "Accepted"
5. **Updates**: Change status if superseded or deprecated

## Superseded ADRs

When an ADR is superseded:
- Update original ADR status to "Superseded by ADR-XXX"
- Create new ADR explaining new decision
- Link between documents

---

**Related**: See [Architecture](../architecture.md) for current system design
