---
name: postgres-query
description: Run read-only PostgreSQL queries via `psql`. Query databases, describe tables, explain query plans, and generate reports without leaving OpenClaw.
metadata:
  openclaw:
    emoji: 🐘
    requires:
      bins:
        - psql
      config:
        - DATABASE_URL
    install:
      - id: homebrew
        kind: brew
        formula: postgresql
        bins:
          - psql
        label: "Install PostgreSQL client (brew)"
      - id: linux
        kind: apt
        package: postgresql-client
        bins:
          - psql
        label: "Install PostgreSQL client (apt)"
---

## Purpose

Execute SQL queries against PostgreSQL databases. Query data, analyze schemas, review statistics, and generate reports directly from OpenClaw workflows without manual database access.

## When to Use

- Query production/staging databases for data analysis
- Generate automated reports (user counts, metrics, etc.)
- Verify data integrity and consistency
- Understand database schema structure
- Analyze slow queries with EXPLAIN plans
- Audit database changes and anomalies

## When Not to Use

- Without proper database access permissions
- For write operations (this skill enforces read-only)
- Without understanding query impact on production
- For sensitive data without encryption/compliance review

## Setup

### Prerequisites

- PostgreSQL installed (client tools only, not full server)
- Access to database credentials
- Network access to database server

### Installation

**macOS (Homebrew):**
```bash
brew install postgresql
```

**Linux (apt):**
```bash
sudo apt-get install postgresql-client
```

**Verify:**
```bash
psql --version  # Should show "psql (PostgreSQL) X.X.X"
```

### Configuration

Set your database connection URL:

```bash
export DATABASE_URL="postgresql://username:password@host:5432/database_name"
```

Or create `.pgpass` for password-less connections:
```bash
echo "host:5432:database:user:password" >> ~/.pgpass
chmod 600 ~/.pgpass
```

**Verify connection:**
```bash
psql "$DATABASE_URL" -c "SELECT version();"
```

## Commands

### Execute Query

Run a SQL query (read-only enforced):

```bash
postgres-query execute "SELECT * FROM users LIMIT 10"
postgres-query execute "SELECT COUNT(*) FROM orders WHERE status = 'pending'"
postgres-query execute "SELECT email FROM users WHERE created_date > NOW() - INTERVAL '7 days'"
postgres-query execute --output json "SELECT id, email, created_at FROM users ORDER BY created_at DESC LIMIT 20"
postgres-query execute --output csv "SELECT * FROM products WHERE price > 100"
```

**Use case**: Run queries, get results in various formats

### Describe Table

Inspect table structure and columns:

```bash
postgres-query describe <table-name>
postgres-query describe <table-name> --verbose   # Includes constraints
```

**Use case**: Understand schema before writing queries

### List Tables

Show all tables in the database:

```bash
postgres-query list-tables
postgres-query list-tables --schema public        # Specific schema
postgres-query list-tables --pattern "user*"     # Pattern filter
```

**Use case**: Explore database structure

### Explain Plan

Analyze query execution plan:

```bash
postgres-query explain "SELECT * FROM users WHERE age > 30"
postgres-query explain "SELECT u.*, o.* FROM users u JOIN orders o ON u.id = o.user_id"
postgres-query explain --analyze "SELECT COUNT(*) FROM large_table"  # Actual run
```

**Use case**: Optimize slow queries, understand performance

### Show Statistics

View table statistics and size:

```bash
postgres-query stats <table-name>
postgres-query stats <table-name> --detailed   # Include row estimates
postgres-query stats --all                     # All tables
```

**Use case**: Understand data volume and distribution

### Check Schema

Show column details with types and constraints:

```bash
postgres-query columns <table-name>
postgres-query columns <table-name> --constraints  # Include FK, PK, etc.
```

**Use case**: Understand data types before writing code

## Examples

### Example 1: Daily Active Users Report

