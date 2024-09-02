from enum import Enum
from clickhouse_sqlalchemy import types, engines
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from src.database.db import Base
from src.common.constants.enum_constant import ResponseType, BusinessStatus
from sqlalchemy.orm import relationship

class SurveyResponse(Base):
    __tablename__ = 'survey_responses'
    __table_args__ = (
        engines.ReplacingMergeTree(
            order_by=('unique_id', 'question_key')
        ),
    )
    
    _id = Column(types.String, ForeignKey('surveys._id')) 
    unique_id = Column(types.String, primary_key=True)    # Original key: "sec_a/unique_id"
    question_key = Column(types.String, primary_key=True) # Original question key from KoboToolbox
    response = Column(types.String)                       # Response value
    response_type = Column(types.Enum(ResponseType))      # Derived from question type
    last_updated = Column(types.DateTime)                 # New field for update tracking
    
    survey = relationship("Survey", back_populates="survey_responses")
    