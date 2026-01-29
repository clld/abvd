"""
This module will be available in templates as ``u``.

This module is also used to lookup custom template context providers, i.e. functions
following a special naming convention which are called to update the template context
before rendering resource's detail or index views.
"""
from pyramid.httpexceptions import HTTPFound
from sqlalchemy import text

from clld.db.meta import DBSession
from clld.db.models import common

from abvd import models


def dataset_detail_html(**kw):
    return dict(
        lcount=DBSession.query(common.Language).count(),
        vcount=DBSession.query(common.Value).count(),
        word=DBSession.query(models.Word).order_by(text('RANDOM()')).limit(1).first(),
    )


def parameter_index_html(request=None, **kw):
    if 'v' in request.params:
        raise HTTPFound(request.route_url('parameter', id=request.params['v']))
    return {}


def language_index_html(request=None, **kw):
    if 'id' in request.params:
        raise HTTPFound(request.route_url('language', id=request.params['id']))
    return dict(
        lcount=DBSession.query(common.Language).count(),
        vcount=DBSession.query(common.Value).count(),
    )
