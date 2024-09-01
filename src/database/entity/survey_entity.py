from ctypes import Array
from enum import Enum
from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String
from clickhouse_sqlalchemy import types, engines
from src.database.db import Base
from src.common.constants.enum_constant import YesNo, YesNoUnknown, BusinessStatus
from sqlalchemy.orm import relationship

class Survey(Base):
    __tablename__ = 'surveys'
    __table_args__ = (
        engines.ReplacingMergeTree(
            order_by=('_id', 'client_id_manifest', 'submission_time'),
            partition_by=None,
            primary_key=('_id')
        ),
    )

    _id = Column(types.Int, primary_key=True)                     # Original key: "_id"
    formhub_uuid = Column(types.String)                               # Original key: "formhub/uuid"
    start_time = Column(types.DateTime)                               # Original key: "starttime"
    end_time = Column(types.DateTime)                                 # Original key: "endtime"
    survey_date = Column(types.Date)                                  # Original key: "cd_survey_date"
    instance_id = Column(types.String)                                # Original key: "meta/instanceID"
    xform_id_string = Column(types.String)                            # Original key: "_xform_id_string"
    uuid = Column(types.String)                                       # Original key: "_uuid"
    submission_time = Column(types.DateTime)                          # Original key: "_submission_time"
    version = Column(types.String)                                    # Original key: "__version__"
    location_id = Column(types.String, ForeignKey('locations.location_id'))  # Derived from sec_a fields
    surveyor_id = Column(types.String, ForeignKey('surveyors.surveyor_id'))  # Derived from sec_b fields
    client_id_manifest = Column(types.String, ForeignKey('clients.client_id_manifest'))  # Original key: "sec_c/cd_client_id_manifest"
    business_status = Column(types.Enum(BusinessStatus))              # Original key: "group_mx5fl16/cd_biz_status"
    business_operating = Column(types.Enum(YesNoUnknown))        # Original key: "group_mx5fl16/bd_biz_operating"
    _geolocation = Column(types.String, nullable=True) # _geolocation
    _tags = Column(types.Array(String), nullable=True) # _tags
    _notes = Column(types.Array(String), nullable=True) # _notes
    _validation_status = Column(types.String, nullable=True)                         # Original key: "_validation_status"
    _submitted_by = Column(types.String, nullable=True)               # Original key: "_submitted_by"
    last_updated = Column(types.DateTime, nullable=False)

    location = relationship("Location", back_populates="surveys")
    surveyor = relationship("Surveyor", back_populates="surveys")
    client = relationship("Client", back_populates="surveys")
    