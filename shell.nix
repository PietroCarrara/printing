with import <nixpkgs> { };

mkShell {
  packages = [
    pdftk
    ghostscript_headless

    (python3.withPackages
      (python: with python; [ (callPackage (import ./nix/pymupdf.nix) { }) ]))
  ];
}
