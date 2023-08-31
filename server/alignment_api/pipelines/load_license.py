"""Load external license data.

Not much validation required since this is a simple input file.
"""


from pydantic import BaseModel  # , ValidationError, conint, constr

from . import config


class License(BaseModel):
    """Manage data that is read in from file on a license.

    This should stay in sync with alignment_api.models.License.
    """

    license_id: str
    license_url: str
    attribution: bool
    sharealike: bool
    noderivs: bool
    noncommercial: bool


class Reader(config.Reader):
    """Read external data and marshall for loading into Django."""

    tsvpath = config.LOADER_DATA_PATH / "license.tsv"
    idattr = "license_id"
    model = License
