from sqlalchemy.orm import joinedload

from clld.web.datatables.base import Col, LinkCol, LinkToMapCol
from clld.web.datatables.value import Values, ValueNameCol
from clld.web.datatables.language import Languages
from clld.web.datatables.parameter import Parameters
from clld.web.datatables.contribution import Contributions, ContributorsCol
from clld.db.util import get_distinct_values
from clld.db.models import common
from clld.web.util.htmllib import HTML, literal
from clld.web.util.helpers import icon
from clld_glottologfamily_plugin.models import Family
from clld_glottologfamily_plugin.datatables import FamilyCol

from abvd.models import Word, Variety, Concept, Wordlist


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


class Words(Values):
    def col_defs(self):
        name_col = ValueNameCol(self, 'value', sTitle='Item:')
        res = []

        if self.parameter:
            return res + [
                LinkCol(self,
                        'language',
                        model_col=common.Language.name,
                        get_object=lambda i: i.valueset.language),
                name_col,
                LinkToMapCol(self, 'm', get_object=lambda i: i.valueset.language),
            ]

        if self.language:
            return res + [
                name_col,
                LinkCol(self,
                        'parameter',
                        model_col=common.Parameter.name,
                        get_object=lambda i: i.valueset.parameter,
                        sTitle='Word:',
                ),
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
                Col(self, 'cognacy', model_col=Word.cognacy, sTitle='Cognacy:'),
                Col(self,
                    'loan',
                    model_col=Word.loan,
                    format=lambda i: 'L' if i.loan != 'false' else '',
                    sTitle='Loan:'),
            ]

        res += [
            name_col,
            #ValueSetCol(self, 'valueset', bSearchable=False, bSortable=False),
            #
            # TODO: contribution col?
            #
        ]
        res.extend([
        ])
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


class Wordlists(Contributions):
    def col_defs(self):
        return [
            # Maybe add details button, opening
            LinkCol(self, 'name'),
            Col(self, 'words', model_col=Wordlist.count_words),
            Col(self, 'concepts', model_col=Wordlist.count_concepts),
            LinkCol(self, 'language', get_object=lambda i: i.language),
            ContributorsCol(self, 'contributor'),
        ]


def includeme(config):
    config.register_datatable('contributions', Wordlists)
    config.register_datatable('values', Words)
    config.register_datatable('parameters', Concepts)
    config.register_datatable('languages', Varieties)
