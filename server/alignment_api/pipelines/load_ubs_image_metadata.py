"""Load external UBS image metadata.

Additional attributes are required 
"""


from pydantic import BaseModel  # , ValidationError, conint, constr

from . import config, load_brandfolder


class Metadata(BaseModel):
    """Manage UBS image metadata, read from file.

    This reflects the file structure, not the Django model: the data
    has to be transformed after reading to match the model
    expectations.

    """

    Id: str
    FileName: str
    Copyright: str
    Title: str
    Subject: str
    Description: str
    Tags: str
    ThematicLink: str
    Authors: str


class Reader(config.Reader):
    """Read external data and marshall for loading into Django."""

    tsvpath = config.LOADER_DATA_PATH / "UBS-images-metadata.tsv"
    idattr = "Id"
    model = Metadata
    brandfolder_data = load_brandfolder.Reader()
