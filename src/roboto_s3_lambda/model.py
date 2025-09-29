import dataclasses
import typing


@dataclasses.dataclass(frozen=True)
class RobotoCreateDatasetArgs:
    description: str | None
    device_id: str | None
    metadata: dict[str, typing.Any] | None
    name: str | None
    tags: list[str] | None


@dataclasses.dataclass(frozen=True)
class RobotoImportFileArgs:
    description: str | None
    device_id: str | None
    metadata: dict[str, typing.Any] | None
    relative_path: str
    tags: list[str] | None