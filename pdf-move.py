import argparse
from functools import reduce
import sys

import pymupdf
import pikepdf

global args


def main():
    global args

    with pikepdf.Pdf.open(args["input-file.pdf"]) as doc:
        for page in doc.pages[4:5]:
            contents = pikepdf.parse_content_stream(page)

            ctm = pikepdf.Matrix()  # current transformation matrix
            text_matrix = pikepdf.Matrix()
            stack: list[pikepdf.Matrix] = []
            result = []
            for operands, command in contents:
                result.append([operands, command])

                if command == pikepdf.Operator("Tm"):
                    text_matrix = pikepdf.Matrix(operands)
                elif command == pikepdf.Operator("cm"):
                    ctm = pikepdf.Matrix(operands) @ ctm
                elif command == pikepdf.Operator("q"):
                    stack.append(ctm)
                elif command == pikepdf.Operator("Q"):
                    ctm = stack.pop()
                elif command == pikepdf.Operator("Do"):
                    print(page)

                    # Before current item
                    result.insert(-1, ([], pikepdf.Operator("q")))
                    result.insert(
                        -1,
                        (
                            pikepdf.Matrix()
                            .scaled(1 / ctm.a, 1 / ctm.d)
                            .translated(cm2point(-1), cm2point(-1))
                            .scaled(ctm.a, ctm.d)
                            .as_array(),
                            pikepdf.Operator("cm"),
                        ),
                    )

                    # Current item goes here

                    # After current item
                    result.append(([], pikepdf.Operator("Q")))
                    print(result)

            page.Contents = doc.make_stream(pikepdf.unparse_content_stream(result))

        doc.save(args["output-file.pdf"])


def cm2point(cm: float | int):
    return cm * 28.3464566929


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
