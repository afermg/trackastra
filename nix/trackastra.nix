{
  lib,
  # build deps
  buildPythonPackage,
  fetchFromGitHub,
  # Py build
  setuptools-scm,
  numpy,
  matplotlib,
  scipy,
  pandas,
  dask,
  humanize,
  configargparse,
  tensorboard,
  pyyaml,
  numba,
  scikit-image,
  chardet,
  lightning,
  kornia,
  torch,
  torchvision,
  lz4,
  imagecodecs,
  wandb,
  # edt, # not on nix
  joblib,
  # test deps
  pytest,
  # Server
  trio,
}:
buildPythonPackage {
  pname = "trackastra";
  version = "0.3.2";

  src = ./..; # For local testing, add flag --impure when running
  # src = fetchFromGitHub {
  #   owner = "afermg";
  #   repo = "trackastra";
  #   rev = "";
  #   sha256 = "sha256-ptLXindgixDa4AV3x+sQ9I4W0PScIQMkyMNMo0WFa0M=";
  # };

  pyproject = true;
  buildInputs = [
    setuptools-scm
  ];
  propagatedBuildInputs = [
    numpy
    matplotlib
    scipy
    pandas
    dask
    humanize
    configargparse
    tensorboard
    pyyaml
    numba
    scikit-image
    chardet
    lightning
    kornia
    torch
    torchvision
    lz4
    imagecodecs
    wandb
    # edt
    joblib
    # kornia>=0.7.0 # TODO remove old augs
    # imagecodecs>=2023.7.10
    # Testing
    pytest
    # Server
    trio
  ];

  pythonImportsCheck = [
  ];

  meta = {
    description = "trackastra";
    homepage = "https://github.com/afermg/trackastra";
    license = lib.licenses.bsd3;
  };
}
