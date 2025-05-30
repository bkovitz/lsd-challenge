let
  pkgs = import (fetchTarball
    "https://github.com/NixOS/nixpkgs/archive/cf8cc1201be8bc71b7cbbbdaf349b22f4f99c7ae.tar.gz")
    { };

in pkgs.mkShell {
  packages = with pkgs; [
    pyright
    python312
    python312Packages.nltk
    python312Packages.pylev
    python312Packages.pytest
    python312Packages.pytest-cov
    python3Packages.ipython
    python3Packages.lark
    python3Packages.pyrsistent
    python3Packages.pytest-sugar
    python3Packages.streamlit
    python3Packages.tabulate
    sphinx
  ];
  shellHook = ''
    # create the virtual environment if it doesn't exist
    if [ ! -d .venv ]; then
      python3 -m venv .venv
    fi

    # activate the virtual environment
    source ./.venv/bin/activate
  '';
}
