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

""" Add some demo data and a couple of products to test against. 
"""

import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import (
    DBSession,
    Order,
    Product,
    )


DEMO_PRODUCTS = (
    ('Product 1', 1000),
    ('Product 2', 2000),
    ('Product 3', 3000),
    ('Product 4', 4000),
    ('Product 5', 5000),
    ('Product 6', 6000),
)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    with transaction.manager:
        for i in range(1,11):
            order = Order('order_%s' % i, i, 'exref_%s' % i)
            DBSession.add(order)
    orders = DBSession.query(Order).all()
    print len(orders)

    with transaction.manager:
        for description, price in DEMO_PRODUCTS:
            product = Product(description, price)
            DBSession.add(product)
    products = DBSession.query(Product).all()
    print len(products)
