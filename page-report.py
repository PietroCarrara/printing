import argparse
from functools import reduce
import sys

import pymupdf

global args


def main():
    global args

    reports = {}

    with pymupdf.open(args["input-file.pdf"]) as doc:
        i = 0
        for page in doc:
            width = page.bound().width
            height = page.bound().height
            key = f"{width}x{height}"

            if key not in reports:
                reports[key] = {
                    "count": 0,
                    "width": width,
                    "height": height,
                    "pages": [],
                }

            reports[key]["count"] += 1
            reports[key]["pages"].append(f"{i + 1}")
            i += 1

    total_pages = i
    biggest_group_key, biggest_group = max(
        reports.items(), key=lambda kv: kv[1]["count"]
    )

    print("# Main group:")
    print_group(biggest_group, args["all"])

    print("# Outliers:")
    for key in reports:
        if key != biggest_group_key:
            print_group(reports[key], True)


def print_group(group, include_pages: bool):
    width = point2cm(group["width"])
    height = point2cm(group["height"])

    print(f"{width:.2f}x{height:.2f} cm: {group["count"]} pages", end="")

    if include_pages:
        print(f" ({",".join(group["pages"])})")
    else:
        print()


def cli_args():
    cli = argparse.ArgumentParser(
        prog="page-report",
        description="Print a report on page sizes of a PDF",
    )
    cli.add_argument(
        "input-file.pdf",
    )
    cli.add_argument(
        "--all",
        action="store_true",
        help="for each size, print all of the pages, not just the outliers",
    )
    return vars(
        cli.parse_args(sys.argv[1:])  # 1: skips the script name included in argv
    )


def point2cm(point: float | int):
    return point * 0.0352777778


if __name__ == "__main__":
    args = cli_args()
    code = main()
    sys.exit(code)
