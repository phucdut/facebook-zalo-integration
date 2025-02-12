"""crud user"""

from typing import Any, List

from sqlalchemy.orm import Session

from app.common.client_filter import new_filter
from app.crud.base import CRUDBase
from app.models import Item
from app.schema import ItemCreate, ItemUpdate


class CRUDItem(CRUDBase[Item, ItemCreate, ItemUpdate]):

    pass


crud_item = CRUDItem(Item)
