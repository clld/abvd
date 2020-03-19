"""
This module will be available in templates as ``u``.

This module is also used to lookup custom template context providers, i.e. functions
following a special naming convention which are called to update the template context
before rendering resource's detail or index views.
"""
from clld.db.meta import DBSession
from clld.db.models import common


def dataset_detail_html(**kw):
    return dict(
        lcount=DBSession.query(common.Language).count(),
        vcount=DBSession.query(common.Value).count(),
    )
