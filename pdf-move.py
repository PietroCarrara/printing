import argparse
from functools import reduce
import sys

import pymupdf
import pikepdf

global args


def main():
    global args

    with pikepdf.Pdf.open(args["input-file.pdf"]) as doc:
        for page in doc.pages:
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
                    # Before current item
                    result.insert(-1, ([], pikepdf.Operator("q")))
                    result.insert(
                        -1,
                        (
                            pikepdf.Matrix().scaled(1 / (ctm.a or 1), 1 / (ctm.d or 1))
                            # .translated(cm2point(-1), cm2point(-1))
                            .scaled(ctm.a, ctm.d).as_array(),
                            pikepdf.Operator("cm"),
                        ),
                    )

                    # Current item goes here

                    # After current item, draw a red rectangle
                    width = 4
                    result.append(([], pikepdf.Operator("q")))
                    # Scale back to user coordinates
                    result.append(
                        (
                            pikepdf.Matrix()
                            .scaled(1 / (ctm.a or 1), 1 / (ctm.d or 1))
                            .as_array(),
                            pikepdf.Operator("cm"),
                        ),
                    )
                    # Line width
                    result.append(([width], pikepdf.Operator("w")))
                    # Red
                    result.append(([1, 0, 0], pikepdf.Operator("RG")))
                    # Rectangle
                    result.append(
                        (
                            [
                                width / 2,
                                width / 2,
                                ctm.a - width / 2,
                                ctm.d - width / 2,
                            ],
                            pikepdf.Operator("re"),
                        )
                    )
                    # Stroke
                    result.append(([], pikepdf.Operator("S")))

                    # Draw resource name
                    result.append(([], pikepdf.Operator("BT")))  # Begin text
                    result.append(([0, 1, 0], pikepdf.Operator("rg")))  # Begin text
                    result.append(
                        (
                            [
                                pikepdf.Name(
                                    next(
                                        iter(
                                            (
                                                page.resources.get("/Font")
                                                or {"/null": ""}
                                            ).keys()
                                        )
                                    )
                                ),
                                32,
                            ],
                            pikepdf.Operator("Tf"),  # Text font
                        )
                    )
                    result.append(
                        (
                            pikepdf.Matrix().as_array(),
                            pikepdf.Operator("Tm"),
                        )
                    )
                    print(
                        operands[0],
                        page.resources.get("/XObject")
                        .get(operands[0])
                        .get("/Subtype"),  # Form XObjects are recursive PDFs!
                    )
                    result.append(
                        ([pikepdf.String(str(operands[0]))], pikepdf.Operator("Tj"))
                    )
                    result.append(([], pikepdf.Operator("ET")))  # End Text

                    result.append(([], pikepdf.Operator("Q")))
                    result.append(([], pikepdf.Operator("Q")))

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
