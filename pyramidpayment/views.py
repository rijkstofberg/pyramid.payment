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

import os
import logging
import transaction

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound

import colander
from deform import Form, ValidationFailure
from deform import widget as widgets

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Order,
    )

from paymentintegrations.processors import PayUProcessor

PAYU_RPP_URL = ''
SUCCESS = 1

CONN_ERR_MSG = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_pyramid.payment_db" script
    to initialize your database tables.  Check your virtual 
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

@view_config(route_name='home', renderer='templates/home.pt')
def home_view(request):
    try:
        one = DBSession.query(Order).filter(Order.id == 1).first()
    except DBAPIError:
        return Response(CONN_ERR_MSG, content_type='text/plain', status_int=500)
    return {}


@view_config(route_name='list_orders', renderer='templates/list_orders.pt')
def list_orders_view(request):
    orders = DBSession.query(Order).all()
    return {'orders': orders}


class OrderSchema(colander.MappingSchema):
    description = colander.SchemaNode(colander.String())
    value = colander.SchemaNode(colander.String())


@view_config(route_name='order', renderer='templates/order.pt')
def order_view(request):
    schema = OrderSchema()
    form = Form(schema,
                css_class='vertical_form',
                buttons=('Place order',))

    if 'Place_order' in request.POST:
        order = Order(
            description = request.POST['description'],
            value = request.POST['value']
        )

        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
            DBSession.add(order)
            DBSession.flush()
            url = request.route_url('confirm')
            url = url + '?order_id=%s' % order.id
            return HTTPFound(location = url)
        except ValidationFailure:
            appstruct = order.as_dict()
            return {'form': form.render(appstruct)}
    else:
        order = Order('', 0)
        appstruct = order.as_dict()
        return {'form': form.render(appstruct)}


@view_config(route_name='confirm', renderer='templates/confirm.pt')
def confirm_view(request):
    message = ''
    order = Order.by_id(int(request.params['order_id']))
    if 'pay_now' in  request.POST:
        processor = PayUProcessor(details = configDetails(order))
        result = processor.setTransaction()
        if result == SUCCESS:
            url = PAYU_RPP_URL + '?order_id=%s' % order.id
            return HTTPFound(url)
    return {'order': order,
            'message': message}

def configDetails(order):
    return dict(
        transactionType       = 'PAYMENT',
        username              = 'Staging Integration Store 1',
        password              = '78cXrW1W',
        safekey               = '{45D5C765-16D2-45A4-8C41-8D6F84042F8C}',
        basket                = dict(
                                  description = 'Basket description',
                                  amountInCents = '100',
                                  currencyCode = 'ZAR',
                                  ),
        additionalInformation = dict(
                                  merchantReference = order.id,
                                  returnUrl = 'http://example.com/return-url',
                                  cancelUrl = 'http://example.com/cancel-url',
                                  supportedPaymentMethods = 'CREDITCARD',
                                  ),
        customer              = dict(
                                  merchantUserId = "7",
                                  email = "john@doe.com",
                                  firstName = 'John',
                                  lastName = 'Doe',
                                  mobile = '0211234567',
                                  ),
        client_log_lvl        = logging.DEBUG,
        transport_log_lvl     = logging.DEBUG,
        schema_log_lvl        = logging.DEBUG,
        wsdl_log_lvl          = logging.DEBUG,
    )
