import argparse
from functools import reduce
import sys
import traceback
from typing import Union

import pikepdf

global args

PDFInstructionList = list[
    Union[pikepdf.ContentStreamInstruction, pikepdf.ContentStreamInlineImage]
]


def main():
    global args

    with pikepdf.Pdf.open(args["input-file.pdf"]) as doc:
        for page in doc.pages:
            result = walk_content_objects(doc, page, on_image=highlight_images)
            page.Contents = doc.make_stream(pikepdf.unparse_content_stream(result))

        doc.save(args["output-file.pdf"])


def no_transform(
    doc: pikepdf.Pdf,
    page_or_stream: pikepdf.Object | pikepdf.Page,
    instructions: PDFInstructionList,
    ctm: pikepdf.Matrix,
    text_matrix: pikepdf.Matrix,
) -> PDFInstructionList:
    return instructions


def walk_content_objects(
    doc: pikepdf.Pdf,
    page_or_stream: pikepdf.Object | pikepdf.Page,
    on_image=no_transform,
):
    contents = pikepdf.parse_content_stream(page_or_stream)

    ctm = pikepdf.Matrix()  # current transformation matrix
    text_matrix = pikepdf.Matrix()
    stack: list[pikepdf.Matrix] = []
    result = []

    for operands, command in contents:
        instructions = [(operands, command)]

        if command == pikepdf.Operator("Tm"):
            text_matrix = pikepdf.Matrix(operands)
        elif command == pikepdf.Operator("cm"):
            ctm = pikepdf.Matrix(operands) @ ctm
        elif command == pikepdf.Operator("q"):
            stack.append(ctm)
        elif command == pikepdf.Operator("Q"):
            ctm = stack.pop()
        elif command == pikepdf.Operator("Do"):
            try:
                xobject = page_or_stream.resources.get("/XObject").get(operands[0])
                match xobject.get("/Subtype"):
                    case "/Image":
                        instructions = on_image(
                            doc,
                            page_or_stream,
                            instructions.copy(),
                            ctm,
                            text_matrix,
                        )
                    case "/Form":
                        new_instructions = walk_content_objects(
                            doc, xobject, on_image=on_image
                        )
                        new_stream = doc.make_stream(
                            pikepdf.unparse_content_stream(new_instructions),
                            xobject.stream_dict,
                        )
                        page_or_stream.get("/Resources").get("/XObject")[
                            operands[0]
                        ] = new_stream
            except Exception as e:
                print(repr(e), file=sys.stderr)
                print(traceback.format_exc(), file=sys.stderr)

        result.extend(instructions)

    return result


def highlight_images(
    doc: pikepdf.Pdf,
    page_or_stream: pikepdf.Object | pikepdf.Page,
    instructions: PDFInstructionList,
    ctm: pikepdf.Matrix,
    text_matrix: pikepdf.Matrix,
) -> PDFInstructionList:
    operands, command = instructions[0]

    # Before current item
    instructions.insert(-1, ([], pikepdf.Operator("q")))
    instructions.insert(
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
    instructions.append(([], pikepdf.Operator("q")))
    # Scale back to user coordinates
    instructions.append(
        (
            pikepdf.Matrix().scaled(1 / (ctm.a or 1), 1 / (ctm.d or 1)).as_array(),
            pikepdf.Operator("cm"),
        ),
    )
    # Line width
    instructions.append(([width], pikepdf.Operator("w")))
    # Red
    instructions.append(([1, 0, 0], pikepdf.Operator("RG")))
    # Rectangle
    instructions.append(
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
    instructions.append(([], pikepdf.Operator("S")))

    instructions.append(([], pikepdf.Operator("Q")))
    instructions.append(([], pikepdf.Operator("Q")))

    return instructions


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