```bash
#!/bin/bash
# Count active users by day for last 30 days

query="
SELECT
  DATE(last_login) as login_date,
  COUNT(DISTINCT user_id) as active_users
FROM user_sessions
WHERE last_login >= NOW() - INTERVAL '30 days'
GROUP BY DATE(last_login)
ORDER BY login_date DESC;
"

postgres-query execute "$query" --output csv > active_users_report.csv
echo "Report saved to active_users_report.csv"
```

### Example 2: Find Slow Queries

```bash
#!/bin/bash
# Find queries taking more than 1 second

query="
SELECT
  query,
  calls,
  total_time,
  mean_time,
  max_time
FROM pg_stat_statements
WHERE query NOT ILIKE '%pg_stat_statements%'
ORDER BY mean_time DESC
LIMIT 20;
"

postgres-query execute "$query" --output json | jq '.[]'
```

### Example 3: Data Quality Checks

```bash
#!/bin/bash
# Check for data anomalies

# Find users with invalid emails
echo "=== Invalid emails ==="
postgres-query execute "
  SELECT COUNT(*) FROM users
  WHERE email IS NULL OR email NOT LIKE '%@%.%'
"

# Find orders without users
echo "=== Orphaned orders ==="
postgres-query execute "
  SELECT COUNT(*) FROM orders o
  WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id = o.user_id)
"

# Find stale accounts (no activity in 6 months)
echo "=== Stale accounts ==="
postgres-query execute "
  SELECT COUNT(*) FROM users
  WHERE last_login < NOW() - INTERVAL '6 months'
"
```

### Example 4: Generate Customer Report

```bash
#!/bin/bash
# Create detailed customer metrics

query="
SELECT
  u.id,
  u.email,
  u.created_at,
  u.last_login,
  COUNT(o.id) as total_orders,
  SUM(o.amount) as lifetime_value,
  MAX(o.created_at) as last_order_date,
  CASE
    WHEN MAX(o.created_at) < NOW() - INTERVAL '6 months' THEN 'Inactive'
    WHEN MAX(o.created_at) < NOW() - INTERVAL '1 month' THEN 'At Risk'
    ELSE 'Active'
  END as customer_status
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.email, u.created_at, u.last_login
ORDER BY lifetime_value DESC
LIMIT 100;
"

postgres-query execute "$query" --output csv > customer_report.csv
echo "Generated customer_report.csv"
```

### Example 5: Compare Data Between Environments

```bash
#!/bin/bash
# Export data from prod and staging to compare

export_db() {
  local db_url=$1
  local table=$2
  local output=$3

  export DATABASE_URL=$db_url
  postgres-query execute "SELECT * FROM $table" --output csv > "$output"
}

echo "Exporting user counts..."
export_db "postgresql://prod-user:pass@prod.db:5432/prod" "users" prod_users.csv
export_db "postgresql://staging-user:pass@staging.db:5432/staging" "users" staging_users.csv

# Compare
echo "Production users: $(wc -l < prod_users.csv)"
echo "Staging users: $(wc -l < staging_users.csv)"

# Show differences
diff <(sort prod_users.csv) <(sort staging_users.csv) | head -20
```

### Example 6: Monitor Table Growth

```bash
#!/bin/bash
# Track table sizes over time

query="
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
  n_live_tup as row_count
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"

postgres-query execute "$query" --output csv | tee table_sizes_$(date +%Y%m%d).csv
```

### Example 7: Analyze Index Usage

```bash
#!/bin/bash
# Find unused or underutilized indexes

query="
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan as scans,
  idx_tup_read as tuples_read,
  idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;
"

echo "=== Index Usage ==="
postgres-query execute "$query" --output json | jq '.[] | select(.scans == 0)'
```

### Example 8: Check Query Performance

```bash
#!/bin/bash
# Analyze slow query before deployment

query="
SELECT u.id, u.email, COUNT(o.id) as orders
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > NOW() - INTERVAL '1 year'
GROUP BY u.id, u.email
HAVING COUNT(o.id) > 5
"

echo "=== EXPLAIN PLAN ==="
postgres-query explain "$query"

echo -e "\n=== ANALYZE ACTUAL EXECUTION ==="
postgres-query explain --analyze "$query"
```

