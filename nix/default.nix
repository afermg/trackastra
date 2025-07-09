{
  lib,
  pkgs,
  python3Packages,
}:
let
  callPackage = lib.callPackageWith (pkgs // packages // python3Packages);
  packages = {
    trackastra = callPackage ./trackastra.nix { };
  };
in
packages
