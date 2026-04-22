from pydantic import BaseModel, Field


class StartsWith(BaseModel):
    """Class defining identifying Dataset for NXxas file."""

    path: str = Field(description="Path to an HDF5 Dataset in the NXxas file.")
    value: str = Field(
        description=(
            "If the Dataset is a string and starts with this value, it will use this "
            "mapping."
        ),
    )


class XdiColumn(BaseModel):
    """Class defining how to extract an XDI data column from NXxas."""

    name: str = Field(
        description=(
            "Name of the column to use in the XDI fields section and header row of the "
            "table."
        ),
    )
    path: str = Field(description="HDF5 path to the column data.")


class XdiField(BaseModel):
    """Class defining how to extract and format the value of an XDI field from NXxas."""

    format_str: str = Field(
        default="{}",
        description=(
            "The value for the XDI field will be this string, formatted with "
            "positional arguments from `paths`."
        ),
    )
    paths: list[str] = Field(
        min_length=1,
        description=(
            "Ordered list of HDF5 Dataset paths, values of which will be used to "
            "format `format_str`."
        ),
    )


class XdiModel(BaseModel):
    """Class defining how to map from a non-generic NXxas file to XDI."""

    starts_with: StartsWith = Field(
        description=(
            "Identifies whether this mapping can be applied to a input NXxas file by "
            "checking if a dataset starts with a specific string."
        ),
    )
    extra_columns: list[XdiColumn] = Field(
        description=(
            "List of data columns beyond the required energy, incoming_beam, and "
            "absorbed_beam."
        ),
    )
    fields: dict[str, str | XdiField] = Field(
        description=(
            "Mapping from XDI field names to either a static value (str) or XdiField "
            "object identifying which hdf5 datasets define the value."
        ),
    )
