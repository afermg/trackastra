{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    nixpkgs_master.url = "github:NixOS/nixpkgs/master";
    systems.url = "github:nix-systems/default";
    flake-utils.url = "github:numtide/flake-utils";
    flake-utils.inputs.systems.follows = "systems";
    nahual-flake.url = "github:afermg/nahual";
    nahual-flake.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    systems,
    ...
  } @ inputs:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = import nixpkgs {
          system = system;
          config = {
            allowUnfree = true;
            cudaSupport = true;
          };
        };
        modelPackages = pkgs.callPackage ./nix {};
        python_with_pkgs = pkgs.python3.withPackages (pp: [
          (inputs.nahual-flake.packages.${system}.nahual)
          modelPackages.trackastra
        ]);
        runServer = pkgs.writeScriptBin "nahual-trackastra" ''
          #!${pkgs.bash}/bin/bash
          exec ${python_with_pkgs}/bin/python ${self}/server.py "''${1:-tcp://0.0.0.0:5555}"
        '';
        serverApp = {
          type = "app";
          program = "${runServer}/bin/nahual-trackastra";
        };
      in
        with pkgs; rec {
          apps.default = serverApp;
          formatter = pkgs.alejandra;
          packages =
            modelPackages
            // pkgs.lib.optionalAttrs pkgs.stdenv.hostPlatform.isLinux {
              oci-image = import ./nix/oci-image.nix {
                inherit pkgs;
                name = "trackastra";
                title = "Nahual Trackastra";
                description = "Trackastra cell tracking served through Nahual";
                source = "https://github.com/afermg/trackastra";
                revision = self.rev or self.dirtyRev or "unknown";
                server = runServer;
                entrypoint = serverApp.program;
              };
            };
          devShells = {
            default = let
              python_with_pkgs = (
                python3.withPackages (pp: [
                  (inputs.nahual-flake.packages.${system}.nahual)
                  packages.trackastra
                ])
              );
            in
              mkShell {
                packages = [
                  python_with_pkgs
                ];
                currentSystem = system;
                venvDir = "./.venv";
                postVenvCreation = ''
                  unset SOURCE_DATE_EPOCH
                '';
                postShellHook = ''
                  unset SOURCE_DATE_EPOCH
                '';
                shellHook = ''
                  runHook venvShellHook
                  # PYTHONSAFEPATH=1 (Python 3.11+) keeps Python from prepending
                  # the script's directory (or cwd for python -c mode) to
                  # sys.path, which would otherwise let the in-tree trackastra/
                  # source dir shadow the nix-built package.
                  export PYTHONSAFEPATH=1
                '';
              };
          };
        }
    );
}
