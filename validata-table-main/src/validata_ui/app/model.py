"""Config model using pydantic."""
from typing import List, Optional, Union

from pydantic import BaseModel, HttpUrl, root_validator


class Link(BaseModel):
    """Link class."""

    title: str
    url: HttpUrl


class ExternalLink(BaseModel):
    """ExternalLink class."""

    name: str
    type: str
    title: str
    description: str
    website: HttpUrl


class Schema(BaseModel):
    """Schema class."""

    name: str
    repo_url: HttpUrl


class Catalog(BaseModel):
    """Catalog class."""

    version: int
    schemas: List[Schema]


class Section(BaseModel):
    """Section class."""

    name: str
    title: str
    description: Optional[str] = None
    catalog: Optional[Union[HttpUrl, Catalog]] = None
    links: Optional[List[ExternalLink]] = None

    @root_validator
    def check_catalog_or_links(cls, values):  # noqa
        """Check that catalog or links attributes is defined but not both."""
        catalog, links = values.get("catalog"), values.get("links")
        if catalog is None and links is None:
            raise ValueError("catalog or links field must be defined")
        if catalog is not None and links is not None:
            raise ValueError("only one of catalog and links must be defined")
        return values


class Footer(BaseModel):
    """Footer section."""

    links: List[Link]


class Header(BaseModel):
    """Header section."""

    links: List[Link]


class Homepage(BaseModel):
    """Homepage section."""

    sections: List[Section]


class Config(BaseModel):
    """Config class defines header, footer and homepage sections."""

    footer: Footer
    header: Header
    homepage: Homepage
