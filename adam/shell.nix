let
  pkgs = import (fetchTarball
    "https://github.com/NixOS/nixpkgs/archive/cf8cc1201be8bc71b7cbbbdaf349b22f4f99c7ae.tar.gz")
    { };

in pkgs.mkShell {
  packages = with pkgs; [
<<<<<<< HEAD:adam/shell.nix
    python312
    python312Packages.pytest
    python312Packages.pytest-cov
=======
    python313
>>>>>>> parent of 15f09df (add commets):shell.nix
    python3Packages.ipython
    python312Packages.pylev
    python312Packages.nltk
    python3Packages.lark
    python3Packages.streamlit
    python3Packages.pyrsistent
    python3Packages.pytest-sugar
<<<<<<< HEAD:adam/shell.nix
    python3Packages.tabulate
    sphinx

=======
>>>>>>> parent of 15f09df (add commets):shell.nix
    pyright
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
