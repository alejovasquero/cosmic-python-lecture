# pylint: disable=attribute-defined-outside-init
from __future__ import annotations
import abc
from typing import ContextManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from allocation import config
from allocation.adapters import repository
import contextlib

class AbstractUnitOfWork(abc.ABC):
    # should this class contain __enter__ and __exit__?
    # or should the context manager and the UoW be separate?
    # up to you!
    batches: repository.AbstractRepository
    is_commited: bool

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_batches(self, reference):
        raise NotImplementedError

    @abc.abstractmethod  
    def start_transaction(self):
        raise NotImplementedError


DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(
        config.get_postgres_uri(),
    )
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory
        self.session = None
        self.is_commited = False

    @contextlib.contextmanager
    def start_transaction(self):
        try:
            self.session = self.session_factory(autocommit=False)
            self.batches = repository.SqlAlchemyRepository(self.session)
            self.is_commited = False
            yield
        except Exception as e:
            self.rollback()
            raise e

        if not self.is_commited:
            self.rollback()

    def commit(self):
        print("COMMITING")
        self.session.commit()
        self.is_commited = True

    def rollback(self):
        self.session.rollback()

    def get_batches(self, reference):
        return self.batches.get(reference=reference)
    

# One alternative would be to define a `start_uow` function,
# or a UnitOfWorkStarter or UnitOfWorkManager that does the
# job of context manager, leaving the UoW as a separate class
# that's returned by the context manager's __enter__.
#
# A type like this could work?
# AbstractUnitOfWorkStarter = ContextManager[AbstractUnitOfWork]