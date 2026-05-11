from importlib.metadata import version
from pathlib import Path
from typing import Any

from h5py import File
import yaml

from nexuscreator_container.models import XdiField, XdiModel


class XdiMapper:
    """Control object for loading from NXxas and writing to XDI."""

    def __init__(
        self,
        h5_filepath: Path,
        mappings_path: Path,
        extra_path: Path | None,
    ) -> None:
        """
        Args:
            h5_filepath (Path): Path to NXxas format data to read.
            mappings_path (Path):
                Path to either a single YAML mapping file, or a directory of them.
            extra_path (Path | None):
                Path to YAML file defining static values for XDI fields to use in
                addition to the dynamically extracted values.

        Raises:
            ValueError:
                If `mappings_path` does not define a valid mapping for `h5_filepath`.
        """
        self.h5_filepath = h5_filepath
        self.mappings_path = mappings_path
        self.extra_path = extra_path
        self.version = version("nexuscreator_container")

    @classmethod
    def open(
        cls,
        h5_filepath: Path,
        mappings_path: Path,
        extra_path: Path | None,
    ) -> "XdiMapper":
        return cls(
            h5_filepath=h5_filepath,
            mappings_path=mappings_path,
            extra_path=extra_path,
        )

    def __enter__(self) -> "XdiMapper":
        self.column_count = 0
        self.columns = {}
        self.h5_file = File(name=self.h5_filepath)
        if Path(self.mappings_path).is_dir():
            for filepath in sorted(Path(self.mappings_path).glob("*.yaml")):
                try:
                    self._init_mapping(filepath, extra_path=self.extra_path)
                    return self
                except ValueError:
                    pass
            self.h5_file.close()
            msg = f"No mappings in {self.mappings_path} are valid for provided data."
            raise ValueError(msg)
        else:
            self._init_mapping(filepath=self.mappings_path, extra_path=self.extra_path)
        return self

    def __exit__(self, *_) -> None:
        self.h5_file.close()

    def _init_mapping(self, filepath: Path, extra_path: Path | None) -> None:
        """
        Loads YAML from `filepath`, verifies it is valid for `self.h5_file` and
        optionally loads static fields from `extra_path`.

        Args:
            filepath (Path): Path to a single YAML mapping file.
            extra_path (Path | None):
                Path to YAML file defining static values for XDI fields to use in
                addition to the dynamically extracted values.
        Raises:
            ValueError:
                If `filepath` does not define a valid mapping for `self.h5_file`.
        """
        with open(filepath) as f:
            mapping = XdiModel(**yaml.safe_load(f))

        value = self._get_value(mapping.starts_with.path)
        if isinstance(value, str) and value.startswith(mapping.starts_with.value):
            if extra_path is not None:
                with open(extra_path) as e:
                    updates = yaml.safe_load(e) or {}
                    mapping.fields.update(**updates)

            self.mapping = mapping
            return

        raise ValueError(f"Mapping {filepath} is not valid for provided data.")

    def _get_value(self, path: str) -> Any:
        """
        Extract and format a metadata value from `self.h5_file`, including units if
        defined.

        Args:
            path (str): Path to HDF5 Dataset.

        Returns:
            Any:
                Value associated with path. For valid metadata may be float, int, str
                (in which case we will format it so any newlines start with "# " so they
                are valid XDI). Returns None if data is a non-str tensor (i.e. actual
                data rather than metadata). In principle a h5py might return several
                types, however if it is not one of the prior expected cases this
                function may fail.
        """
        value = self.h5_file.get(path)
        if value is not None:
            units = value.attrs.get("units")
            if value.size == 1:
                value = value[(0,) * value.ndim]
                if isinstance(value, bytes):
                    value = value.decode()
                    if "\n" in value:  # e.g. newline delimited XML
                        value = "\n# " + value.rstrip("\n").replace("\n", "\n# ")
            else:
                try:
                    value = "\n# ".join(v.decode() for v in value)
                except AttributeError:
                    return None

            if units is not None:
                value = f"{value} {units}"

        return value

    def _extract_column(self, name: str, path: str) -> None:
        """
        Extract `name` from `self.h5_file`, store the data and write the corresponding
        XDI metadata field.

        Args:
            name (str):
                Name of the column to use in the XDI fields section and header row of
                the table.
            path (str): HDF5 path to the column data.
        """
        dataset = self.h5_file.get(path)
        if dataset is not None:
            self.column_count += 1
            self.xdi_file.write(f"# Column.{self.column_count}: {name}\n")
            self.columns[name] = dataset

    def _extract_field(self, name: str | None, xdi_field: str | XdiField) -> None:
        """
        Extract the metadata defined by `xdi_field` and write it against the label
        `name`.

        Args:
            name (str | None):
                Name of the column to use in the XDI fields section and header row of
                the table. May be None for the comments section, where multiple lines
                can be written without an explicit label per line.
            xdi_field (str | XdiField):
                Object defining how to extract and format the value of an XDI field from
                NXxas.
        """
        formatted_name = ""
        if name is not None:
            formatted_name = f"{name}: "

        if isinstance(xdi_field, str):
            self.xdi_file.write(f"# {formatted_name}{xdi_field}\n")
        else:
            values = []
            for path in xdi_field.paths:
                value = self._get_value(path)
                if value is not None:
                    values.append(value)

            if values:
                formatted_value = xdi_field.format_str.format(*values)
                self.xdi_file.write(f"# {formatted_name}{formatted_value}\n")

    def write(self, filepath: Path) -> None:
        """Convert all (meta)data to XDI format and write to file.

        Args:
            filepath (Path): Output XDI filepath.
        """
        with open(filepath, "w+") as self.xdi_file:
            self.xdi_file.write(f"# XDI/1.0 nexuscreator_container/{self.version}\n")
            self._extract_column(name="energy", path="/entry/data/energy")
            self._extract_column(name="i0", path="/entry/data/incoming_beam")
            mode = self.h5_file.get("/entry/data/mode")[()]
            mode_short = mode.decode()[:5].lower()
            self._extract_column(
                name=f"i{mode_short}", path="/entry/data/absorbed_beam"
            )

            for column in self.mapping.extra_columns:
                self._extract_column(name=column.name, path=column.path)

            for name, xdi_field in self.mapping.fields.items():
                self._extract_field(name=name, xdi_field=xdi_field)

            self.xdi_file.write("# ///\n")
            for key in self.h5_file.get("/entry/metadata").keys():
                if key == "general_notes":
                    name = None
                else:
                    name = key.removeprefix("nexus_entry1_").removeprefix("general_")
                    name = name.replace("_", " ")
                field = XdiField(paths=[f"/entry/metadata/{key}"])
                self._extract_field(name=name, xdi_field=field)

            self.xdi_file.write("# ---\n")
            self.xdi_file.write(f"# {' '.join(self.columns.keys())}\n")
            for row in zip(*self.columns.values(), strict=True):
                self.xdi_file.write(f"  {' '.join([str(v) for v in row])}\n")
