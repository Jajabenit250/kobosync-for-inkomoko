from enum import Enum
import os
from dotenv import load_dotenv
import clickhouse_connect
from typing import List, Type, Dict, Any, Union
from pydantic import BaseModel
from datetime import date, datetime
import uuid
from decimal import Decimal

# Load environment variables
load_dotenv()

# Function to map Pydantic (Python) types to ClickHouse SQL types
def map_python_type_to_clickhouse(field_type: Type[Any]) -> str:
    type_mapping = {
        str: "String",
        int: "Int32",
        float: "Float64",
        bool: "UInt8",
        datetime: "DateTime",
        date: "Date",
        uuid.UUID: "UUID",
        Decimal: "Decimal(38, 9)",
        list: "Array(String)",
        dict: "String",
    }
    if issubclass(field_type, Enum):
        return f"Enum8({', '.join([f"'{item.value}' = {i + 1}" for i, item in enumerate(field_type)])})"
    if hasattr(field_type, '__origin__'):
        if field_type.__origin__ is Union and type(None) in field_type.__args__:
            inner_type = [t for t in field_type.__args__ if t is not type(None)][0]
            return f"Nullable({map_python_type_to_clickhouse(inner_type)})"
    return type_mapping.get(field_type, "String")

class ClickHouseProvider:
    def __init__(self, document_models: List[Type[BaseModel]]):
        self.client = clickhouse_connect.get_client(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 8123)),
            username=os.getenv("DB_USER", "default"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME"),
        )
        self.models = {model.__name__: model for model in document_models}
        self.table_definitions = self._generate_table_definitions()
    
    def _generate_table_definitions(self) -> Dict[str, Dict[str, Any]]:
        table_definitions = {}
        
        for model_name, model in self.models.items():
            columns = {}
            indexes = []
            primary_key = None
            
            for field_name, field in model.__fields__.items():
                column_type = map_python_type_to_clickhouse(field.type_)
                columns[field_name] = {
                    "type": column_type,
                    "nullable": field.allow_none,
                }
                
                if field.field_info.extra.get("primary_key", False):
                    primary_key = field_name
                
                if field.field_info.extra.get("index", False):
                    indexes.append(field_name)
            
            if not primary_key:
                primary_key = f"{model_name.lower()}_id"
                columns[primary_key] = {"type": "UInt32", "nullable": False}
            
            partition_by = "toYYYYMM(survey_date)" if 'survey_date' in columns else None
            
            table_definitions[model_name] = {
                "columns": columns,
                "primary_key": primary_key,
                "indexes": indexes,
                "partition_by": partition_by,
            }
            
            if hasattr(model.Config, 'composite_unique'):
                table_definitions[model_name]['composite_unique'] = model.Config.composite_unique
        
        return table_definitions
    
    def _get_existing_schema(self, table_name: str) -> Dict[str, Any]:
        query = f"DESCRIBE TABLE {table_name}"
        result = self.client.query(query)
        
        columns = {}
        for row in result.result_rows:
            column_name, column_type = row[0], row[1]
            columns[column_name] = {
                "type": column_type,
                "nullable": "Nullable" in column_type
            }
        
        return {"columns": columns}
    
    def _generate_alter_statements(self, table_name: str, desired_schema: Dict[str, Any], existing_schema: Dict[str, Any]) -> List[str]:
        alter_statements = []
        
        # Add new columns
        for col_name, col_info in desired_schema['columns'].items():
            if col_name not in existing_schema['columns']:
                alter_statements.append(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_info['type']}")
        
        # Modify existing columns
        for col_name, col_info in desired_schema['columns'].items():
            if col_name in existing_schema['columns']:
                existing_col = existing_schema['columns'][col_name]
                if existing_col['type'] != col_info['type']:
                    alter_statements.append(f"ALTER TABLE {table_name} MODIFY COLUMN {col_name} {col_info['type']}")
        
        # Add new indexes
        for index in desired_schema.get('indexes', []):
            alter_statements.append(f"ALTER TABLE {table_name} ADD INDEX idx_{table_name}_{index} ({index}) TYPE minmax")
        
        # Add composite unique constraints
        for unique_constraint in desired_schema.get('composite_unique', []):
            constraint_name = f"idx_{table_name}_{'_'.join(unique_constraint)}"
            alter_statements.append(f"ALTER TABLE {table_name} ADD INDEX {constraint_name} ({', '.join(unique_constraint)}) TYPE minmax")
        
        return alter_statements
    
    def synchronize(self):
        for table_name, desired_schema in self.table_definitions.items():
            try:
                existing_schema = self._get_existing_schema(table_name)
                alter_statements = self._generate_alter_statements(table_name, desired_schema, existing_schema)
                
                for statement in alter_statements:
                    self.client.command(statement)
                
                print(f"Synchronized table {table_name}")
            except Exception as e:
                if "doesn't exist" in str(e):
                    # Table doesn't exist, create it
                    columns_def = ", ".join([f"{col} {info['type']}" for col, info in desired_schema['columns'].items()])
                    primary_key = desired_schema['primary_key']
                    partition_by = f"PARTITION BY {desired_schema['partition_by']}" if desired_schema['partition_by'] else ""
                    
                    create_statement = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        {columns_def}
                    ) ENGINE = MergeTree()
                    ORDER BY {primary_key}
                    {partition_by}
                    """
                    
                    self.client.command(create_statement)
                    print(f"Created table {table_name}")
                    
                    # Add indexes
                    for index in desired_schema.get('indexes', []):
                        self.client.command(f"ALTER TABLE {table_name} ADD INDEX idx_{table_name}_{index} ({index}) TYPE minmax")
                    
                    # Add composite unique constraints
                    for unique_constraint in desired_schema.get('composite_unique', []):
                        constraint_name = f"idx_{table_name}_{'_'.join(unique_constraint)}"
                        self.client.command(f"ALTER TABLE {table_name} ADD INDEX {constraint_name} ({', '.join(unique_constraint)}) TYPE minmax")
                else:
                    print(f"Error synchronizing table {table_name}: {e}")
        
        self._synchronize_materialized_views()
    
    def _synchronize_materialized_views(self):
        # Add SurveysDailyCount materialized view
        if 'Survey' in self.models:
            self.client.command("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS surveys_daily_count
                ENGINE = SummingMergeTree()
                ORDER BY (survey_date, program_id, cohort_id)
                POPULATE AS
                SELECT
                    survey_date,
                    program_id,
                    cohort_id,
                    count() AS survey_count
                FROM surveys
                GROUP BY survey_date, program_id, cohort_id
            """)
        
        # Add ClientDemographics materialized view
        if 'Client' in self.models:
            self.client.command("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS client_demographics
                ENGINE = AggregatingMergeTree()
                ORDER BY (nationality_id, gender, age_group)
                POPULATE AS
                SELECT
                    nationality_id,
                    gender,
                    intDiv(age, 10) * 10 AS age_group,
                    count() AS client_count,
                    avgState(age) AS avg_age,
                    groupArrayState(education_level_id) AS education_levels
                FROM clients
                GROUP BY nationality_id, gender, age_group
            """)

    def drop_tables(self):
        for table_name in self.table_definitions.keys():
            query = f"DROP TABLE IF EXISTS {table_name.lower()}"
            self.client.query(query)

    def insert(self, model_name: str, entity: BaseModel):
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found.")
        columns = ', '.join(entity.dict().keys())
        values = ', '.join(f"'{v}'" if isinstance(v, str) else str(v) for v in entity.dict().values())
        query = f"INSERT INTO {model_name.lower()} ({columns}) VALUES ({values})"
        self.client.query(query)

    def update(self, model_name: str, entity: BaseModel, condition: Dict[str, Any]):
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found.")
        set_clause = ', '.join(f"{key} = '{value}'" if isinstance(value, str) else f"{key} = {value}" for key, value in entity.dict().items())
        where_clause = ' AND '.join(f"{key} = '{value}'" if isinstance(value, str) else f"{key} = {value}" for key, value in condition.items())
        query = f"ALTER TABLE {model_name.lower()} UPDATE {set_clause} WHERE {where_clause}"
        self.client.query(query)

    def delete(self, model_name: str, condition: Dict[str, Any]):
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found.")
        where_clause = ' AND '.join(f"{key} = '{value}'" if isinstance(value, str) else f"{key} = {value}" for key, value in condition.items())
        query = f"ALTER TABLE {model_name.lower()} DELETE WHERE {where_clause}"
        self.client.query(query)

    def get_all(self, model_name: str) -> List[Dict[str, Any]]:
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found.")
        query = f"SELECT * FROM {model_name.lower()}"
        result = self.client.query(query)
        return result.result_rows

    def find_by_id(self, model_name: str, id: int) -> Dict[str, Any]:
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found.")
        query = f"SELECT * FROM {model_name.lower()} WHERE id = {id}"
        result = self.client.query(query)
        rows = result.result_rows
        return rows[0] if rows else None

