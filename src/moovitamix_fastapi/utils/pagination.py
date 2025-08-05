# src/moovitamix_fastapi/utils/pagination.py

from fastapi import Query
from fastapi_pagination import Page

CustomPage = Page.with_custom_options(
    size=Query(100, ge=1, le=100),
)