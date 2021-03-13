import pytest

from ..get import get_all_categories, get_category_by_id
from ..update import update_category


@pytest.mark.asyncio
async def test_categories_list_can_be_get(categories):
    assert await get_all_categories()


@pytest.mark.asyncio
async def test_category_can_be_get_by_id(category):
    assert category == await get_category_by_id(category.id)


@pytest.mark.asyncio
async def test_getting_category_by_nonexistent_id_returns_none(db):
    assert await get_category_by_id(2000) is None
