from argparse import ArgumentParser
from pathlib import Path

from nexuscreator_container.xdi_mapper import XdiMapper


def main() -> None:
    """Entrypoint for nxxas_to_xdi."""
    parser = ArgumentParser("nxxas_to_xdi")
    parser.add_argument("nxxas", type=Path, help="NXxas file to read.")
    parser.add_argument(
        "mapping",
        type=Path,
        help=(
            "YAML file or directory containing YAML files mapping from XDI field to "
            "NXxas paths."
        ),
    )
    parser.add_argument(
        "-x",
        "--xdi",
        type=Path,
        help=(
            "Filepath to write XDI to. Defaults to nxxas path with .nxs replaced with "
            ".xdi."
        ),
    )
    parser.add_argument(
        "-e", "--extra", type=Path, help="YAML file containing extra fields to apply."
    )
    args = parser.parse_args()
    mapper = XdiMapper(
        h5_filepath=args.nxxas, mappings_path=args.mapping, extra_path=args.extra
    )
    mapper.write(filepath=args.xdi or args.nxxas.removesuffix(".nxs") + ".xdi")
