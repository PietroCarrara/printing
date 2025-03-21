with import <nixpkgs> { };

mkShell {
  packages = [
    (python3.withPackages
      (python: with python; [ (callPackage (import ./nix/pymupdf.nix) { }) ]))
  ];
}
