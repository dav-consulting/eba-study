import os, json, time, re
from util import (
    _PARSED_FILES_PATH,
    load_jsonl,
    update_eba_evaluations_column,
    create_eba_evaluations_column,
    get_file_id,
)


def main():
    """ Update eba evaluations with auxillary information. """
    total_file_cnt, start_aux_cnt, end_aux_cnt = 0, 0, 0
    end_author_cnt = 0
    silence_updates = True
    create_eba_evaluations_column("authors")
    create_eba_evaluations_column("commisioned_by")
    create_eba_evaluations_column("publ_date")
    create_eba_evaluations_column("publisher")
    create_eba_evaluations_column("art_no")
    for file_idx, file in enumerate(_PARSED_FILES_PATH.iterdir()):
        if file.name.endswith("_content.json"):
            found_aux_page = False
            total_file_cnt += 1
            file_id = get_file_id(file)
            print(file_id)
            data = load_jsonl(file)
            aux_text = ""
            for row_id, content in enumerate(data):
                text = content["text"]
                start_aux = re.match("Authors:", text)
                if start_aux:
                    start_aux_cnt += 1
                    found_aux_page = True

                end_aux = re.search("This publication can be downloaded", text)
                if end_aux:
                    end_aux_cnt += 1

                if found_aux_page:
                    aux_text = "{} {}".format(aux_text, text).strip()

                if found_aux_page and end_aux:
                    print(aux_text)
                    end_author_text = re.search(
                        "The views and interpretations", aux_text
                    )
                    author_str = aux_text[8 : end_author_text.span()[0]].strip()
                    author_str = author_str.replace(" and ", ", ")
                    if author_str:
                        update_eba_evaluations_column(
                            "authors",
                            author_str,
                            primary_key=file_id,
                            silence=silence_updates,
                        )

                    start_comm_text = re.search("Commissioned by", aux_text)
                    end_comm_text = re.search("Copyright:", aux_text)
                    if start_comm_text and end_comm_text:
                        comm_str = aux_text[
                            start_comm_text.span()[1] : end_comm_text.span()[0]
                        ].strip()
                        update_eba_evaluations_column(
                            "commisioned_by",
                            comm_str,
                            primary_key=file_id,
                            silence=silence_updates,
                        )

                    start_date_text = re.search("Date of final report:", aux_text)
                    end_date_text = re.search("Published by|Printed by", aux_text)
                    if start_date_text and end_date_text:
                        date_str = aux_text[
                            start_date_text.span()[1] : end_date_text.span()[0]
                        ].strip()
                        update_eba_evaluations_column(
                            "publ_date",
                            date_str,
                            primary_key=file_id,
                            silence=silence_updates,
                        )

                    end_publisher_text = re.search("Art. no.", aux_text)
                    if end_publisher_text:
                        publisher_str = aux_text[
                            end_date_text.span()[1] : end_publisher_text.span()[0]
                        ].strip()
                        update_eba_evaluations_column(
                            "publisher",
                            publisher_str,
                            primary_key=file_id,
                            silence=silence_updates,
                        )

                    end_aux_text = re.search(
                        "This publication can be downloaded", aux_text
                    )
                    if end_aux_text:
                        art_no_str = aux_text[
                            end_publisher_text.span()[1] : end_aux_text.span()[0]
                        ].strip()
                        update_eba_evaluations_column(
                            "art_no",
                            art_no_str,
                            primary_key=file_id,
                            silence=silence_updates,
                        )

                    if end_author_text:
                        end_author_cnt += 1
                    break

    print(total_file_cnt, start_aux_cnt, end_aux_cnt, end_author_cnt)


if __name__ == "__main__":
    # python -m q0.main
    main()
