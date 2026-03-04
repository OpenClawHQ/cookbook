# CSV Processor Plugin

A plugin that reads, filters, transforms, and aggregates CSV files.

## What It Does

- Read CSV files from disk
- Filter rows based on conditions
- Add computed columns with transformations
- Aggregate data (sum, count, average, min, max)
- Export processed results as CSV or JSON

## Requirements

- Python 3.8+
- CSV files to process

## Configuration

No configuration required. Pass parameters directly when executing the plugin.

## How to Run

```bash
# Install
pip install -e .

# Run
python -m plugin
```

## Example Usage

```python
from src.plugin import CSVProcessor

plugin = CSVProcessor()

# Read a CSV file
data = plugin.execute({
    "action": "read",
    "file": "data.csv"
})

# Filter rows where age > 30
filtered = plugin.execute({
    "action": "filter",
    "file": "data.csv",
    "column": "age",
    "condition": ">",
    "value": 30
})

# Add a computed column (e.g., age group)
transformed = plugin.execute({
    "action": "add_column",
    "file": "data.csv",
    "column_name": "age_group",
    "source_column": "age",
    "transform": "age_group"  # Custom transform
})

# Aggregate by group
summary = plugin.execute({
    "action": "aggregate",
    "file": "data.csv",
    "group_by": "department",
    "aggregate": {"salary": "sum", "age": "avg"}
})
```

## API Actions

### `read`
Read a CSV file and return all rows.

**Parameters:**
- `file` (str): Path to the CSV file

**Returns:**
```python
{
    "status": "success",
    "rows": 100,
    "columns": ["name", "age", "department", "salary"],
    "data": [...]
}
```

### `filter`
Filter rows based on a condition.

**Parameters:**
- `file` (str): Path to the CSV file
- `column` (str): Column to filter on
- `condition` (str): Comparison operator ("==", "!=", ">", "<", ">=", "<=", "contains")
- `value`: Value to compare against

**Returns:**
```python
{
    "status": "success",
    "rows": 25,
    "columns": ["name", "age", "department", "salary"],
    "data": [...]
}
```

### `add_column`
Add a computed column to the data.

**Parameters:**
- `file` (str): Path to the CSV file
- `column_name` (str): Name of the new column
- `source_column` (str): Column to base computation on
- `transform` (str): Transformation type ("upper", "lower", "age_group", "salary_band")

**Returns:**
```python
{
    "status": "success",
    "rows": 100,
    "columns": ["name", "age", "department", "salary", "salary_band"],
    "data": [...]
}
```

### `aggregate`
Aggregate data by grouping and computing statistics.

**Parameters:**
- `file` (str): Path to the CSV file
- `group_by` (str): Column to group by
- `aggregate` (dict): Column -> aggregation function mapping
  - Functions: "sum", "count", "avg", "min", "max"

**Returns:**
```python
{
    "status": "success",
    "groups": 5,
    "data": [
        {
            "department": "Engineering",
            "salary_sum": 450000,
            "age_avg": 32.5,
            "count": 10
        }
    ]
}
```

### `stats`
Get basic statistics about a CSV file.

**Parameters:**
- `file` (str): Path to the CSV file

**Returns:**
```python
{
    "status": "success",
    "rows": 100,
    "columns": ["name", "age", "department", "salary"],
    "numeric_columns": ["age", "salary"],
    "stats": {
        "age": {"min": 22, "max": 65, "avg": 35.2},
        "salary": {"min": 50000, "max": 200000, "avg": 95000}
    }
}
```

## Example Data

Sample `employees.csv`:
```csv
name,age,department,salary
Alice Johnson,32,Engineering,95000
Bob Smith,28,Sales,65000
Carol White,45,Marketing,75000
David Brown,38,Engineering,105000
Eve Davis,31,HR,60000
```

### Filter Example
```python
result = plugin.execute({
    "action": "filter",
    "file": "employees.csv",
    "column": "department",
    "condition": "==",
    "value": "Engineering"
})
# Returns Alice and David
```

### Add Column Example
```python
result = plugin.execute({
    "action": "add_column",
    "file": "employees.csv",
    "column_name": "salary_band",
    "source_column": "salary",
    "transform": "salary_band"
})
# Adds salary bands: <75k, 75-100k, 100-150k, 150k+
```

### Aggregate Example
```python
result = plugin.execute({
    "action": "aggregate",
    "file": "employees.csv",
    "group_by": "department",
    "aggregate": {"salary": "sum", "age": "avg"}
})
# Groups by department and calculates totals
```

## Under the Hood

This plugin uses only Python's standard library (`csv`, `statistics`). No external dependencies required.

## License

MIT License
