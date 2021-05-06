import os, json, time
import click
from spacy.matcher import Matcher
from util import (
    load_spacy_docbin_folder,
    load_spacy_model,
    get_model_version_path,
    update_eba_evaluations_column,
    create_eba_evaluations_column,
    eba_2017_comparison,
    _DAC_CRITERIA_VARIATIONS,
)


@click.command()
@click.option(
    "--dac_criteria",
    default="sustainability",
    prompt="Input DAC criteria to assess.",
    type=click.Choice(
        ["sustainability", "relevance", "impacts", "effectiveness", "efficiency"]
    ),
    # case_sensitive=False,
)
@click.option(
    "--model_version",
    default="-1",
    prompt="Which model version should be used?",
    type=int,
    # case_sensitive=False,
)
def main(dac_criteria, model_version):
    version_path, model_version = get_model_version_path(model_version=model_version)
    nlp = load_spacy_model(version_path / "meta.json")
    matcher_dac = Matcher(nlp.vocab)
    patterns = [[{"LOWER": val}] for val in _DAC_CRITERIA_VARIATIONS[dac_criteria]]
    matcher_dac.add(dac_criteria, None, *patterns)

    print(f"Loading model version: {model_version}")
    if dac_criteria == "sustainability":
        column_name = "q23"
    else:
        column_name = "q23_" + dac_criteria
    create_eba_evaluations_column(column_name)
    update_eba_evaluations_column(
        column_name=column_name, update_value="nej",
    )
    for file_path, docs, nlp in load_spacy_docbin_folder(model_version, nlp=nlp):
        print(f"Processing: {file_path.name}")
        for doc in docs:
            if "executive_summary" not in doc._.props.get("category", []):
                continue

            matches = matcher_dac(doc)
            if len(matches) > 0:
                update_eba_evaluations_column(
                    column_name=column_name,
                    update_value="ja",
                    primary_key=file_path.name.replace("_content.bin", ""),
                )
                break

    eba_2017_comparison("I_sammanfattning", "q23")


if __name__ == "__main__":
    main()
