import argparse
from functools import reduce
import sys

import pymupdf

global args


def main():
    global args

    [width, height] = map(lambda x: cm2point(float(x)), args["size"].split("x"))

    with (
        pymupdf.open(args["input-file.pdf"]) as doc,
        pymupdf.Document() as output,
    ):
        for page in doc:
            new_page = output.new_page(width=width, height=height)

            scale_width = width / page.bound().width
            scale_height = height / page.bound().height
            scale = max(scale_width, scale_height)

            gravity = (0.5, 0.5)  # 0 is top left, 0.5 center, 1 bottom right

            bound = page.bound() * scale
            offset_width = abs(width - bound.width)
            offset_height = abs(height - bound.height)

            bound = pymupdf.Rect(
                -offset_width * gravity[0],
                -offset_height * gravity[1],
                width + offset_width * (1 - gravity[0]),
                height + offset_height * (1 - gravity[1]),
            )

            new_page.show_pdf_page(bound, doc, pno=page.number, keep_proportion=False)

        content = output.write()
        with open(args["output-file.pdf"], "wb") as outfile:
            outfile.write(content)


def cli_args():
    cli = argparse.ArgumentParser(
        prog="page-report",
        description="Print a report on page sizes of a PDF",
    )
    cli.add_argument(
        "input-file.pdf",
    )
    cli.add_argument(
        "output-file.pdf",
    )
    cli.add_argument(
        "-s",
        "--size",
        required=True,
        help="set the size for the PDF in centimeters (15x21, 21x29.7, ...)",
    )
    return vars(
        cli.parse_args(sys.argv[1:])  # 1: skips the script name included in argv
    )


def cm2point(cm: float | int):
    return cm * 28.3464566929


if __name__ == "__main__":
    args = cli_args()
    code = main()
    sys.exit(code)
