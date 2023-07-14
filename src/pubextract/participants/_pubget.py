import json
import logging
from pathlib import Path

import pandas as pd
import pubget

from pubextract import _utils
from pubextract.participants import _information_extraction, _summarization

_STEP_NAME = "extract_participants_demographics"
_STEP_DESCRIPTION = (
    "Extract participants count, sex and age from studies' text."
)
_LOG = logging.getLogger(_STEP_NAME)


def _iter_labelbuddy_docs(labelbuddy_dir):
    for batch_file in sorted(labelbuddy_dir.glob("documents_*.jsonl")):
        with open(batch_file, "r", encoding="UTF-8") as stream:
            batch = list(map(json.loads, stream))
        yield from batch


def _extract_from_labelbuddy_dir(labelbuddy_dir, output_dir=None):
    if output_dir is None:
        output_dir = labelbuddy_dir.with_name(
            labelbuddy_dir.name.replace(
                "_labelbuddyData", "_participantsDemographics"
            )
        )
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    status = _utils.check_steps_status(labelbuddy_dir, output_dir, _STEP_NAME)
    if not status["need_run"]:
        return output_dir, 0
    _LOG.info(f"Extracting participant demographics to {output_dir}")
    annotations, full_extractions, summaries = [], [], []
    for (
        doc_annotations,
        participants_info,
    ) in _information_extraction.annotate_labelbuddy_docs(
        _iter_labelbuddy_docs(labelbuddy_dir)
    ):
        annotations.append(doc_annotations)
        doc_extraction = json.loads(_summarization.to_json(participants_info))
        full_extractions.append(doc_extraction)
        summary = {"pmcid": doc_annotations["metadata"]["pmcid"]}
        summary.update(
            {
                k: doc_extraction[k]
                for k in (
                    "count",
                    "females_count",
                    "males_count",
                    "age_mean",
                )
            }
        )
        if doc_extraction.get("age_range") is not None:
            summary["age_range_start"] = doc_extraction["age_range"][0]
            summary["age_range_end"] = doc_extraction["age_range"][1]
        else:
            summary["age_range_start"] = None
            summary["age_range_end"] = None
        summaries.append(summary)
    pd.DataFrame(summaries).to_csv(
        output_dir / "participants_summaries.csv", index=False
    )
    with open(
        output_dir / "participants_labelbuddy_annotations.jsonl",
        "w",
        encoding="UTF-8",
    ) as stream:
        for doc_annotations in annotations:
            stream.write(json.dumps(doc_annotations))
            stream.write("\n")
    with open(
        output_dir / "participants_full_extracted_info.jsonl",
        "w",
        encoding="UTF-8",
    ) as stream:
        for doc_extraction in full_extractions:
            stream.write(json.dumps(doc_extraction))
            stream.write("\n")
    is_complete = bool(status["previous_step_complete"])
    _utils.write_info(output_dir, name=_STEP_NAME, is_complete=is_complete)
    _LOG.info(f"Done extracting participant demographics to {output_dir}")
    return output_dir, 0


class DemographicsStep:
    name = _STEP_NAME
    short_description = _STEP_DESCRIPTION

    def edit_argument_parser(self, argument_parser) -> None:
        argument_parser.add_argument(
            "--demographics",
            action="store_true",
            help="Extract demographic information about "
            "each study's participants.",
        )

    def run(self, args, previous_steps_output):
        if not args.demographics:
            return None, 0
        labelbuddy_dir = previous_steps_output.get("extract_labelbuddy_data")
        if labelbuddy_dir is None:
            labelbuddy_dir, _ = pubget.make_labelbuddy_documents(
                previous_steps_output["extract_data"]
            )
        return _extract_from_labelbuddy_dir(labelbuddy_dir)


class DemographicsCommand:
    name = _STEP_NAME
    short_description = _STEP_DESCRIPTION

    def edit_argument_parser(self, argument_parser) -> None:
        argument_parser.add_argument(
            "labelbuddy_dir",
            help="Directory containing articles in labelbuddy format."
            "It is a directory created by pubget with the '--labelbuddy' "
            "option, whose name ends with 'labelbuddyData'.",
        )

    def run(self, args):
        return _extract_from_labelbuddy_dir(Path(args.labelbuddy_dir))[1]


def get_pubget_actions():
    return {
        "pipeline_steps": [DemographicsStep()],
        "commands": [DemographicsCommand()],
    }
