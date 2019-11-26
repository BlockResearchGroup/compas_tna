# compas_tna

COMPAS package for Thrust Network Analaysis. This package provides the base implementation of TNA. For a RhinoVault-style user interface and workflow, see `compas-RV2`.

## Getting Started

### Installation

`compas_tna` is not yet on the Python Package Index. For now, it still needs to be installed "from source". Note that as with all things COMPAS, we highly recommend installing `compas_tna` in a specific `conda` environment.

```bash
conda create -n tna -c conda-forge python=3.7 COMPAS
conda activate tna
```

> Note that if you are working on Mac, you need to also install `python.app` in the environment: `conda create -n tna -c conda-forge python=3.7 python.app COMPAS`.

If you have cloned or downloaded the `compas_tna` repo to your computer, navigate to the roof folder and do

```bash
pip install -e .
```

If you prefer installing directly from the github repo, do

```bash
pip install git+https://github.com/compas-dev/compas_tna.git#egg=compas_tna
```

> Note that you will need to have Git installed on your computer for this.

To verify the installation, start an interactive Python interpreter (just type `python` on the command line) and try to import the package.

```python
>>> import compas
>>> import compas_tna
>> exit()
```

### Installation for Rhino

To make `compas_tna` available in Rhino, run the following command from within the `tna` environment on the command line:

```bash
python -m compas_rhino.install -p compas compas_rhino compas_tna
```

The next time you start Rhino, `compas`, `compas_rhino`, and `compas_tna` will be available.

## First Steps

A good place to start exploring TNA through `compas_tna` are the [tutorial](https://compas-dev.github.io/compas_tna/tutorial.html), and the [examples](https://compas-dev.github.io/compas_tna/examples.html).

## Questions and Feedback

For questions and feedback , have a look at the [compas_tna category](https://forum.compas-framework.org/c/compas-tna) of the COMPAS forum.

## Issues

If you run into problems, please file an issue on the [issue tracker](https://github.com/compas-dev/compas_tna/issues). If we don't know it is broken, we can't fix it...

## Contributing

Guidelines for developers are under construction. However, we always accept contributions in the form of Pull Requests.

## License

`compas_tna` is licensed under the MIT License. See [LICENSE](https://github.com/compas-dev/compas_tna/blob/master/LICENSE), for more information.
