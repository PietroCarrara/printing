import argparse
from functools import reduce
import sys

import pymupdf
import pikepdf

global args


def main():
    global args

    with pikepdf.Pdf.open(args["input-file.pdf"]) as doc:
        for page in doc.pages[4:]:
            contents = pikepdf.parse_content_stream(page)

            offset_x = -1
            offset_y = 0

            result = []
            for operands, command in contents:
                result.append([operands, command])

                if command == pikepdf.Operator("Tm"):
                    text_matrix = pikepdf.Matrix(operands).translated(
                        offset_x, offset_y
                    )
                    result[-1][0] = pikepdf.Array(text_matrix)

            page.Contents = doc.make_stream(pikepdf.unparse_content_stream(result))

        doc.save(args["output-file.pdf"])


def cli_args():
    cli = argparse.ArgumentParser(
        prog="pdf-move",
        description="Move the contents of PDF pages",
    )
    cli.add_argument(
        "input-file.pdf",
    )
    cli.add_argument(
        "output-file.pdf",
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
