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


@dataclasses.dataclass(frozen=True)
class RobotoSessionArgs:
    """
    The Session an imported file belongs to, e.g. one robot run that is uploaded as many files.

    The session belongs to the dataset's device (`RobotoCreateDatasetArgs.device_id`, which must be set). Every file
    whose record yields the same device and session `name` is added to the same session, however many Lambda
    invocations import them and in whatever order they run.
    """

    name: str
    """Your identifier for the session, unique per device, e.g. a run, flight or drive ID (1 to 120 characters)."""

    inactivity_minutes: int | None = None
    """
    Roboto marks the session complete once this many minutes (1 to 10080, i.e. 7 days) pass without a new file
    being added, and reopens it if a later file arrives. Once a session is complete and every ingestable file in it
    is ingested, Roboto emits a `session.ingested` event, which a trigger can run an action on. Choose a value longer
    than the longest gap between two consecutive uploads of one session. None leaves the session's completion policy
    as it is: a new session takes the org's default policy, if the org has one, and otherwise completes only when
    someone marks it complete.
    """
