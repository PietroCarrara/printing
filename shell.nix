with import <nixpkgs> { };

mkShell {
  packages = [
    pdftk
    ghostscript_headless

    (python3.withPackages (python:
      with python; [
        pikepdf
        (callPackage (import ./nix/pymupdf.nix) { })
      ]))
  ];
}
