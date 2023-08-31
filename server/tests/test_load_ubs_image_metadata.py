"""Test load_license, in particular the License class."""


from alignment_api.pipelines import load_ubs_image_metadata


class TestReader:
    """Test Reader()."""

    rd = load_ubs_image_metadata.Reader()

    def test_init(self) -> None:
        """Test initialization."""
        rod = self.rd["WEB-0001_aaron_rod"]
        assert rod.Id == "WEB-0001_aaron_rod"
