from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from clickhouse_sqlalchemy import engines
from datetime import datetime
from src.database.db import Base

class Issue(Base):
    __tablename__ = 'issues'
    
    id = Column(Integer, primary_key=True)
    entity_type = Column(String)
    issue_type = Column(String)
    entity_id = Column(String)
    details = Column(String)  # JSON will be stored as a String
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        engines.MergeTree(
            order_by=(entity_type, issue_type, entity_id, created_at),
            primary_key=(entity_type, issue_type, entity_id),
        ),
    )
    