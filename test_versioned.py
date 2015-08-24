import unittest

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from history_meta import Versioned, versioned_session


engine = create_engine('sqlite:///:memory:', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
versioned_session(Session)


class Document(Versioned, Base):
    __tablename__ = 'document'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    description_ = Column('description', String, nullable=True)


DocumentHistory = Document.__history_mapper__.class_


Base.metadata.create_all(engine)


class VersionedTest(unittest.TestCase):

    def test_create_double_flush(self):
        # This test should fail
        document = Document()
        self.session.add(document)
        self.session.flush()
        document.name = 'Foo'
        self.session.flush()
        # IndexError: tuple index out of range

    def test_mutate_plain_column(self):
        # This test should pass
        document = Document()
        self.session.add(document)
        document.name = 'Foo'
        self.session.commit()
        document.name = 'Bar'
        self.session.commit()

        v2 = self.session.query(Document).one()
        v1 = self.session.query(DocumentHistory).one()
        self.assertEqual(v1.id, v2.id)
        self.assertEqual(v2.name, 'Bar')
        self.assertEqual(v1.name, 'Foo')
        # All OK

    def test_mutate_named_column(self):
        # This test should fail
        document = Document()
        self.session.add(document)
        document.description_ = 'Foo'
        self.session.commit()
        document.description_ = 'Bar'
        self.session.commit()

        v2 = self.session.query(Document).one()
        v1 = self.session.query(DocumentHistory).one()
        self.assertEqual(v1.id, v2.id)
        self.assertEqual(v2.description_, 'Bar')
        self.assertEqual(v1.description_, 'Foo')
        # AssertionError: None != 'Foo'

    def setUp(self):
        Base.metadata.create_all(engine)
        self.session = Session()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(engine)
