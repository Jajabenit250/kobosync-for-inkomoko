from dotenv import load_dotenv
from src.common.utils.clickhouse_provider import ClickHouseProvider
from src.database.entity.users_entity import Users

# Load environment variables
load_dotenv()

# Initialize ClickHouseProvider with your models
document_models = [Users]
clickhouse_provider = ClickHouseProvider(document_models=document_models)

def initialize_clickhouse():
    clickhouse_provider.create_tables()

