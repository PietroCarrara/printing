with import <nixpkgs> { };

mkShell {
  packages = [
    pdftk
    ghostscript_headless
    (mupdf.overrideAttrs (old: {
      patches = old.patches ++ [
        # https://github.com/ArtifexSoftware/mupdf/pull/69
        (fetchurl {
          url =
            "https://github.com/PietroCarrara/mupdf/commit/a40716d041cfaf2a18d6077e53bb29be330db0be.patch";
          hash = "sha256-DyQLk33d/l+6QPIbE/GU1iIogiAHHj1bJcT+iTaCWz4=";
        })
        # Process form XObjects
        (fetchurl {
          url =
            "https://github.com/PietroCarrara/mupdf/commit/514207db880ace38231f695c829d88e1da1c0cfa.patch";
          hash = "sha256-AooB1p1yb69gyn6kRGNB1Hhpzgf4dBMx+KPfI74av4I=";
        })
        # Respect end of string with \0
        (fetchurl {
          url =
            "https://github.com/PietroCarrara/mupdf/commit/fd7a1d8a9ac7844ca5573f104412cfc82b5d19da.patch";
          hash = "sha256-QYtd/C7d88TKjtSTtz1s8MnO6Eczd3G4tpUz/TOdxnw=";
        })
      ];
      doCheck = false;
    }))

    (python3.withPackages (python:
      with python; [
        pikepdf
        (callPackage (import ./nix/pymupdf.nix) { })
      ]))
  ];
}
