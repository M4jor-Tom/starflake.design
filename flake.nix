{
  description = "Starflake design development shell";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs =
    { nixpkgs, ... }:
    {
      devShells =
        nixpkgs.lib.genAttrs
          [
            "x86_64-linux"
            "aarch64-linux"
          ]
          (
            system:
            let
              pkgs = nixpkgs.legacyPackages.${system};
            in
            {
              default = pkgs.mkShell {
                packages = [
                  pkgs.uv
                  pkgs.python314
                  pkgs.just
                  pkgs.ruff # PyPI's ruff binary cannot run on NixOS
                ];
                # PyOxigraph's PyPI wheel needs the C++ runtime at import time.
                shellHook = ''
                  # Run the checks before every push (.githooks/pre-push).
                  git rev-parse --git-dir >/dev/null 2>&1 && git config core.hooksPath .githooks
                  export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [ pkgs.stdenv.cc.cc.lib ]}''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
                '';
                # uv's downloaded interpreters cannot run on NixOS: use the one above.
                UV_PYTHON_DOWNLOADS = "never";
              };
            }
          );
    };
}
