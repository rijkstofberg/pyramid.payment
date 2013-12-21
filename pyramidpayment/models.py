from sqlalchemy import (
    Column,
    Sequence,
    Integer,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer,
                Sequence('order_seq_id', optional=True),
                primary_key=True,
               )
    order_number = Column(Text, unique=True)
    value = Column(Integer)
    status = Column(Text)

    def __init__(self, order_number, value):
        self.order_number = order_number
        self.value = value
        self.status = 'ordered'
