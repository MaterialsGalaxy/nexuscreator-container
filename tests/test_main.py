import os
from pathlib import Path
import sys

import pytest

from nexuscreator_container.main import main


class TestMain:
    @pytest.mark.parametrize(
        ["arguments", "expected_filepath"],
        [
            pytest.param(
                ["tests/data/b18_dat.nxs", "resources/mappings"],
                "tests/data/b18_dat.xdi",
                id="B18 dat",
            ),
            pytest.param(
                ["tests/data/b18_dat.nxs", "resources/mappings/dls_b18_dat.yaml"],
                "tests/data/b18_dat.xdi",
                id="B18 dat mapping specified",
            ),
            pytest.param(
                ["tests/data/b18_nxs.nxs", "resources/mappings"],
                "tests/data/b18_nxs.xdi",
                id="B18 nxs",
            ),
            pytest.param(
                ["tests/data/b18_nxs.nxs", "resources/mappings/dls_b18_nxs.yaml"],
                "tests/data/b18_nxs.xdi",
                id="B18 nxs mapping specified",
            ),
            pytest.param(
                [
                    "tests/data/b18_dat.nxs",
                    "resources/mappings",
                    "--extra=tests/data/extra.yaml",
                ],
                "tests/data/extra.xdi",
                id="Extra metadata",
            ),
        ],
    )
    def test_main(
        self, arguments: list[str], expected_filepath: str, tmp_path: Path
    ) -> None:
        xdi_filepath = tmp_path / "out.xdi"
        sys.argv = ["nxxas_to_xdi", *arguments, f"--xdi={xdi_filepath}"]
        main()
        assert os.path.exists(xdi_filepath), os.listdir(tmp_path)
        with open(xdi_filepath) as actual, open(expected_filepath) as expected:
            assert actual.read() == expected.read()

    def test_main_no_mapping(self, tmp_path: Path) -> None:
        sys.argv = [
            "nxxas_to_xdi",
            "tests/data/b18_dat.nxs",
            str(tmp_path),
            f"--xdi={tmp_path}/out.xdi",
        ]
        match = f"No mappings in {tmp_path} are valid for provided data."
        with pytest.raises(ValueError, match=match):
            main()
