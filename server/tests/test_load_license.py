"""Test load_license, in particular the License class."""


from alignment_api.pipelines import load_license


class TestLicense:
    """Test License dataclass."""

    cc0 = load_license.License(
        license_id="CC0",
        license_url="url",
        attribution=False,
        sharealike=False,
        noderivs=False,
        noncommercial=False,
    )

    def test_init(self) -> None:
        """Test initialization."""
        assert self.cc0.license_id == "CC0"


class TestReader:
    """Test Reader()."""

    rd = load_license.Reader()

    def test_init(self) -> None:
        """Test initialization."""
        cc0 = self.rd["CC0"]
        assert cc0.license_id == "CC0"
        assert cc0.attribution == False
