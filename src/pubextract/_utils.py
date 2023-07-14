"""Helpers for making pubget plugins.

They are copied from pubget._utils; if some of them are ever exposed in
pubget's public API they should be removed from this module and imported from
pubget.
"""
from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Any, Dict, Union, Optional


def assert_exists(path: Path) -> None:
    """raise a FileNotFoundError if path doesn't exist."""
    path.resolve(strict=True)


def check_steps_status(
    previous_step_dir: Optional[Path], current_step_dir: Path, logger_name: str
) -> Dict[str, Union[None, bool, str]]:
    """Check whethere previous and current processing steps are complete.

    Logs a warning if the previous step is incomplete and a message about
    skipping the current step if it is already complete.

    Returns a dict with completion status of both steps. "need_run" is true if
    the current step is not already complete. If `previous_step_dir` is `None`
    it means there is no previous step (the current step is download, the
    beginning of the pipeline).
    """
    result: Dict[str, Union[None, bool, str]] = dict.fromkeys(
        [
            "previous_step_complete",
            "current_step_complete",
            "previous_step_name",
            "current_step_name",
            "need_run",
        ]
    )
    if previous_step_dir is not None:
        assert_exists(previous_step_dir)
        previous_info_file = previous_step_dir.joinpath("info.json")
        if previous_info_file.is_file():
            previous_info = json.loads(previous_info_file.read_text("utf-8"))
            result["previous_step_complete"] = previous_info["is_complete"]
            result["previous_step_name"] = previous_info.get(
                "name", previous_step_dir.name
            )
        else:
            result["previous_step_complete"] = False
            result["previous_step_name"] = previous_step_dir.name
    current_info_file = current_step_dir.joinpath("info.json")
    if current_info_file.is_file():
        current_info = json.loads(current_info_file.read_text("utf-8"))
        result["current_step_complete"] = current_info["is_complete"]
        result["current_step_name"] = current_info.get(
            "name", current_step_dir.name
        )
    else:
        result["current_step_complete"] = False
        result["current_step_name"] = current_step_dir.name
    logger = logging.getLogger(logger_name)
    if result["current_step_complete"]:
        logger.info(
            f"Nothing to do: current processing step "
            f"'{result['current_step_name']}' already completed "
            f"in {current_step_dir}"
        )
        result["need_run"] = False
        return result
    if previous_step_dir is not None and not result["previous_step_complete"]:
        logger.warning(
            f"Previous processing step '{result['previous_step_name']}' "
            "was not completed: not all the articles matching the query "
            "will be processed."
        )
    result["need_run"] = True
    return result


def write_info(
    output_dir: Path, *, name: str, is_complete: bool, **info: Any
) -> Path:
    """Write info about a processing step to its output directory."""
    info["name"] = name
    info["is_complete"] = is_complete
    info["date"] = datetime.now().isoformat()
    info_file = output_dir.joinpath("info.json")
    info_file.write_text(json.dumps(info), "utf-8")
    return info_file
