# -*- coding: utf-8 -*-

from sqlalchemy import *
from sqlalchemy.ext.declarative import *
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.schema import *

Base = declarative_base()

class MyMixin(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)

class Word(Base, MyMixin):
    VELARS = ('г', 'к', 'х')
    SIBILANTS = ('ж', 'ч', 'ш', 'щ')
    VOICED = ('з', 'в', 'д', 'б', 'г', 'ж')
    VOICELESS = ('с', 'ф', 'т', 'п', 'к', 'ш')

    CONS_HARD = VOICED + VOICELESS + ('ц', 'н', 'р', 'л', 'м', 'х', 'ч', 'щ')
    CONS_SOFT = ('й',)
    CONSONANTS = CONS_HARD + CONS_SOFT

    VOWS_A = ('а', 'я')
    VOWS_I = ('ы', 'и')
    VOWS_O = ('о', 'е', 'ё', 'э')
    VOWS_U = ('у', 'ю')

    VOWS_HARD = ('а', 'э', 'ы', 'у', 'о')
    VOWS_SOFT = ('я', 'е', 'и', 'ю', 'ё')
    VOWELS = VOWS_HARD + VOWS_SOFT

    SIGN_HARD = ('ъ',)
    SIGN_SOFT = ('ь',)
    SIGNS = SIGN_HARD + SIGN_SOFT

    LETTS_SOFT = CONS_SOFT + VOWS_SOFT + SIGN_SOFT
    LETTS_HARD = CONS_HARD + VOWS_HARD + SIGN_HARD
    LETTERS = LETTS_HARD + LETTS_SOFT

    spelling = Column(Unicode, unique=True)
    meaning = Column(String)
    type = Column(String)

    __mapper_args__ = {'polymorphic_on': type, 'polymorphic_identity': 'word'}

    def __init__(self, spelling, meaning):
        self.spelling = spelling
        self.meaning = meaning

    def __repr__(self):
        return "%s - %s" % (self.spelling, self.meaning)

    def apply_spelling_rules(self, s_in):
        s = list(s_in)
        while True:
            valid = True
            for i in range(len(s) - 1):
                # 1
                if s[i] in self.VELARS + self.SIBILANTS:
                    if s[i + 1] == 'ы':
                        s[i + 1] = 'и'
                        valid = False
                # 2
                if s[i] in self.VELARS + self.SIBILANTS + ('ц',):
                    if s[i + 1] == 'ю':
                        s[i + 1] = 'y'
                        valid = False
                    if s[i + 1] == 'я':
                       s[i + 1] = 'а'
                       valid = False
            if valid: return ''.join(s)

class Noun(Word):
    MASCULINES = Word.CONSONANTS
    FEMININES = Word.VOWS_A
    NEUTERS = Word.VOWS_O
    UNKNOWNS = Word.SIGNS

    id = Column(Integer, ForeignKey('word.id'), primary_key=True)
    pl = Column(Unicode, nullable=True)
    indeclinable = Column(Boolean)
    g = Column(Enum('m', 'f', 'n', '?', '!'), nullable=True)
    __mapper_args__ = {'polymorphic_identity':'noun'}

    def __init__(self, *args, pl=None, g=None, indeclinable=False):
        super().__init__(*args)
        self.pl = pl
        self.g = g
        self.indeclinable = indeclinable

    def naive_g(self, s):
        if s[-1] in self.MASCULINES: return 'm'
        if s[-1] in self.FEMININES: return 'f'
        if s[-1] in self.NEUTERS: return 'n'
        if s[-1] in self.GENDER_UNKOWNS: return '?'
        else: return '!'

    def naive_pl(self, s):
        if s[-1] in self.CONS_HARD: s_pl =  s + 'ы'
        elif s[-1] == 'а': s_pl = s[:-1] + 'ы'
        elif s[-1] == 'о': s_pl = s[:-1] + 'а'
        elif s[-1] == 'е': s_pl = s[:-1] + 'я'
        elif s[-1] in self.LETTS_SOFT: s_pl = s[:-1] + 'и'
        else: raise Exception
        return self.apply_spelling_rules(s_pl)

    def __repr__(self):
        s = self.spelling
        if self.pl is not None and self.pl != self.naive_pl(self.spelling):
            s += '/%s' % self.pl
        if self.g is not None and self.g != self.naive_g(self.spelling):
            s += ' (%s)' % self.g
        if self.indeclinable: s += ' indecl.'
        return '%s - %s' % (s.capitalize(), self.meaning.capitalize())