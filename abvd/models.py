from zope.interface import implementer
from sqlalchemy import (
    Column,
    String,
    Unicode,
    Integer,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin
from clld.db.models.common import Contribution, Language, Value, Parameter

from clld_glottologfamily_plugin.models import HasFamilyMixin


#-----------------------------------------------------------------------------
# specialized common mapper classes
#-----------------------------------------------------------------------------
@implementer(interfaces.IParameter)
class Concept(CustomModelMixin, Parameter):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)
    category = Column(Unicode)
    count_wordlists = Column(Integer, default=0)
    id_int = Column(Integer)


@implementer(interfaces.IContribution)
class Wordlist(CustomModelMixin, Contribution):
    pk = Column(Integer, ForeignKey('contribution.pk'), primary_key=True)
    language_pk = Column(Integer, ForeignKey('language.pk'))
    language = relationship(Language, backref='wordlists')
    notes = Column(Unicode)
    problems = Column(Unicode)
    count_concepts = Column(Integer)
    count_words = Column(Integer)


@implementer(interfaces.IValue)
class Word(CustomModelMixin, Value):
    pk = Column(Integer, ForeignKey('value.pk'), primary_key=True)
    cognacy = Column(Unicode)
    loan = Column(Unicode)
    comment = Column(Unicode)


@implementer(interfaces.ILanguage)
class Variety(CustomModelMixin, Language, HasFamilyMixin):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    glottocode = Column(Unicode)
    count_wordlists = Column(Integer)
    #level = Column(Unicode)
    #parent_language_pk = Column(Integer, ForeignKey('variety.pk'))
    #parent_language = relationship('Variety', backref='dialects', foreign_keys=[parent_language_pk])
