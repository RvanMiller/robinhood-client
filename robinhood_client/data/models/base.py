from abc import ABC
from typing import Optional
from pydantic import BaseModel


# Base Schemas
#
class BaseRequest(BaseModel, ABC):
    pass


class BaseResponse(BaseModel, ABC):
    pass


class BaseCursorRequest(BaseRequest, ABC):
    page_size: Optional[int] = 10


class BaseCursorResponse(BaseResponse, ABC):
    next: Optional[str] = None
    previous: Optional[str] = None
