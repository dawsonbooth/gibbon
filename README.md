# `gibbon`

[![pypi version](https://img.shields.io/pypi/v/gibbon.svg?style=flat)](https://pypi.org/pypi/gibbon/)
[![downloads](https://pepy.tech/badge/gibbon)](https://pepy.tech/project/gibbon)
[![build status](https://github.com/dawsonbooth/gibbon/workflows/build/badge.svg)](https://github.com/dawsonbooth/gibbon/actions?workflow=build)
[![python versions](https://img.shields.io/pypi/pyversions/gibbon.svg?style=flat)](https://pypi.org/pypi/gibbon/)
[![format](https://img.shields.io/pypi/format/gibbon.svg?style=flat)](https://pypi.org/pypi/gibbon/)
[![license](https://img.shields.io/pypi/l/gibbon.svg?style=flat)](https://github.com/dawsonbooth/gibbon/blob/master/LICENSE)

## Description

Organize the files in your filesystem according to their attributes.

## Installation

With [Python](https://www.python.org/downloads/) installed, simply run the following command to add the package to your project.

```bash
python -m pip install gibbon
```

## Usage

The following is an example usage of the package:

```python
from gibbon import Tree

with Tree("/path/to/root/folder/", glob="**/*.txt") as tree:
    tree.flatten()
```

Feel free to [check out the docs](https://dawsonbooth.github.io/gibbon/) for more information.

## License

This software is released under the terms of [MIT license](LICENSE).
