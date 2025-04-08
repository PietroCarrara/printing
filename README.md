# Things That Help Me Prepare PDFs for printing

## Useful Commands

- `gs -sDEVICE=pdfwrite -dNOPAUSE -dBATCH -dSAFER -dCompatibilityLevel=1.3 -sOutputFile=output.pdf input.pdf`: Downgrade a PDF to version 1.3. Useful for compatibility.
- `echo "" | ps2pdf -sPAPERSIZE=a5 - blank.pdf`: Generate a PDF with a single blank page
- `npx press-ready lint input.pdf`: Check if PDF is okay for printing
- `gs -sDEVICE=pdfwrite -o out.pdf -c "<< /AlwaysOutline [/Fo1S0 /Fo2S0 /Fo3S0 /Fo4S0] >> setdistillerparams" -f input.pdf`: Converts text using the listed fonts into vectors (a.k.a. "Outlining")
- `gs -sDEVICE=pdfwrite -o out.pdf -c "<< /AlwaysOutline [/] >> setdistillerparams" -f input.pdf`: Removes fonts with no name (probably by outlining them, but I don't even know if it's possible to reference them)

## Useful Links

- **[sejda.com](https://www.sejda.com)**: Useful PDF tools. Freemium.
- **[convertio.co](https://convertio.co)**: Convert CFF fonts to TTF. Freemium.

## Notes

### On Scribus and PDF Editing

Scribus can import PDFs for editing, but in my experience, if you import more than one page at a time, it will generate a very complex output (`ghostscript` looked like it was in an infinite loop when trying to process those). I found out that by importing one page at a time, and then glueing them all later works best.

## TODOs:

### Scaling and Full-Page Images

Scaling the contents of a book to fit them inside the safety margins of the printer will cause images that previously touched the borders of the page to not do so anymore. This is currently fixed by hand, via importing the PDF on Scribus and editing each offender. Maybe this could be scripted, even if using the Scribus python API.
