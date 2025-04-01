import argparse
import sys

import pymupdf

global args


def main():
    global args
    args = cli_args()

    margins = get_margins(args["size"])
    with pymupdf.open(args["input-file.pdf"]) as doc:
        (width, height) = document_size(doc)
        if (
            abs(margins["size_with_bleed"][0] - width) >= 0.1
            or abs(margins["size_with_bleed"][1] - height) >= 0.1
        ):
            print(
                f"Expected a {margins["size_with_bleed"][0]}x{margins["size_with_bleed"][1]}cm document, got a {width:.2f}x{height:.2f}cm instead. Do you need --spine?"
            )
            return 1

        def draw_margin(margin: str, page: pymupdf.Page, color):
            rect_left = page.bound().tl.x + cm2point(margins[margin][0])
            rect_top = page.bound().tl.y + cm2point(margins[margin][1])
            rect_right = page.bound().br.x - cm2point(margins[margin][2])
            rect_bottom = page.bound().br.y - cm2point(margins[margin][3])

            # Pages reverse inner/outer border for left pages
            if i % 2 == 0:
                rect_left = page.bound().tl.x + cm2point(margins[margin][2])
                rect_right = page.bound().br.x - cm2point(margins[margin][0])

            page.draw_rect(
                pymupdf.Rect(
                    rect_left,
                    rect_top,
                    rect_right,
                    rect_bottom,
                ),
                color=color,
                width=2,
            )

        i = 1 if not args["start_left"] else 2
        for page in doc:
            red = (1, 0, 0)
            green = (0, 1, 0)
            orange = (1, 0.25, 0)
            draw_margin("safety", page, red)
            draw_margin("cut", page, green)
            if "spine" in margins:
                draw_margin("spine", page, orange)
            i += 1

        doc.save(args["output-file.pdf"])
        args


def get_margins(size: str):
    # All units are given in cm
    # Margins are in the format: margin inner, margin top, margin outer, margin bottom

    global args

    if not args["cover"]:
        match size:
            case "15x21":
                return {
                    "size_with_bleed": (15.5, 21.5),
                    "cut": (0.25, 0.25, 0.25, 0.25),
                    "safety": (1.45, 0.75, 0.75, 0.75),
                }
            case "14x21":
                return {
                    "size_with_bleed": (14.5, 21.5),
                    "cut": (0.25, 0.25, 0.25, 0.25),
                    "safety": (1.45, 0.75, 0.75, 0.75),
                }
        raise Exception(f"unknown page size {size}")

    spine_size = args["spine_size"] / 10  # mm to cm

    # hard cover
    if args["hard"]:
        match size:
            case "15x21":
                return {
                    "size_with_bleed": (15 * 2 + 2 * 2 + spine_size, 25),
                    "cut": (2, 2, 2, 2),
                    "safety": (2.5, 2.5, 2.5, 2.5),
                    "spine": (15 + 2, 0, 15 + 2, 0),
                }

    raise Exception(
        f"unknown cover page size {size}. Do you need to use/drop --cover or --hard?"
    )


def document_size(doc: pymupdf.Document):
    width = None
    height = None

    for page in doc:
        if width is None:
            width = page.bound().width
        elif width != page.bound().width:
            raise Exception(
                f"found pages with both width {width} and {page.bound().width}. Please, use pdf-resize"
            )

        if height is None:
            height = page.bound().height
        elif height != page.bound().height:
            raise Exception(
                f"found pages with both height {height} and {page.bound().height}. Please, use pdf-resize"
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
        "--start-left",
        action="store_true",
        help="Is the first page in the PDF the left page?",
    )
    cli.add_argument(
        "--cover",
        action="store_true",
        help="Is this PDF a cover?",
    )
    cli.add_argument(
        "--hard",
        action="store_true",
        help="Is PDF cover a hard one?",
    )
    cli.add_argument(
        "--spine-size", type=float, help="The book spine width, im mm.", default=0
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
