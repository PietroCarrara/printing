import argparse
from functools import reduce
import sys

import pymupdf

global args


def main():
    global args

    [width, height] = map(lambda x: cm2point(float(x)), args["size"].split("x"))

    # 0 is top outer, 0.5 center, 1 bottom inner
    gravity = tuple(map(float, args["gravity"].split("x")))

    policy = min
    match args["scale_policy"]:
        case "fill":
            policy = max  # Stop as the two edges fit the page
        case "fit":
            policy = min  # Stop as soon as one of the edges fits on the page
        case "keep":
            policy = lambda w, h: 1  # Don't scale content

    if args["scale"] != None:
        policy = lambda w, h: float(args["scale"])

    with (
        pymupdf.open(args["input-file.pdf"]) as doc,
        pymupdf.Document() as output,
    ):
        i = 0
        for page in doc:
            i += 1
            new_page = output.new_page(width=width, height=height)

            scale_width = width / page.bound().width
            scale_height = height / page.bound().height
            scale = policy(scale_width, scale_height)

            bound = page.bound() * scale
            offset_width = width - bound.width
            offset_height = height - bound.height

            # Reverse horizontal gravity on right pages
            gravx, gravy = gravity if i % 2 == 0 else (1 - gravity[0], gravity[1])

            bound = pymupdf.Rect(
                offset_width * gravx,
                offset_height * gravy,
                offset_width * gravx + bound.width,
                offset_height * gravy + bound.height,
            )

            new_page.show_pdf_page(bound, doc, pno=page.number, keep_proportion=False)

        content = output.write()
        with open(args["output-file.pdf"], "wb") as outfile:
            outfile.write(content)


def cli_args():
    cli = argparse.ArgumentParser(
        prog="pdf-resize",
        description="Resize all pages of a PDF to match a given size",
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
    cli.add_argument(
        "--scale-policy",
        default="keep",
        choices=["keep", "fit", "fill"],
        help="set how the contents should be scaled to fit the new page size",
    )
    cli.add_argument(
        "--scale",
        help="manually sets the scale of the content. Overrides --scale-policy",
    )
    cli.add_argument(
        "-g",
        "--gravity",
        default="0.5x0.5",
        help="sets where the content should stick to. 0x0 means top outer, 1x1 means bottom inner. 0.5x0.5 centers the contents (default)",
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
