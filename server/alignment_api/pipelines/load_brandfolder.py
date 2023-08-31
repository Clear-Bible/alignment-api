"""Load external brandfolder data.

Not much validation required since this is a simple input file.
"""


from pydantic import BaseModel  # , ValidationError, conint, constr

from . import config


class Brandfolder(BaseModel):
    """Manage data that is read in from file on a brandfolder.

    There's no corresponding Django model: this augments MediaAsset.
    """

    # this key must match the same attribute in the MediaAsset metadata
    media_asset_id: str
    brandfolder_id: str


class Reader(config.Reader):
    """Read external data and marshall for loading into Django."""

    tsvpath = config.LOADER_DATA_PATH / "Brandfolder.tsv"
    idattr = "media_asset_id"
    model = Brandfolder
