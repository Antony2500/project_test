from typing import Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db_session

DBSession_Depends = Annotated[AsyncSession, Depends(get_db_session)]