## SQL Query Patterns

### Find Duplicate Data

```sql
SELECT column1, COUNT(*) as count
FROM table_name
GROUP BY column1
HAVING COUNT(*) > 1
ORDER BY count DESC;
```

### Compare Timestamps

```sql
SELECT * FROM table_name
WHERE created_at > NOW() - INTERVAL '7 days'
AND updated_at < NOW() - INTERVAL '1 day';
```

### Aggregate with Conditions

```sql
SELECT
  DATE_TRUNC('day', created_at) as date,
  status,
  COUNT(*) as count,
  SUM(amount) as total
FROM orders
GROUP BY DATE_TRUNC('day', created_at), status
ORDER BY date DESC;
```

### Window Functions for Rankings

```sql
SELECT
  user_id,
  amount,
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) as order_number,
  LAG(amount) OVER (PARTITION BY user_id ORDER BY created_at) as prev_amount
FROM orders
ORDER BY user_id, created_at;
```

### Full Text Search

```sql
SELECT id, title, ts_rank(to_tsvector(content), query) as rank
FROM documents,
  plainto_tsquery(?) as query
WHERE to_tsvector(content) @@ query
ORDER BY rank DESC;
```

## Database Inspection Commands

### Show Table Structure

```bash
postgres-query describe users
```

Output:
```
 Column  |            Type             | Nullable | Default
---------+-----------------------------+----------+---------
 id      | integer                     | NO       | nextval(...)
 email   | character varying(255)      | NO       |
 name    | character varying(255)      | YES      |
 created_at | timestamp with time zone | NO       | now()
 updated_at | timestamp with time zone | NO       | now()
```

### List All Indexes

```sql
SELECT indexname, tablename, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```

### Find Constraints

```sql
SELECT constraint_name, table_name, constraint_type
FROM information_schema.table_constraints
WHERE table_schema = 'public'
ORDER BY table_name, constraint_name;
```

## Performance Tips

1. **Use EXPLAIN ANALYZE**: Before running expensive queries
   ```bash
   postgres-query explain --analyze "SELECT ..."
   ```

2. **Add WHERE clauses**: Filter early and often
3. **Use indexes**: Check `postgres-query stats`
4. **Limit results**: Add LIMIT to prevent huge resultsets
5. **Use aggregation**: GROUP BY instead of post-processing

## Connection Formats

```bash
# Full URL
postgresql://user:password@host:5432/database

# With socket
postgresql:///database?host=/var/run/postgresql

# In psql
psql -h host -U user -d database -p 5432
```

## Output Formats

- `--output csv` - Comma-separated values
- `--output json` - JSON objects
- `--output table` - Formatted table (default)
- `--output tsv` - Tab-separated values

## Environment Variables

- `DATABASE_URL` - Connection string (required)
- `PGPASSWORD` - Password (avoid using, prefer .pgpass)
- `PGHOST` - Host override
- `PGUSER` - User override
- `PGDATABASE` - Database override

## Best Practices

1. **Read-only queries only**: Use SELECT, EXPLAIN, describe operations
2. **Monitor performance**: Use EXPLAIN ANALYZE on complex queries
3. **Batch large exports**: Use LIMIT and OFFSET for pagination
4. **Handle nulls**: Use COALESCE for nullable columns
5. **Document queries**: Add comments explaining business logic
6. **Test on staging**: Before running on production
7. **Limit result sets**: Always add LIMIT unless you need all rows

## Security Notes

- Credentials in DATABASE_URL are sensitive; use `.pgpass` instead
- Read-only user recommended for automated queries
- Don't export sensitive data without encryption
- Audit query access in production
- Never hardcode database credentials in scripts

## Notes

- Queries are read-only enforced (CREATE, UPDATE, DELETE blocked)
- Large result sets automatically paginate
- Connection pooling recommended for high-volume queries
- Query timeout: 30 seconds (configurable)
- Results cached locally; refresh with `--no-cache` flag
