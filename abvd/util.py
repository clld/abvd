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
from clld_cognacy_plugin.models import Cognateset, Cognate
from markdown import markdown

from abvd import models


def about(*args, **kw):
    page = DBSession.query(common.Config).filter(common.Config.key == 'about').first()
    links = {k: v for k, v in page.jsondata.items()}

    def repl(line):
        if line.startswith('#'):
            return ('#' if 'About' in line else '##') + line
        for fname, url in page.jsondata.items():
            if fname in line:
                line = line.replace(fname, url)
                del links[fname]
        return line

    qurl = 'https://s3.nexus.mpcdf.mpg.de/eva-dlce-valpal/questionnaire.pdf'
    md = page.value.split('\n')
    #md = [line.replace('ValencyDBQuestionnaireManual.pdf', qurl) for line in md]
    return {'text': markdown('\n'.join(map(repl, md)), extensions=['tables', 'footnotes'])}


#def cognateset_detail_html(**kw):
#    from clld_cognacy_plugin.models import Cognate
#    return {'cognate_cls': Cognate}


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


def contribution_detail_html(context=None, request=None, **kw):
    def csids(wlpk):
        return {
            r[0] for r in DBSession.query(Cognateset.pk)
            .join(Cognate)
            .join(common.Value)
            .join(common.ValueSet).filter(common.ValueSet.contribution_pk == wlpk)}

    ctx_csids = csids(context.pk)
    pmp = DBSession.query(common.Contribution).filter(common.Contribution.id == '269').one()
    poc = DBSession.query(common.Contribution).filter(common.Contribution.id == '270').one()
    return {
        'pmp': pmp,
        'pmp_retentions': len(ctx_csids.intersection(csids(pmp.pk))),
        'poc': poc,
        'poc_retentions': len(ctx_csids.intersection(csids(poc.pk))),
    }
