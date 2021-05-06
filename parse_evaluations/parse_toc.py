import json, re
from pathlib import Path
from util import (
    _PARSED_FILES_PATH,
    load_jsonl,
    dump_jsonl,
    files_to_exclude,
)
from util import (
    _EXECUTIVE_SUMMARY_VARIATIONS,
    _CONCLUDING_SECTION_VARIATIONS,
    _RECOMMENDATION_SECTION_VARIATIONS,
    _DAC_CRITERIA_VARIATIONS,
    _TERMS_OF_REFERENCE,
    _INTRODUCTION_VARIATIONS,
)


def parse_toc(file_path):
    """ Parsing table of contents for deriving categories - creates a "category" dict key 
    in meta files which denotes whether entry belongs to a specific category e.g. Executive Summary, 
    Conclusions, of Terms of Reference...

    Method also outputs some summary stats in the summary folder."""
    file_path = Path(file_path)
    summary_stats = dict()
    cnt_parsed_files = 0
    invalid_file_ids = files_to_exclude()  # Files to not include in final report

    for file in sorted(file_path.iterdir()):
        if file.name.endswith("_meta.json"):  # and "2020:19" in file.name:
            file_id = file.name.replace("_meta.json", "")
            toc = load_jsonl(file)
            executive_summary, concluding_sections, dac, terms_of_reference = (
                None,
                None,
                None,
                None,
            )
            if toc:
                summary_stats[file_id] = dict()
            else:
                print("Table of contents not found for: ", file_id)

            parent_categories = {}
            for t_id, c in enumerate(toc):
                if c["type"] == "toc":
                    c["category"] = []
                    if c["section_type"] == "Main":
                        # print(c.get("section"), c["text"], dac_criteria_section_num)
                        for dac_key, dac_val in _DAC_CRITERIA_VARIATIONS.items():
                            dac_criteria = next(
                                (
                                    (idx, var)
                                    for idx, var in enumerate(dac_val)
                                    if var in c["text"].lower()
                                ),
                                None,
                            )
                            if dac_criteria:
                                if c.get("section"):
                                    parent_categories.setdefault(
                                        c.get("section"), [dac_key]
                                    ).append(dac_key)
                                c["category"].append(dac_key)
                                summary_stats[file_id][dac_key] = True

                        # Identify intro section
                        introduction_section = next(
                            (
                                (idx, var)
                                for idx, var in enumerate(_INTRODUCTION_VARIATIONS)
                                if var in c["text"].lower()
                            ),
                            None,
                        )
                        if introduction_section:
                            if c.get("section"):
                                parent_categories.setdefault(
                                    c.get("section"), ["introduction"]
                                ).append("introduction")
                                # parent_categories[c.get("section")] = "recommendations"
                            c["category"].append("introduction")
                            summary_stats[file_id]["introduction"] = True

                        # Identify recommendation section
                        recommendation_section = next(
                            (
                                (idx, var)
                                for idx, var in enumerate(
                                    _RECOMMENDATION_SECTION_VARIATIONS
                                )
                                if var in c["text"].lower()
                            ),
                            None,
                        )
                        if recommendation_section:
                            if c.get("section"):
                                parent_categories.setdefault(
                                    c.get("section"), ["recommendations"]
                                ).append("recommendations")
                                # parent_categories[c.get("section")] = "recommendations"
                            c["category"].append("recommendations")
                            summary_stats[file_id]["recommendations"] = True

                        # Identify Executive summary
                        executive_summary = next(
                            (
                                (idx, var)
                                for idx, var in enumerate(_EXECUTIVE_SUMMARY_VARIATIONS)
                                if var in c["text"].lower()
                            ),
                            None,
                        )
                        if not summary_stats[file_id].get("executive_summary"):
                            if executive_summary:
                                c["category"].append("executive_summary")
                                summary_stats[file_id]["executive_summary"] = True
                            elif "Summary" in c["text"] and not summary_stats[
                                file_id
                            ].get("introduction"):
                                c["category"].append("executive_summary")
                                summary_stats[file_id]["executive_summary"] = True

                        # Identify concluding sections
                        concluding_sections = next(
                            (
                                (idx, var)
                                for idx, var in enumerate(
                                    _CONCLUDING_SECTION_VARIATIONS
                                )
                                if var in c["text"].lower()
                            ),
                            None,
                        )
                        if concluding_sections:
                            parent_categories.setdefault(
                                c.get("section"), ["concluding_sections"]
                            ).append("concluding_sections")
                            c["category"].append("concluding_sections")
                            summary_stats[file_id]["concluding_sections"] = True

                        # if current section is a subsection then we add the parent section category
                        if parent_categories.get(c.get("parent_section")):
                            c["category"] += parent_categories.get(
                                c.get("parent_section")
                            )
                        c["category"] = list(set(c["category"]))

                    else:
                        terms_of_reference = next(
                            (
                                (idx, var)
                                for idx, var in enumerate(_TERMS_OF_REFERENCE)
                                if var in c["text"].lower()
                            ),
                            None,
                        )
                        if terms_of_reference:
                            c["category"] = ["terms_of_reference"]
                            summary_stats[file_id]["terms_of_reference"] = True
            print(file_id)
            for r in toc:
                print(r)
            print("")
            dump_jsonl(toc, file)

            ## Adds category also to content file
            prev_content_idx = None
            content_filename = file_id + "_content.json"
            contents = load_jsonl(_PARSED_FILES_PATH / content_filename)
            for c in toc[::-1]:
                if c["category"]:
                    content_idx = c["toc_match"]["content_idx"]
                    for content in contents[content_idx:prev_content_idx]:
                        content["category"] = c["category"]
                prev_content_idx = c["toc_match"]["content_idx"]

            dump_jsonl(contents, _PARSED_FILES_PATH / content_filename)
        elif file.name.endswith("_content.json"):
            cnt_parsed_files += 1

    # Write results data
    with open(_PARSED_FILES_PATH / "summary/parsing_meta_results.json", "w") as f:
        f.write(json.dumps(summary_stats))

    # Write results data
    with open(_PARSED_FILES_PATH / "summary/parsing_toc_summary.json", "w") as f:
        executive_summary_cnt = sum(
            [
                v.get("executive_summary", False)
                for k, v in summary_stats.items()
                if k not in invalid_file_ids
            ]
        )
        introduction_cnt = sum(
            [
                v.get("introduction", False)
                for k, v in summary_stats.items()
                if k not in invalid_file_ids
            ]
        )
        concluding_sections_cnt = sum(
            [
                v.get("concluding_sections", False)
                for k, v in summary_stats.items()
                if k not in invalid_file_ids
            ]
        )
        terms_of_reference_cnt = sum(
            [
                v.get("terms_of_reference", False)
                for k, v in summary_stats.items()
                if k not in invalid_file_ids
            ]
        )
        recommendations_cnt = sum(
            [
                v.get("recommendations", False)
                for k, v in summary_stats.items()
                if k not in invalid_file_ids
            ]
        )
        stats = {
            "introduction_cnt": introduction_cnt,
            "executive_summary_cnt": executive_summary_cnt,
            "recommendations_cnt": recommendations_cnt,
            "terms_of_reference_cnt": terms_of_reference_cnt,
            "concluding_sections_cnt": concluding_sections_cnt,
        }
        for dac_key, _ in _DAC_CRITERIA_VARIATIONS.items():
            stats[dac_key + "_cnt"] = sum(
                [
                    v.get(dac_key, False)
                    for k, v in summary_stats.items()
                    if k not in invalid_file_ids
                ]
            )
        stats["total_toc_cnt"] = len(
            [k for k, v in summary_stats.items() if k not in invalid_file_ids]
        )
        stats["total_valid_files"] = cnt_parsed_files - len(invalid_file_ids)
        stats["total_cnt_parsed_files"] = cnt_parsed_files
        print(invalid_file_ids)
        f.write(json.dumps(stats))


def main():
    """ Command line method for parsing all table of contents in a directory """
    # Run from project level
    # python -m parse_evaluations.parse_toc

    parse_toc(_PARSED_FILES_PATH)
    print("Success parsing table of contents!")


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    # python -m parse_evaluations.parse_toc
    main()
