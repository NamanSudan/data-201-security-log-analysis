from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class IshaanHttpAccessStaging(Base):
    __tablename__ = "ishaan_http_access_staging"
    __table_args__ = (
        CheckConstraint("line_number > 0", name="ishaan_http_access_staging_line_number_ck"),
        Index("ishaan_http_access_staging_event_ts_idx", "event_timestamp"),
        Index("ishaan_http_access_staging_client_ip_ts_idx", "client_ip", "event_timestamp"),
        {"schema": "staging"},
    )

    line_number = Column(Integer, primary_key=True)
    event_timestamp = Column(DateTime(timezone=True))
    client_ip = Column(INET)
    http_method = Column(String(10))
    request_url = Column(Text)
    url_path = Column(Text)
    query_string = Column(Text)
    status_code = Column(SmallInteger)
    bytes_sent = Column(Integer)
