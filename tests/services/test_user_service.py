from unittest.mock import AsyncMock

import pytest

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services import user_service


@pytest.mark.asyncio
async def test_get_all_users_returns_scalars(mock_session, result_stub):
    stored = [User(full_name="Jane Doe", email="jane@example.com", password="secret")]
    mock_session.execute.return_value = result_stub(stored)

    users = await user_service.get_all_users(mock_session)

    assert users == stored
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_user_hashes_password(mock_session):
    payload = UserCreate(full_name="John Smith", email="john@example.com", password="pwd123")

    user = await user_service.create_user(mock_session, payload)

    assert isinstance(user, User)
    assert user.password == hash("pwd123")
    mock_session.add.assert_called_once_with(user)
    assert mock_session.commit.await_count == 1
    assert mock_session.refresh.await_args_list[0].args[0] is user


@pytest.mark.asyncio
async def test_update_user_missing(monkeypatch, mock_session):
    monkeypatch.setattr(user_service, "get_user", AsyncMock(return_value=None))

    result = await user_service.update_user(
        mock_session,
        user_id=77,
        data=UserUpdate(full_name="New", email=None),
    )

    assert result is None
    assert mock_session.commit.await_count == 0


@pytest.mark.asyncio
async def test_delete_user_invokes_session(monkeypatch, mock_session):
    entity = User(full_name="Kate", email="kate@example.com", password="hashed")
    monkeypatch.setattr(user_service, "get_user", AsyncMock(return_value=entity))

    deleted = await user_service.delete_user(mock_session, user_id=1)

    assert deleted is entity
    mock_session.delete.assert_awaited_once_with(entity)
    assert mock_session.commit.await_count == 1


@pytest.mark.asyncio
async def test_get_user_returns_scalar_one_or_none(mock_session, result_stub):
    stored = User(full_name="John Doe", email="john@example.com", password="hashed")
    mock_session.execute.return_value = result_stub([stored])

    user = await user_service.get_user(mock_session, user_id=1)

    assert user == stored
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_user_returns_none_when_not_found(mock_session, result_stub):
    mock_session.execute.return_value = result_stub([])

    user = await user_service.get_user(mock_session, user_id=999)

    assert user is None
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_user_mutates_entity(monkeypatch, mock_session):
    entity = User(full_name="Old Name", email="old@example.com", password="hashed")
    monkeypatch.setattr(user_service, "get_user", AsyncMock(return_value=entity))
    patch = UserUpdate(full_name="New Name", email="new@example.com")

    updated = await user_service.update_user(mock_session, user_id=1, data=patch)

    assert updated is entity
    assert updated.full_name == "New Name"
    assert updated.email == "new@example.com"
    assert mock_session.commit.await_count == 1
    assert mock_session.refresh.await_count == 1
    assert mock_session.refresh.await_args_list[0].args[0] is entity
