import mimetypes
from datetime import date
from collections import Counter

from sqlalchemy.orm import joinedload, aliased
from clld.cliutil import Data, add_language_codes, bibtex2source
from clld.db.meta import DBSession
from clld.db.models import common
from clld.lib import bibtex
from clldutils.misc import slug
from clldutils import color
from pycldf import Sources
from clld_cognacy_plugin.models import Cognate, Cognateset
from nameparser import HumanName
from clld_glottologfamily_plugin.util import load_families
from pyglottolog import Glottolog
from markdown import markdown
from csvw import metadata

import abvd
from abvd import models


def md(s):
    if not s:
        return ''
    return markdown(s, extensions=['tables'])


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
        description='Austronesian Basic Vocabulary Database',
        domain='abvd.clld.org',
        published=date.today(),
        license='https://creativecommons.org/licenses/by/4.0/',
        contact='',
        jsondata={
            'doi': '10.5281/zenodo.21703382',
            'license_icon': 'cc-by.png',
            'license_name': 'Creative Commons Attribution 4.0 International License'})
    DBSession.add(dataset)

    about, url_map = None, {}
    for row in args.cldf['MediaTable']:
        if row['Name'] == 'our_research.md':
            about = (args.cldf.directory / row['Download_URL'].unsplit()).read_text(encoding='utf8')
        else:
            url_map[row['Name']] = (f"https://s3.nexus.mpcdf.mpg.de/eva-dlce-abvd/"
                                    f"{row['ID']}{mimetypes.guess_extension(row['Media_Type'])}")
    DBSession.add(common.Config(key='about', value=about, jsondata=url_map))

    for name in ['Simon Greenhill', 'Robert Blust', 'Russell Gray']:
        common.Editor(contributor=contributor(data, name), dataset=dataset)

    for rec in bibtex.Database.from_file(args.cldf.bibpath, lowercase=True):
        data.add(common.Source, rec.id, _obj=bibtex2source(rec))

    cnames = Counter()
    families = Counter([l['Family'] for l in args.cldf['LanguageTable']])
    colors = dict(
        zip([i[0] for i in families.most_common()], color.qualitative_colors(len(families))))
    cid2l = {}
    glangs = {lg.id: lg for lg in Glottolog(args.glottolog).languoids()}

    for lang in args.cldf['LanguageTable']:
        glang = glangs.get(lang['Glottocode'])
        # if Proto in name -> language, otherwise -> dialect
        l = data.add(
            models.Variety, lang['ID'],
            id=lang['ID'],
            name=glang.name if glang else lang['Name'],
            latitude=lang['Latitude'],
            longitude=lang['Longitude'],
            glottocode=lang['Glottocode'],
            jsondata=dict(
                family=lang['Family'],
                icon=f"{'c' if lang['Family'] else 't'}{colors[lang['Family']]}",
            ),
        )
        if lang['Glottocode'] or lang['ISO639P3code']:
            add_language_codes(
                data, l, isocode=lang['ISO639P3code'], glottocode=lang['Glottocode'])

    for wl in args.cldf['ContributionTable']:
        lid = wl['Language_ID']
        cid2l[wl['ID']] = data['Variety'][lid]
        cname = f"{wl['Name']} ({wl['Source_Comment']})"
        cnames.update([cname])
        if cnames[cname] > 1:
            cname += f' {cnames[cname]}'
        c = data.add(
            models.Wordlist, wl['ID'],
            id=wl['ID'],
            name=cname,
            description=wl['Source_Comment'],
            language=cid2l[wl['ID']],
            notes=md(wl['Description']),
            problems=md(wl['problems']),
        )
        i = 0
        typers = [n.strip() for n in (wl['Contributor'] or '').split(' and ') if n.strip()]
        checkers = [n.strip() for n in (wl['checkedby'] or '').split(' and ') if n.strip()]
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
        for sid in wl['Source']:
            common.ContributionReference(contribution=c, source=data['Source'][sid])

    for param in args.cldf['ParameterTable']:
        data.add(
            models.Concept, param['ID'],
            id=param['ID'],
            name=param['Name'],
            description=param['Comment'],
            category=param['Category'],
            id_int=int(param['ID'].split('_')[0]),
        )

    f2c = {}
    for row in args.cldf['FormTable']:
        f2c[row['ID']] = data['Concept'][row['Parameter_ID']].name
        vs = data['ValueSet'].get((row['Language_ID'], row['Parameter_ID']))
        if not vs:
            vs = data.add(
                common.ValueSet,
                (row['Language_ID'], row['Parameter_ID']),
                id='{0}-{1}'.format(row['Language_ID'], row['Parameter_ID']),
                language=cid2l[row['Language_ID']],
                parameter=data['Concept'][row['Parameter_ID']],
                contribution=data['Wordlist'][row['Language_ID']],
            )
        v = data.add(
            models.Word,
            row['ID'],
            id=row['ID'],
            name=row['Form'],
            valueset=vs,
            # FIXME: normalize: remove whitespace!
            cognacy=row['Cognacy'].replace(' ', '') if row['Cognacy'] else None,
            loan=row['Loan'],
            loan_doubt='?' in (row['Loan_Raw'] or ''),
            comment=row['Comment'],
        )

    for row in args.cldf['CognateTable']:
        concept = f2c[row['Form_ID']]
        cc = data['Cognateset'].get(row['Cognateset_ID'])
        if not cc:
            cc = data.add(
                Cognateset, row['Cognateset_ID'],
                id=row['Cognateset_ID'], name=f'{concept} {row["Cognateset_ID"].split("-")[-1]}')
        data.add(
            Cognate,
            row['ID'],
            cognateset=cc,
            counterpart=data['Word'][row['Form_ID']],
            doubt=row['Doubt'],
        )

    load_families(
        Data(),
        [(l.glottocode, l) for l in data['Variety'].values()],
        glottolog_repos=args.glottolog,
        isolates_icon='tcccccc',
        strict=False,
    )


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """
    for lg in DBSession.query(models.Wordlist).options(joinedload(common.Contribution.valuesets).joinedload(common.ValueSet.values)):
        lg.count_concepts = len(lg.valuesets)
        lg.count_words = sum(len(vs.values) for vs in lg.valuesets)
        lg.count_loans = sum(1 if v.loan else 0 for vs in lg.valuesets for v in vs.values)

    for lg in DBSession.query(models.Variety).options(joinedload(models.Variety.wordlists)):
        lg.count_wordlists = len(lg.wordlists)

    for c in DBSession.query(models.Concept).options(joinedload(common.Parameter.valuesets).joinedload(common.ValueSet.values)):
        c.count_wordlists = len(c.valuesets)

    for w in DBSession.query(models.Word).options(joinedload(models.Word.cognates), joinedload(models.Word.cognates, Cognate.cognateset)):
        w.cs_ids = ' '.join(f'{cog.cognateset.id}-{"?" if cog.doubt else ""}' for cog in w.cognates)
