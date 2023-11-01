# WrapKit

[![License: MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](http://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/wrapkit.svg)](https://badge.fury.io/py/wrapkit)
[![PyPI Supported Versions](https://img.shields.io/pypi/pyversions/wrapkit.svg)](https://pypi.org/project/wrapkit)
[![Tests](https://github.com/DavidDotCheck/WrapKit/actions/workflows/test-matrix.yml/badge.svg)](https://github.com/DavidDotCheck/WrapKit/actions/workflows/test-matrix.yml)
[![Coverage](https://github.com/DavidDotCheck/WrapKit/actions/workflows/test-coverage.yml/badge.svg)](https://github.com/DavidDotCheck/WrapKit/actions/workflows/test-coverage.yml)

---
## Table of Contents

- [overview](#overview)
- [prerequisites](#prerequisites)
- [installation](#installation)
- [quickstart](#quickstart)
- [features](#features)
- [usage](#usage)
- [running tests](#running-tests)
- [build documentation](#build-documentation)
- [contributing](#contributing)
- [license](#license)
- [troubleshooting](#troubleshooting)
- [credits](#credits)
- [version history](#version-history)

---
## Overview

WrapKit is a versatile Python library that provides a variety of Object-Oriented Wrapper Classes for common concepts such as Files, Directories, and more. 
It is designed to be easy to use, and easy to extend. It is also designed to be cross-platform, maintaining compatibility with Windows, Linux, and MacOS.

---
## Prerequisites

- Python 3.8 or higher
- `pip` installed
- System requirements: 2GB RAM, 1GB disk space
---
## Installation

### Install from PyPI

```bash
pip install wrapkit
```

### Install from source

```bash
git clone https://api.github.com/repos/DavidDotCheck/WrapKit
cd WrapKit
pip install .
```
---
## Quickstart

### Run the application

```bash
python WrapKit
```
---
## Features

- Feature 1
- Feature 2
- Feature 3
---
## Usage

### File System Example
  
  ```python
  from wrapkit.file_system import File, Directory

  # Create a file
  file = File(content_type="text/plain", content="Hello World!", path="hello.txt")

  # Create a directory
  directory = Directory(path="my_directory")
  directory.create()
  directory.write_file(file)
  ```

## Running tests

To run tests, execute this command in the project's root directory:

```bash
invoke test
```
---
## Build documentation

To build documentation locally, execute this command in the project's root directory:

```bash
invoke docs
```
---
## How to contribute

We welcome contributions from the community! Please read our [contributing guidelines](CONTRIBUTING.md) to learn how to submit a pull request.

---
## License

This project is licensed under the terms of the [MIT License](LICENSE).

---
## FAQ

**Q:** How do i troubleshoot an installation issue?
**A:** See [troubleshooting](#troubleshooting).

---
## Troubleshooting

If you encounter any bugs, please [file an issue](https://api.github.com/repos/DavidDotCheck/WrapKit/issues) along with a detailed description.

---
## Credits

This project was created with [PyLibTemplate](https://github.com/DavidDotCheck/py-lib-template).

---
## Version history

- 0.1.0 - Initial Skeleton
- 0.1.1 - README.md Updates
