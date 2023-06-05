"""Set up paths for loaders."""

# haven't figured out Django loading yet
# from django.conf import settings

# LOADER_DATA_PATH = settings.BASE_DIR / "loader_data"

from pathlib import Path

SERVER_ROOT = Path(__file__).parent.parent.parent

LOADER_DATA_PATH = SERVER_ROOT / "loader_data"
LOADER_SOURCE_PATH = SERVER_ROOT / "alignment_api/pipelines"
