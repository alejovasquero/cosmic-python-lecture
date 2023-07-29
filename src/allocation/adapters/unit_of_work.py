import abc
from src.allocation.adapters import repository
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from allocation import config

DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(
        config.get_postgres_uri(),
    )
)



class AbstractUnitOfWork(abc.ABC):
    products: repository.AsbtractProductRepository

    def __enter__(self) -> "AbstractUnitOfWork":
        return self
    
    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError
    
    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError
    
class DefaultUnitOfWork(AbstractUnitOfWork):

    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY) -> None:
        self.session_factory = session_factory

    def __enter__(self) -> "DefaultUnitOfWork":
        self.session = self.session_factory()
        self.products = repository.ProductRepository(self.session)
        yield