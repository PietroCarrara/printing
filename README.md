# Things That Help Me Prepare PDFs for printing

## Useful Commands

- `gs -sDEVICE=pdfwrite -dNOPAUSE -dBATCH -dSAFER -dCompatibilityLevel=1.3 -sOutputFile=output.pdf input.pdf`: Downgrade a PDF to version 1.3. Useful for compatibility.
- `echo "" | ps2pdf -sPAPERSIZE=a5 - blank.pdf`: Generate a PDF with a single blank page

## Useful Links

- **[sejda.com](https://www.sejda.com)**: Useful PDF tools. Freemium.

## TODOs:

### Scaling and Full-Page Images

Scaling the contents of a book to fit them inside the safety margins of the printer will cause images that previously touched the borders of the page to not do so anymore. This is currently fixed by hand, via importing the PDF on Scribus and editing each offender. Maybe this could be scripted, even if using the Scribus python API.
