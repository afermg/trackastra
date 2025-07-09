{
  lib,
  buildPythonPackage,
  fetchFromGitHub,
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
  # edt, # not on nixpkgs
  joblib,
  pytest,
}:
buildPythonPackage {
  pname = "trackastra";
  version = "0.3.2";
  format = "pyproject";

  src = fetchFromGitHub {
    owner = "afermg";
    repo = "trackastra";
    rev = "";
    sha256 = "";
  };

  
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
    # Testing
    pytest
  ];

  pythonImportsCheck = [
    "trackastra"
  ];

  meta = {
    description = "trackastra";
    homepage = "https://github.com/afermg/trackastra";
    license = lib.licenses.bsd3;
    maintainers = with lib.maintainers; [ afermg ];
    platforms = lib.platforms.all;
  };
}
