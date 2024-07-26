from typing import Generator, Annotated

from fastapi import Depends

from src.core.db import Session, engine


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session  # So it can close the session after the request is finished


SessionDep = Annotated[Session, Depends(get_db)]  # And then MetaData do be injected