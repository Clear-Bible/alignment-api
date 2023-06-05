"""Load external license data and save into Django."""

from collections import UserDict
from csv import DictReader


from pydantic import BaseModel  # , ValidationError, conint, constr

from .config import LOADER_DATA_PATH


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


class Reader(UserDict):
    """Read external data and marshall for loading into Django."""

    tsvpath = LOADER_DATA_PATH / "license.tsv"

    def __init__(self) -> None:
        """Initialize a Reader instance."""
        super().__init__()
        with self.tsvpath.open() as f:
            reader = DictReader(f, delimiter="\t")
            for row in reader:
                self.row = row
                license_id = row["license_id"]
                self.data[license_id] = License(**row)
