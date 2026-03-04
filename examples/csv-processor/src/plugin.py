"""
CSV Processor Plugin

A working example plugin that reads, filters, transforms, and aggregates CSV data.
Uses only Python standard library (csv, statistics).
"""

import csv
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from statistics import mean


class PluginConfig(dict):
    """Configuration container for plugins."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


class PluginBase(ABC):
    """Abstract base class for all plugins."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the plugin with configuration.

        Args:
            config: Dictionary of configuration parameters
        """
        self.config = PluginConfig(config or {})
        self.setup()

    @abstractmethod
    def setup(self):
        """Called once during initialization. Store or validate configuration."""
        pass

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Any:
        """
        Execute the plugin with the given context.

        Args:
            context: Dictionary containing action and parameters

        Returns:
            Result of the plugin execution
        """
        pass


class CSVProcessor(PluginBase):
    """
    A plugin that reads, filters, transforms, and aggregates CSV files.
    """

    def setup(self):
        """Initialize CSV processor."""
        pass

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action based on context["action"].

        Supported actions:
        - read: Read a CSV file
        - filter: Filter rows by condition
        - add_column: Add a computed column
        - aggregate: Group and aggregate data
        - stats: Get statistics
        """
        action = context.get("action")

        if action == "read":
            return self._read(context)
        elif action == "filter":
            return self._filter(context)
        elif action == "add_column":
            return self._add_column(context)
        elif action == "aggregate":
            return self._aggregate(context)
        elif action == "stats":
            return self._stats(context)
        else:
            return {"error": f"Unknown action: {action}"}

    def _read(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Read a CSV file and return all rows."""
        file_path = context.get("file")

        if not file_path:
            return {"error": "Missing required parameter: file"}

        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        try:
            rows = []
            columns = []

            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                columns = reader.fieldnames or []

                for row in reader:
                    rows.append(row)

            return {
                "status": "success",
                "rows": len(rows),
                "columns": columns,
                "data": rows,
            }

        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}

    def _filter(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Filter rows based on a condition."""
        file_path = context.get("file")
        column = context.get("column")
        condition = context.get("condition")
        value = context.get("value")

        if not all([file_path, column, condition, value is not None]):
            return {
                "error": "Missing required parameters: file, column, condition, value"
            }

        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        try:
            rows = []
            columns = []

            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                columns = reader.fieldnames or []

                for row in reader:
                    if column not in row:
                        continue

                    cell_value = row[column]

                    if self._compare(cell_value, condition, str(value)):
                        rows.append(row)

            return {
                "status": "success",
                "rows": len(rows),
                "columns": columns,
                "filter": {
                    "column": column,
                    "condition": condition,
                    "value": value,
                },
                "data": rows,
            }

        except Exception as e:
            return {"error": f"Failed to filter: {str(e)}"}

    def _add_column(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Add a computed column to the data."""
        file_path = context.get("file")
        column_name = context.get("column_name")
        source_column = context.get("source_column")
        transform = context.get("transform")

        if not all([file_path, column_name, source_column, transform]):
            return {
                "error": "Missing parameters: file, column_name, source_column, transform"
            }

        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        try:
            rows = []
            columns = []

            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                columns = list(reader.fieldnames or [])

                for row in reader:
                    if source_column not in row:
                        continue

                    source_value = row[source_column]
                    computed_value = self._transform(source_value, transform)
                    row[column_name] = computed_value
                    rows.append(row)

            if column_name not in columns:
                columns.append(column_name)

            return {
                "status": "success",
                "rows": len(rows),
                "columns": columns,
                "new_column": column_name,
                "transform": transform,
                "data": rows,
            }

        except Exception as e:
            return {"error": f"Failed to add column: {str(e)}"}

    def _aggregate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate data by grouping and computing statistics."""
        file_path = context.get("file")
        group_by = context.get("group_by")
        aggregate = context.get("aggregate", {})

        if not all([file_path, group_by]):
            return {"error": "Missing required parameters: file, group_by"}

        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        if not isinstance(aggregate, dict):
            return {"error": "aggregate must be a dict of column->function mappings"}

        try:
            groups = {}

            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    if group_by not in row:
                        continue

                    group_key = row[group_by]

                    if group_key not in groups:
                        groups[group_key] = {
                            group_by: group_key,
                            "_data": {col: [] for col in aggregate.keys()},
                        }

                    for col, func in aggregate.items():
                        if col in row:
                            try:
                                groups[group_key]["_data"][col].append(float(row[col]))
                            except (ValueError, TypeError):
                                # Non-numeric values, count them
                                groups[group_key]["_data"][col].append(row[col])

            # Compute aggregations
            result_data = []
            for group_key, group_data in groups.items():
                result_row = {group_by: group_key, "count": 0}

                for col, func in aggregate.items():
                    values = group_data["_data"][col]

                    if func == "sum":
                        result_row[f"{col}_sum"] = sum(v for v in values if isinstance(v, (int, float)))
                    elif func == "count":
                        result_row[f"{col}_count"] = len([v for v in values if isinstance(v, (int, float))])
                    elif func == "avg":
                        numeric_values = [v for v in values if isinstance(v, (int, float))]
                        result_row[f"{col}_avg"] = mean(numeric_values) if numeric_values else 0
                    elif func == "min":
                        numeric_values = [v for v in values if isinstance(v, (int, float))]
                        result_row[f"{col}_min"] = min(numeric_values) if numeric_values else None
                    elif func == "max":
                        numeric_values = [v for v in values if isinstance(v, (int, float))]
                        result_row[f"{col}_max"] = max(numeric_values) if numeric_values else None

                result_row["count"] = len(group_data["_data"][list(aggregate.keys())[0]]) if aggregate else 0
                result_data.append(result_row)

            return {
                "status": "success",
                "groups": len(result_data),
                "group_by": group_by,
                "aggregate": aggregate,
                "data": result_data,
            }

        except Exception as e:
            return {"error": f"Failed to aggregate: {str(e)}"}

    def _stats(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get basic statistics about a CSV file."""
        file_path = context.get("file")

        if not file_path:
            return {"error": "Missing required parameter: file"}

        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        try:
            rows = []
            columns = []
            numeric_columns = []
            column_values = {}

            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                columns = reader.fieldnames or []

                for row in reader:
                    rows.append(row)

            # Identify numeric columns and collect values
            if columns:
                for col in columns:
                    column_values[col] = []

            for row in rows:
                for col in columns:
                    if col in row:
                        try:
                            column_values[col].append(float(row[col]))
                        except (ValueError, TypeError):
                            pass

            # Identify numeric columns
            for col, values in column_values.items():
                if len(values) > 0:  # Has numeric values
                    numeric_columns.append(col)

            # Calculate statistics
            stats = {}
            for col in numeric_columns:
                values = column_values[col]
                if values:
                    stats[col] = {
                        "min": min(values),
                        "max": max(values),
                        "avg": mean(values),
                        "count": len(values),
                    }

            return {
                "status": "success",
                "rows": len(rows),
                "columns": columns,
                "numeric_columns": numeric_columns,
                "stats": stats,
            }

        except Exception as e:
            return {"error": f"Failed to compute stats: {str(e)}"}

    def _compare(self, cell_value: str, condition: str, compare_value: str) -> bool:
        """Compare a cell value with a condition."""
        try:
            # Try numeric comparison
            cell_num = float(cell_value)
            compare_num = float(compare_value)

            if condition == "==":
                return cell_num == compare_num
            elif condition == "!=":
                return cell_num != compare_num
            elif condition == ">":
                return cell_num > compare_num
            elif condition == "<":
                return cell_num < compare_num
            elif condition == ">=":
                return cell_num >= compare_num
            elif condition == "<=":
                return cell_num <= compare_num
        except (ValueError, TypeError):
            # Fall back to string comparison
            pass

        # String comparison
        if condition == "==":
            return cell_value == compare_value
        elif condition == "!=":
            return cell_value != compare_value
        elif condition == "contains":
            return compare_value in cell_value
        elif condition == ">":
            return cell_value > compare_value
        elif condition == "<":
            return cell_value < compare_value
        elif condition == ">=":
            return cell_value >= compare_value
        elif condition == "<=":
            return cell_value <= compare_value

        return False

    def _transform(self, value: str, transform: str) -> str:
        """Apply a transformation to a value."""
        if transform == "upper":
            return value.upper()
        elif transform == "lower":
            return value.lower()
        elif transform == "age_group":
            try:
                age = int(float(value))
                if age < 25:
                    return "18-25"
                elif age < 35:
                    return "25-35"
                elif age < 50:
                    return "35-50"
                else:
                    return "50+"
            except (ValueError, TypeError):
                return "unknown"
        elif transform == "salary_band":
            try:
                salary = float(value)
                if salary < 75000:
                    return "<75k"
                elif salary < 100000:
                    return "75-100k"
                elif salary < 150000:
                    return "100-150k"
                else:
                    return "150k+"
            except (ValueError, TypeError):
                return "unknown"

        return value


if __name__ == "__main__":
    # Example usage with a sample CSV
    import tempfile

    # Create a sample CSV file
    sample_csv = """name,age,department,salary
Alice Johnson,32,Engineering,95000
Bob Smith,28,Sales,65000
Carol White,45,Marketing,75000
David Brown,38,Engineering,105000
Eve Davis,31,HR,60000"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(sample_csv)
        temp_file = f.name

    try:
        plugin = CSVProcessor()

        print("Reading CSV...")
        result = plugin.execute({"action": "read", "file": temp_file})
        print(f"Found {result['rows']} rows")

        print("\nFiltering for Engineering department...")
        result = plugin.execute(
            {
                "action": "filter",
                "file": temp_file,
                "column": "department",
                "condition": "==",
                "value": "Engineering",
            }
        )
        print(f"Found {result['rows']} rows")

        print("\nAdding salary_band column...")
        result = plugin.execute(
            {
                "action": "add_column",
                "file": temp_file,
                "column_name": "salary_band",
                "source_column": "salary",
                "transform": "salary_band",
            }
        )
        print(f"New columns: {result['columns']}")

        print("\nAggregating by department...")
        result = plugin.execute(
            {
                "action": "aggregate",
                "file": temp_file,
                "group_by": "department",
                "aggregate": {"salary": "sum", "age": "avg"},
            }
        )
        print(f"Groups: {result['groups']}")

        print("\nComputing statistics...")
        result = plugin.execute({"action": "stats", "file": temp_file})
        print(f"Numeric columns: {result['numeric_columns']}")

    finally:
        os.unlink(temp_file)
