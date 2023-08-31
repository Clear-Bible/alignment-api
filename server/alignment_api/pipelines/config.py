"""Set up paths for loaders."""

# haven't figured out Django loading yet
# from django.conf import settings

# LOADER_DATA_PATH = settings.BASE_DIR / "loader_data"

from pathlib import Path
from collections import UserDict
from csv import DictReader

from pydantic import BaseModel  # , ValidationError, conint, constr


SERVER_ROOT = Path(__file__).parent.parent.parent

LOADER_DATA_PATH = SERVER_ROOT / "loader_data"
LOADER_SOURCE_PATH = SERVER_ROOT / "alignment_api/pipelines"


class Reader(UserDict):
    """Read external data and marshall for loading into Django.

    This is generalized for use where the source data is in TSV, with
    column headers that match a BaseModel instance, and a designated
    identity element.

    """

    # subs must define these
    tsvpath: Path = None
    idattr: str = ""
    model: BaseModel = None

    def __init__(self) -> None:
        """Initialize a Reader instance."""
        super().__init__()
        assert self.tsvpath, "tsvpath must be defined"
        assert self.idattr, "idattr must be defined"
        assert self.model, "model must be defined"
        with self.tsvpath.open() as f:
            reader = DictReader(f, delimiter="\t")
            self.data = {
                idattr: self.model(**row) for row in reader if (idattr := row[self.idattr])
            }
