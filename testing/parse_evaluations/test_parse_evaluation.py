import os, json
from util import _PARSED_FILES_PATH, _PROJECT_PATH, db_connect, load_jsonl


def test():
    """ Method for testing parsing and verifying parsing results are coherent after editing parsing methods. """
    # parse settings
    granularity = True
    font_size_remainder = 1
    pageNumberStyleMatch = "rough"  # exact: font and size must be equal; rough:  size must be equal, font must almost match; else: match on font size only

    # list of file locations, can be urls or file paths.
    file_locations = [
        # "https://www.sida.se/contentassets/cfb177e7869f412ab60e1c00d425f800/15254.pdf",
        # "https://www.sida.se/contentassets/671f6c7178b14c6cb158915e9bf3ad32/15366.pdf",
        # "https://www.sida.se/contentassets/6b9f34eab0f0444088437f7dab68ac57/de2018_7_62135en.pdf",
        # "https://www.sida.se/contentassets/62da777630074bd786cfa161a7f0cab1/15492.pdf",
        # "https://www.sida.se/contentassets/cb4bf78c03bd4e929b32fd5f22f67447/18292.pdf",
        # "https://www.sida.se/contentassets/1c9953d8f28945bd9d07a225902f2197/de2020_5_62278en.pdf",
        # "https://www.sida.se/contentassets/d4506e4823f74f0f826fed1070d687ee/15409.pdf",
        # "https://www.sida.se/contentassets/ef045264a9e94e9ca451832403ac98ab/15290.pdf",
        # "https://www.sida.se/contentassets/2f27ee31a9e5498d8ac85f6635d5cc16/15188.pdf",
    ]

    # Read test data
    try:
        with open(
            os.path.join(
                _PROJECT_PATH, "parse_evaluations/_temp_dev/parsing_results.json"
            ),
            "r",
        ) as f:
            test_vals = json.loads(f.read())
    except:
        test_vals = {}

    results = {}
    for _, url in enumerate(file_locations):
        filename = url.split("/")[-1]
        print("")
        print("retrieve:", filename)
        print("granularity: ", granularity)

        file_path = os.path.join(
            _PROJECT_PATH, "parse_evaluations/_temp_dev/docs/", filename
        )
        if not os.path.exists(file_path):
            if "https:" in url:
                print(file_path)
                pdf = request.urlretrieve(url, file_path)
            else:
                pdf = [os.path.join(_PROJECT_PATH, url)]
            pdoc = ParseDoc(
                pdf[0],
                font_size_remainder=font_size_remainder,
                granularity=granularity,
                pageNumberStyleMatch=pageNumberStyleMatch,
            )
        else:
            pdoc = ParseDoc(
                file_path,
                font_size_remainder=font_size_remainder,
                granularity=granularity,
                pageNumberStyleMatch=pageNumberStyleMatch,
            )

        font_counts, styles, page_numbers = pdoc.fonts_and_page_numbers()
        size_tags = pdoc.font_tags()
        footnotes = pdoc.get_footnotes()
        parsed_content = pdoc.parse_content()
        pdoc.extract_table_of_contents()
        toc = pdoc.match_table_of_contents()
        toc_scores = []
        for t in toc:
            show_keys = ["text", "page_number", "parent_section"]
            print(
                t["toc_match"]["token_sort_ratio"],
                " / ",
                t["toc_match"]["content_idx"],
                ": ",
                {key: t[key] for key in show_keys},
            )
            toc_scores.append(t["toc_match"]["token_sort_ratio"])

        pdoc.write_files(
            output_path=os.path.join(
                _PROJECT_PATH, "parse_evaluations/_temp_dev/results/"
            )
        )

        assert toc, "No table of contents found!"

        results[filename] = {
            "font_counts": int(len(font_counts)),
            "styles": int(len(styles)),
            "page_numbers": int(len(page_numbers)),
            "size_tag": int(len(size_tags)),
            "footnotes": int(len(footnotes)),
            "parsed_content": int(len(parsed_content)),
            "toc_scores": toc_scores,
        }

        if filename in test_vals.keys():
            for k, v in test_vals[filename].items():
                assert v == test_vals[filename][k]
        else:
            print("New file {}!".format(filename))

        print("font_counts:", int(len(font_counts)))
        print("styles:", int(len(styles)))
        print("page_numbers:", int(len(page_numbers)))
        print("size_tag:", int(len(size_tags)))
        print("footnotes:", int(len(footnotes)))
        print("parsed_content:", int(len(parsed_content)))

    # Write test data
    with open(
        os.path.join(
            _PROJECT_PATH, "parse_evaluations/_temp_dev/results/parsing_results.json"
        ),
        "w",
    ) as f:
        f.write(json.dumps(results))


def test1():
    conn, cur = db_connect()
    cur.execute(
        "SELECT _id, title FROM eba_evaluations WHERE eba_match_title IS NOT NULL"
    )
    rows = cur.fetchall()
    ll = []

    for row in rows:
        toc = load_jsonl(_PARSED_FILES_PATH / f"{row[0]}_meta.json")
        print(toc)
        if len(toc) == 0:
            ll.append(row[0])
    print(ll)
    pass


if __name__ == "__main__":
    test1()
