let
  pkgs = import (fetchTarball
    "https://github.com/NixOS/nixpkgs/archive/cf8cc1201be8bc71b7cbbbdaf349b22f4f99c7ae.tar.gz")
    { };

in pkgs.mkShell {
  packages = with pkgs; [
    python3
    python312
    python312Packages.pytest
    python3Packages.ipython
    python3Packages.lark
    python3Packages.streamlit
    python3Packages.pyrsistent
    python3Packages.pytest
    python3Packages.pytest-sugar

    pyright
    pypy
  ];
}
