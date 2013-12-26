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
    Product,
    )

from paymentintegrations.processors import PayUProcessor

SUCCESS = 200

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
    """ The root of the application. The first page most users see.
    """
    try:
        one = DBSession.query(Order).filter(Order.id == 1).first()
    except DBAPIError:
        return Response(CONN_ERR_MSG, content_type='text/plain', status_int=500)
    return {}


@view_config(route_name='list_orders', renderer='templates/list_orders.pt')
def list_orders_view(request):
    """ List all order in the system.
    """
    orders = DBSession.query(Order).all()
    return {'orders': orders}


class OrderSchema(colander.MappingSchema):
    """ Defines what a order looks like, data wise.
    """
    description = colander.SchemaNode(colander.String())
    value = colander.SchemaNode(
        colander.String(),
        widget = widgets.HiddenWidget()
    )
    display_value = colander.SchemaNode(
        colander.String(),
        missing= '',
        widget = widgets.TextInputWidget(readonly = True)
    )


class OrderView(object):
    """ Facilitates the selection of product and the initiating of a PayU
        payment transaction.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='order', renderer='templates/order.pt')
    def order_view(self):
        schema = OrderSchema()
        form = Form(schema,
                    css_class='vertical_form',
                    buttons=('Confirm order',))

        if 'Confirm_order' in self.request.POST:
            order = Order(
                description = self.request.POST['description'],
                value = self.request.POST['value']
            )

            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
                DBSession.add(order)
                DBSession.flush()
                url = self.request.route_url('confirm')
                url = url + '?order_id=%s' % order.id
                return HTTPFound(location = url)
            except ValidationFailure:
                appstruct = order.as_dict()
                return {'form': form.render(appstruct)}
        elif 'product_id' in self.request.params:
            product = Product.by_id(int(self.request.params.get('product_id')))
            order = Order(product.description, product.price)
            schema.get('display_value').missing = product.price
            appstruct = order.as_dict()
            return {'form': form.render(appstruct),
                    'order': order}
        return {}

    def products(self):
        """ Utility method used by the template to render all orders.
        """
        return DBSession.query(Product).all()


@view_config(route_name='confirm', renderer='templates/confirm.pt')
def confirm_view(request):
    """ Helps the user confirm the selected product and move to the payment
        step.
    """
    message = ''
    order = Order.by_id(int(request.params['order_id']))
    if 'pay_now' in  request.POST:
        settings = request.registry.settings
        processor = PayUProcessor(details = configDetails(order, settings))
        resultCode, resultObj = processor.setTransaction()
        if resultCode == SUCCESS:
            order.external_reference_number = resultObj.payUReference
            payu_RPP_URL = settings.get('payu_RPP_URL')
            url = payu_RPP_URL + '?PayUReference=%s' % resultObj.payUReference
            message = resultObj.__repr__()
            return HTTPFound(url)
    return {'order': order,
            'message': message}

def configDetails(order, settings):
    """ Look in ./etc for the relevant .ini.in file.  It declares a lot of the
        settings used below.
        This method helps us build the settings necessary to speak to the 
        PayU payment webservice.
    """
    return dict(
        transactionType       = 'PAYMENT',
        username              = settings.get('username'),
        password              = settings.get('password'),
        safekey               = settings.get('safekey'),
        basket                = dict(
                                  description = order.description,
                                  amountInCents = order.value,
                                  currencyCode = 'ZAR',
                                  ),
        additionalInformation = dict(
                                  merchantReference = order.id,
                                  returnUrl = settings.get('returnUrl'),
                                  cancelUrl = settings.get('cancelUrl'),
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


@view_config(route_name='payment-processed', renderer='templates/payment_processed.pt')
def payment_processed_view(request):
    """ Used as callback view for PayU to tell the user what happened during
        the payment process.
        This view also puts the order in the 'paid' state.
    """
    ext_ref = request.params.get('payUReference',
              request.params.get('PayUReference'))
    order = Order.by_external_reference_number(ext_ref)
    order.status = 'paid'
    return {'order': order}


@view_config(route_name='payment-cancelled', renderer='templates/payment_cancelled.pt')
def payment_cancelled_view(request):
    """ PayU redirects here if the user cancels the payment process.
        This view also puts the order in the 'cancelled' state.
    """
    ext_ref = request.params.get('payUReference',
              request.params.get('PayUReference'))
    order = Order.by_external_reference_number(ext_ref)
    order.status = 'cancelled'
    return {'order': order}
