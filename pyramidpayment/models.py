##############################################################################
#
# Copyright (c) 2013 Rijk Stofberg
# All Rights Reserved.
#
# This software is subject to the provisions of the MIT License (MIT),
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# 
#
##############################################################################

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
    description = Column(Text)
    value = Column(Integer)
    external_reference_number = Column(Text, unique=True)
    status = Column(Text)

    def __init__(self, description, value, external_reference_number=''):
        self.description = description
        self.value = value
        self.external_reference_number = external_reference_number
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
            description = self.description,
            value = self.value, 
            display_value = self.format_value(),
            order_number = self.formatted_order_number(),
            external_reference_number = self.external_reference_number,
        )

    def format_value(self):
        return 'R {0:0.2f}'.format(self.value/100.00) 

    @classmethod
    def by_id(self, id):
        order = DBSession.query(Order).filter(Order.id == id)
        return order.first()

    @classmethod
    def by_external_reference_number(self, external_reference_number):
        orders = DBSession.query(Order).filter(
            Order.external_reference_number == external_reference_number)
        return orders.first()

    @classmethod
    def next_order_number(self, order_number):
        results = DBSession.execute('select max("id") from "order"')
        return results.first()[0] +1


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer,
                Sequence('product_seq_id', optional=True),
                primary_key=True,)
    description = Column(Text)
    price = Column(Integer)

    def __init__(self, description, price):
        self.description = description
        self.price = price

    def format_price(self):
        return 'R {0:0.2f}'.format(self.price/100.00) 

    @classmethod
    def by_id(self, id):
        order = DBSession.query(Product).filter(Product.id == id)
        return order.first()
