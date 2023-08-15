import abc
from src.allocation.domain import model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch):
        self.session.add(batch)

    def get(self, reference):
        return self.session.query(model.Batch).filter_by(reference=reference).one()

    def list(self):
        return self.session.query(model.Batch).all()


class AsbtractProductRepository(abc.ABC):

    @abc.abstractmethod
    def get(self, sku: str) -> model.Product:
        ...

    @abc.abstractmethod
    def add(self, product: model.Product) -> model.Product:
        ...


class ProductRepository(AsbtractProductRepository):

    def __init__(self, session):
        self.session = session

    def get(self, sku: str) -> model.Product:
        return self.session.query(model.Product).filter_by(sku=sku).one()

    def add(self, product: model.Product) -> model.Product:
        self.session.add(product)
