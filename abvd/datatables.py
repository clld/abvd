from sqlalchemy.orm import joinedload

from clld.web.datatables.base import Col, LinkCol, LinkToMapCol, DataTable, IdCol, DetailsRowLinkCol
from clld.web.datatables.value import Values, ValueNameCol
from clld.web.datatables.language import Languages
from clld.web.datatables.parameter import Parameters
from clld.web.datatables.contribution import Contributions, ContributorsCol
from clld.db.util import get_distinct_values, icontains
from clld.db.models import common
from clld.db.meta import DBSession
from clld.web.util.htmllib import HTML, literal
from clld.web.util.helpers import icon, link
from clld_glottologfamily_plugin.models import Family
from clld_glottologfamily_plugin.datatables import FamilyCol
from clld_cognacy_plugin.models import Cognateset, Cognate
from clld_cognacy_plugin.datatables import Cognates

from abvd.models import Word, Variety, Concept, Wordlist


class ABVDCognates(Cognates):
    def col_defs(self):
        cols = Cognates.col_defs(self)
        return [
            cols[0],
            LinkCol(self, 'wordlist', get_object=lambda i: i.counterpart.valueset.contribution),
            cols[1],
            Col(self, 'doubt', model_col=Cognate.doubt, format=lambda i: '?' if i.doubt else '')
        ] + cols[2:]


class ConceptIdCol(LinkCol):
    __kw__ = dict(sTitle='ID:', bSearchable=False)

    def get_attrs(self, item):
        return {'label': str(self.get_obj(item).id_int)}

    def order(self):
        return Concept.id_int


class ConceptNameCol(LinkCol):
    __kw__ = dict(sTitle='Word:', bSearchable=False)

    def get_attrs(self, item):
        item = self.get_obj(item)
        label = literal(item.name)
        if item.description:
            label = HTML.div(label, icon('info-sign', title=item.description))
        return {'label': label, 'title': item.name}

    def order(self):
        return common.Parameter.name


class CognacyCol(Col):
    """
    choices are the individual set numbers
    """
    def __init__(self, dt, name, **kw):
        """Set choices, if a Parameter is selected!"""
        param = kw.pop('parameter', None)
        Col.__init__(self, dt, name, **kw)
        if param:
            self.choices = list(DBSession.query(Cognateset).filter(Cognateset.pk.in_(
                DBSession.query(Cognate.cognateset_pk).filter(Cognate.counterpart_pk.in_(
                    DBSession.query(Word.pk).join(common.Value.valueset).filter(
                        common.ValueSet.parameter == param))
                ))
            ).options(joinedload(Cognateset.cognates)))
            self.choices = [(int(cs.id.split('-')[-1]), len(cs.cognates)) for cs in self.choices]
            self.choices = sorted(self.choices, key=lambda i: i[0])
            self.choices = [f'{i[0]} ({i[1]})' for i in self.choices]

    def format(self, item):
        """Link to individual Cognateset pages!"""
        res = []
        for cog in sorted(item.cognates, key=lambda cog: int(cog.cognateset.id.split('-')[-1])):
            label = cog.cognateset.id.split('-')[-1]
            if cog.doubt:
                label += '?'
            res.append(link(self.dt.req, cog.cognateset, label=label))
            res.append(' ')
        return HTML.div(*res)

    def search(self, qs):
        return icontains(Word.cs_ids, f'-{qs.split()[0]}-')


class Words(Values):
    def base_query(self, query):
        query = Values.base_query(self, query)
        if self.parameter:
            query = query.options(joinedload(Word.cognates), joinedload(Word.cognates, Cognate.cognateset))
        return query

    def col_defs(self):
        name_col = ValueNameCol(self, 'value', sTitle='Item:')
        res = []

        if self.parameter:
            return res + [
                LinkCol(self,
                        'language',
                        model_col=common.Language.name,
                        get_object=lambda i: i.valueset.language),
                LinkCol(self,
                        'wordlist',
                        model_col=common.Contribution.name,
                        get_object=lambda i: i.valueset.contribution),
                name_col,
                CognacyCol(self, 'c', parameter=self.parameter),
                Col(self, 'comment', model_col=Word.comment),
                LinkToMapCol(self, 'm', get_object=lambda i: i.valueset.language),
            ]

        if self.contribution:
            return res + [
                # FIXME: add info with description to parameter col
                ConceptIdCol(
                    self,
                    'id_int',
                    get_object=lambda o: o.valueset.parameter,
                ),
                ConceptNameCol(
                    self,
                    'parameter',
                    model_col=common.Parameter.name,
                    get_object=lambda i: i.valueset.parameter,
                    sTitle='Word:',
                ),
                name_col,
                Col(self, 'comment', model_col=Word.comment, sTitle='Annotation:'),
                Col(self,
                    'loan',
                    model_col=Word.loan,
                    format=lambda i: 'L' if i.loan != 'false' else '',
                    sTitle='Loan:'),
            ]

        res += [
            name_col,
        ]
        return res


class Varieties(Languages):
    def base_query(self, query):
        return query.outerjoin(Family).options(joinedload(Variety.family)).distinct()

    def col_defs(self):
        return [
            LinkCol(self, 'name'),
            Col(self, 'count_wordlists', model_col=Variety.count_wordlists, sTitle='Wordlists:'),
            FamilyCol(self, 'Family', Variety),
            Col(self,
                'latitude',
                sDescription='<small>The geographic latitude</small>'),
            Col(self,
                'longitude',
                sDescription='<small>The geographic longitude</small>'),
            LinkToMapCol(self, 'm'),
        ]


class Concepts(Parameters):
    def col_defs(self):
        return [
            # ID
            ConceptIdCol(self, 'id_int'),
            # Word
            LinkCol(self, 'name', sLabel='Word'),
            # icon-info-sign -> description
            # Category
            Col(self,
                'category',
                model_col=Concept.category,
                choices=get_distinct_values(Concept.category),
                sTitle='Category'),
            # Number of entries
            Col(self, 'count_wordlists', model_col=Concept.count_wordlists, sTitle='Number of wordlists'),
        ]


class LanguageCol(LinkCol):
    def get_obj(self, item):
        return item.language

    def search(self, qs):
        return icontains(common.Language.name, qs)

    def order(self):
        return common.Language.name


class Wordlists(Contributions):
    def base_query(self, query):
        query = Contributions.base_query(self, query)
        return query.join(common.Language).options(joinedload(Wordlist.language))

    def col_defs(self):
        return [
            # Maybe add details button, opening
            DetailsRowLinkCol(self, '?'),
            LinkCol(self, 'name'),
            Col(self, 'words', model_col=Wordlist.count_words),
            Col(self, 'concepts', model_col=Wordlist.count_concepts),
            LanguageCol(self, 'language'),
            ContributorsCol(self, 'contributor'),
        ]


def includeme(config):
    config.register_datatable('contributions', Wordlists)
    config.register_datatable('values', Words)
    config.register_datatable('parameters', Concepts)
    config.register_datatable('languages', Varieties)
