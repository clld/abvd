from datetime import date
import re
from collections import defaultdict, Counter

from sqlalchemy.orm import joinedload
from clld.cliutil import Data, add_language_codes
from clld.db.meta import DBSession
from clld.db.models import common
from clld.lib import bibtex
from clldutils.misc import slug
from clldutils import color
from pycldf import Sources
from clld_cognacy_plugin.models import Cognate, Cognateset
from nameparser import HumanName

import abvd
from abvd import models


def contributor(data, n):
    name = HumanName(n)
    kw = dict(
        id=slug('{0}{1}'.format(name.last, name.first or name.title)),
        name='{1} {0}'.format(name.last, name.first or name.title),
    )
    c = data['Contributor'].get(kw['id'])
    if not c:
        c = data.add(common.Contributor, kw['id'], **kw)
    return c


def main(args):
    data = Data()

    dataset = common.Dataset(
        id=abvd.__name__,
        name='ABVD',
        description='',
        domain='abvd.clld.org',
        published=date.today(),
        license='https://creativecommons.org/licenses/by/4.0/',
        contact='',
        jsondata={
            'doi': args.doi,
            'license_icon': 'cc-by.png',
            'license_name': 'Creative Commons Attribution 4.0 International License'})
    DBSession.add(dataset)

    for name in ['Simon Greenhill', 'Robert Blust', 'Russell Gray']:
        common.Editor(contributor=contributor(data, name), dataset=dataset)

    cnames = Counter()
    families = Counter([l['Family'] for l in args.cldf['LanguageTable']])
    colors = dict(
        zip([i[0] for i in families.most_common()], color.qualitative_colors(len(families))))
    cid2l = {}
    for lang in args.cldf['LanguageTable']:
        lid = (lang['Name'], lang['Glottocode'])
        l = data['Language'].get(lid)
        if not l:
            l = data.add(
                common.Language, lid,
                id=lang['ID'],
                name=lang['Name'],
                latitude=lang['Latitude'],
                longitude=lang['Longitude'],
                jsondata=dict(
                    family=lang['Family'],
                    icon='{0}{1}'.format('c' if lang['Family'] else 't', colors[lang['Family']]),
                ),
            )
            if lang['Glottocode'] or lang['ISO639P3code']:
                add_language_codes(
                    data, l, isocode=lang['ISO639P3code'], glottocode=lang['Glottocode'])
        cid2l[lang['ID']] = l
        cname = '{0} ({1})'.format(lang['Name'], lang['author'])
        cnames.update([cname])
        if cnames[cname] > 1:
            cname += ' {0}'.format(cnames[cname])
        c = data.add(
            models.Wordlist, lang['ID'],
            id=lang['ID'],
            name=cname,
            description=lang['author'],
            language=l,
            notes=lang['notes'],
        )
        i = 0
        typers = (lang['typedby'] or '').split(' and ')
        checkers = (lang['checkedby'] or '').split(' and ')
        for name in typers:
            i += 1
            DBSession.add(common.ContributionContributor(
                contribution=c,
                contributor=contributor(data, name),
                ord=i,
                jsondata=dict(type='typedby and checkedby' if name in checkers else 'typedby'),
            ))
        for name in checkers:
            if name in typers:
                continue
            i += 1
            DBSession.add(common.ContributionContributor(
                contribution=c,
                contributor=contributor(data, name),
                ord=i,
                jsondata=dict(type='checkedby'),
            ))

    for param in args.cldf['ParameterTable']:
        data.add(
            common.Parameter, param['ID'],
            id=param['ID'],
            name=param['Name'],
        )

    #
    # FIXME: add sources!
    #
    vsrs = set()
    for row in args.cldf['FormTable']:
        vs = data['ValueSet'].get((row['Language_ID'], row['Parameter_ID']))
        if not vs:
            vs = data.add(
                common.ValueSet,
                (row['Language_ID'], row['Parameter_ID']),
                id='{0}-{1}'.format(row['Language_ID'], row['Parameter_ID']),
                language=cid2l[row['Language_ID']],
                parameter=data['Parameter'][row['Parameter_ID']],
                contribution=data['Wordlist'][row['Language_ID']],
            )
        v = data.add(
            common.Value,
            row['ID'],
            id=row['ID'],
            name=row['Form'],
            valueset=vs
        )

    for row in args.cldf['CognateTable']:
        cc = data['Cognateset'].get(row['Cognateset_ID'])
        if not cc:
            cc = data.add(Cognateset, row['Cognateset_ID'], id=row['Cognateset_ID'])
        data.add(
            Cognate,
            row['ID'],
            cognateset=cc,
            counterpart=data['Value'][row['Form_ID']],
            doubt=row['Doubt'],
        )



def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodiucally whenever data has been updated.
    """
