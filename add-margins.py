import argparse
import sys

import pymupdf

global args


def main():
    global args
    args = cli_args()

    with pymupdf.open(args["input-file.pdf"]) as doc:
        (width, height) = document_size(doc)
        margins = get_margins(args["size"])
        offset_width = (margins["page_size"][0] - width) / 2
        offset_height = (margins["page_size"][1] - height) / 2

        print(f"pdf is {width}cm x {height}cm")

        def draw_margin(margin: str, page: pymupdf.Page, color):
            rect_left = margins[margin][0] - offset_width
            rect_top = margins[margin][1] - offset_height
            rect_right = margins["page_size"][0] - margins[margin][2] - offset_width
            rect_bottom = margins["page_size"][1] - margins[margin][3] - offset_height

            # even pages mean left
            if i % 2 == 0:
                rect_left = margins[margin][2] - offset_width
                rect_right = margins["page_size"][0] - margins[margin][0] - offset_width

            page.draw_rect(
                pymupdf.Rect(
                    cm2point(rect_left),
                    cm2point(rect_top),
                    cm2point(rect_right),
                    cm2point(rect_bottom),
                ),
                color=color,
            )

        i = 1 if not args["start_left"] else 2
        for page in doc:
            draw_margin("safety", page, (1, 0, 0))
            draw_margin("cut", page, (0, 1, 0))
            i += 1

        doc.save(args["output-file.pdf"])
        args


def get_margins(size: str):
    # All units are given in cm
    # Margins are in the format: margin inner, margin top, margin outer, margin bottom

    match size:
        case "15x21":
            return {
                "page_size": (15, 21),
                "cut": (0, 0, 0, 0),
                "bleed": (-0.25, -0.25, -0.25, -0.25),  # Bleed goes out of the page
                "safety": (1.5, 0.5, 0.5, 0.5),
            }
        case "14x21":
            return {
                "page_size": (14, 21),
                "cut": (0, 0, 0, 0),
                "bleed": (-0.25, -0.25, -0.25, -0.25),  # Bleed goes out of the page
                "safety": (1.5, 0.5, 0.5, 0.5),
            }

    raise Exception(f"unknown page size {size}")


def document_size(doc: pymupdf.Document):
    width = None
    height = None

    for page in doc:
        if width is None:
            width = page.bound().width
        elif width != page.bound().width and not args["ignore_size_errors"]:
            raise Exception(
                f"found pages with both width {width} and {page.bound().width}. Please, make your PDF uniform or use --ignore-size-error"
            )

        if height is None:
            height = page.bound().height
        elif height != page.bound().height and not args["ignore_size_errors"]:
            raise Exception(
                f"found pages with both height {height} and {page.bound().height}. Please, make your PDF uniform or use --ignore-size-error"
            )

    if width is None or height is None:
        raise Exception("could not find any pages in your pdf")

    return (point2cm(width), point2cm(height))


def cli_args():
    cli = argparse.ArgumentParser(
        prog="add-margins",
        description="Prints rectangles displaying print margins to a PDF",
    )
    cli.add_argument(
        "input-file.pdf",
    )
    cli.add_argument("output-file.pdf")
    cli.add_argument(
        "-s",
        "--size",
        choices=["14x21", "15x21"],
        required=True,
        help="The page size you wish to print this to",
    )
    cli.add_argument(
        "--ignore-size-errors",
        action="store_true",
        help="Should the script continue operating even when not all PDF pages have the same size?",
    )
    cli.add_argument(
        "--start-left",
        action="store_true",
        help="Is the first page in the PDF the left page?",
    )
    return vars(
        cli.parse_args(sys.argv[1:])  # 1: skips the script name included in argv
    )


def cm2point(cm: float | int):
    return cm * 28.3464566929


def point2cm(point: float | int):
    return point * 0.0352777778


if __name__ == "__main__":
    code = main()
    sys.exit(code)
