from punq import Container

from usecases.interfaces import DBRepositoryInterface

from repositories.db import DBRepository

container = Container()


container.register(
    DBRepositoryInterface,
    DBRepository
)
