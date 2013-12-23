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


PAYU_RPP_URL = ''
PAYU_WDSL_URL = 'https://staging.payu.co.za/service/PayUAPI?wsdl'

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
    value = colander.SchemaNode(colander.String())


@view_config(route_name='order', renderer='templates/order.pt')
def order_view(request):
    import pdb;pdb.set_trace()
    schema = OrderSchema()
    form = Form(schema,
                css_class='vertical_form',
                buttons=('submit',))

    if 'submit' in request.POST:
        controls = request.POST.items()
        appstruct = form.validate(controls)
        return HTTPFound(PAYU_RPP_URL)
    else:
        order = Order()
        appstruct = order.as_dict()
        return {'form': form.render(appstruct),
                'order': order}
