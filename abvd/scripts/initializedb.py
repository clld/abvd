from datetime import date
import re
from collections import defaultdict, Counter

from sqlalchemy.orm import joinedload
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

import abvd
from abvd import models

GEO = {
    'Fijian (Ba; Nakoroboya)': '-17.65° S, 177.80',
    "Red Ston": "linked to tasi1237 in Vanuatu Voices",
}

WORD_NOTES = {
    "8": ("to turn", "veer to the side, as in turning left"),
    "13": ("back", "body part"),
    "26": ("hair", "of the head"),
    "38": ("to chew", "A: general term; B: chew betel"),
    "39": ("to cook", "A: general term; B: boil food"),
    "49": ("to lie down", "to sleep"),
    "67": ("to sew", "clothing"),
    "69": ("to hunt", "for game"),
    "70": ("to shoot", "an arrow"),
    "72": ("to hit", "with stick, club"),
    "77": ("to scratch", "an itch"),
    "78": ("to cut, hack", "wood"),
    "80": ("to split", "transitive"),
    "83": ("to work", "in garden, field"),
    "86": ("to grow", "intransitive"),
    "87": ("to swell", "as an abcess"),
    "88": ("to squeeze", "as juice from a fruit"),
    "89": ("to hold", "in the fist"),
    "93": ("to pound, beat", "as rice or prepared food"),
    "94": ("to throw", "as a stone"),
    "95": ("to fall", "as a fruit"),
    "108": ("louse", "A: general term, B: head louse"),
    "112": ("rotten", "of food, or corpse"),
    "113": ("branch", "the branch itself, not the fork of the branch"),
    "122": ("water", "fresh water"),
    "131": ("cloud", "white cloud, not a rain cloud"),
    "137": ("to blow", "A: of the wind, B: with the mouth"),
    "138": ("warm", "of weather"),
    "139": ("cold", "of weather"),
    "140": ("dry", "A: general term, B: to dry up"),
    "144": ("to burn", "transitive"),
    "145": ("smoke", "of a fire"),
    "154": ("short", "A: in height, B: in length"),
    "155": ("long", "of objects"),
    "156": ("thin", "of objects"),
    "157": ("thick", "of objects"),
    "162": ("old", "of people"),
    "170": ("when?", "question"),
    "171": ("to hide", "intransitive"),
    "172": ("to climb", "A: ladder, B: mountain"),
    "181": ("where?", "question"),
    "185": ("we", "A: inclusive, B: exclusive"),
    "188": ("what?", "question"),
    "189": ("who?", "question"),
    "194": ("how?", "question"),
    "197": ("One", "1"),
    "198": ("Two", "2"),
    "199": ("Three", "3"),
    "200": ("Four", "4"),
    "201": ("Five", "5"),
    "202": ("Six", "6"),
    "203": ("Seven", "7"),
    "204": ("Eight", "8"),
    "205": ("Nine", "9"),
    "206": ("Ten", "10"),
    "207": ("Twenty", "20"),
    "208": ("Fifty", "50"),
    "209": ("One Hundred", "100"),
    "210": ("One Thousand", "1,000"),
}
WORD_NOTES = {k: v[1] for k, v in WORD_NOTES.items()}


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
    wordlists = {r['ID']: r for r in args.cldf['ContributionTable']}
    for lang in args.cldf['LanguageTable']:
        wl = wordlists[lang['ID']]
        lid = lang['Glottocode'] or lang['ID']
        l = data['Variety'].get(lid)
        if not l:
            glang = glangs.get(lang['Glottocode'])
            # if Proto in name -> language, otherwise -> dialect
            l = data.add(
                models.Variety, lid,
                id=lid,
                name=glang.name if glang else lang['Name'],
                latitude=lang['Latitude'],
                longitude=lang['Longitude'],
                glottocode=lang['Glottocode'],
                jsondata=dict(
                    family=lang['Family'],
                    icon='{0}{1}'.format('c' if lang['Family'] else 't', colors[lang['Family']]),
                ),
            )
            if lang['Glottocode'] or lang['ISO639P3code']:
                add_language_codes(
                    data, l, isocode=lang['ISO639P3code'], glottocode=lang['Glottocode'])

        cid2l[lang['ID']] = l
        cname = '{0} ({1})'.format(lang['Name'], wl['Source_Comment'])
        cnames.update([cname])
        if cnames[cname] > 1:
            cname += f' {cnames[cname]}'
        c = data.add(
            models.Wordlist, lang['ID'],
            id=lang['ID'],
            name=cname,
            description=wl['Source_Comment'],
            language=l,
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
            description=WORD_NOTES.get(param['ID'].split('_')[0]),
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

    for lg in DBSession.query(models.Variety).options(joinedload(models.Variety.wordlists)):
        lg.count_wordlists = len(lg.wordlists)

    for c in DBSession.query(models.Concept).options(joinedload(common.Parameter.valuesets).joinedload(common.ValueSet.values)):
        c.count_wordlists = len(c.valuesets)

    for w in DBSession.query(models.Word).options(joinedload(models.Word.cognates), joinedload(models.Word.cognates, Cognate.cognateset)):
        w.cs_ids = ' '.join(f'-{cog.cognateset.id.split("-")[-1]}-' for cog in w.cognates)
