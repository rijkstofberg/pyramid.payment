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
                primary_key=True,)
    external_reference_number = Column(Text)
    value = Column(Integer)
    status = Column(Text)

    def __init__(self, external_reference_number='', value=0):
        self.external_reference_number = external_reference_number
        self.value = value
        self.status = 'order_pending'
    
    def formatted_order_number(self):
        """ Format the id by prepending the string 'order_' and left padding the
            actual id up to 4 characters with '0'.
            e.g. An order with the id '1' will be formatted:
            'order_0001'
        """
        if self.id is None:
            return ''
        return 'order_{id:04}'.format(id=self.id)
    
    def as_dict(self):
        return dict(
            order_number = self.formatted_order_number(),
            value = self.value, 
            external_reference_number = self.external_reference_number,
        )

    @classmethod
    def by_id(self, id):
        order = DBSession.query(Order).filter(Order.id == id)
        return order.first()

    @classmethod
    def next_order_number(self, order_number):
        results = DBSession.execute('select max("id") from "order"')
        return results.first()[0] +1
