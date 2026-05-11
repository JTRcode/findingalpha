# ADR 0002: Storage Layer

Date: 2026-05-10
Status: Accepted

## Context
The MVP must save raw data, processed bars, features, signal snapshots, and alpha evaluation outputs locally. It should be simple to inspect and easy to migrate.

## Options considered
- CSV/Parquet files: Lowest setup. Parquet is efficient and typed; CSV is readable but weaker for schema and size.
- SQLite: Simple embedded database, but less ideal for analytical columnar workloads.
- DuckDB: Embedded analytical database that can query Parquet directly and integrate with pandas.
- PostgreSQL: Reliable general database, more setup than needed.
- TimescaleDB: Good for time series at scale, unnecessary for daily MVP.
- ClickHouse: Excellent analytical scale, operationally heavier than MVP needs.

## Decision
Use partitioned Parquet files for storage and DuckDB for local analytical queries when needed.

## Rationale
Daily bars and signal snapshots fit naturally in Parquet. DuckDB gives SQL over local files without requiring a server. This keeps the MVP simple while preserving a migration path.

## Consequences
Concurrent writes, access control, and server-style workflows are limited. File organization and schema discipline matter. Later intraday/tick data may require a database upgrade.

## Review triggers
- Data volume becomes slow in local Parquet.
- Multiple users or services need concurrent writes.
- Intraday/tick storage is added.
- Deployment moves beyond a local personal workstation.

