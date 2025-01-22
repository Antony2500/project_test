from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import User
from backend.services.auth import hash_password


async def create_user(db_session: AsyncSession, name: str, email: str, password: str) -> User:
    password_hash = hash_password(password)

    new_user = User(
        name=name,
        email=email,
        password=password_hash
    )

    db_session.add(new_user)
    await  db_session.commit()

    return new_user


async def get_all_users(db_session: AsyncSession) -> List[User]:

    stmt = select(User)
    result = await db_session.execute(stmt)
    users = result.scalars().all()

    return users


async def get_user(db_session: AsyncSession, user_id: int):
    return await db_session.scalar(
        select(User).filter(User.id == user_id)
    )
