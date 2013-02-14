#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from models import *

def get_session(db_name):
    engine = sqlalchemy.create_engine('sqlite:///%s' % db_name)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

session = get_session(sys.argv[1])

f = open(sys.argv[2], 'r')
assert f.readline().strip().split(',') == ['Spelling', 'Meaning']
for row in f:
    fields = row.strip().split(',')
    if len(fields) == 2:
        session.add(Word(*fields))

session.add(Noun('кот', 'cat'))
session.add(Noun('собака', 'dog'))
session.add(Noun('ребёнок', 'child', pl='дети'))
session.add(Noun('кофе', 'coffee', g='m', indeclinable=True))
session.commit()

for word in session.query(Word).all():
    print(word)