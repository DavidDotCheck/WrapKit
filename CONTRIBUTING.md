# Contributing to WrapKit

Thank you for your interest in contributing to WrapKit! We welcome contributions from everyone. Below are guidelines on how to contribute.
---
## Table of Contents

-[architecture](#architecture)
-[getting started](#getting-started)
-[setting up development environment](#setting-up-development-environment)
-[contributing workflow](#contributing-workflow)
-[issue guidelines](#issue-guidelines)
-[pull request guidelines](#pull-request-guidelines)
-[code style](#code-style)
-[testing](#testing)
-[documentation](#documentation)

---
## Architecture

### Overview

Add a brief description of the project architecture here.
Maybe include a diagram or two.

### Components

You can add a list of components here to give an overview of the project structure.
---
## Getting Started

To get started, make sure you have:

- Forked the repository
- Cloned your fork locally
- Created a new branch for your feature or fix
---
## Setting Up Development Environment

1. Python 3.8 or higher
2. `pip` installed
3. System requirements: 2GB RAM, 1GB disk space
---
## Contributing Workflow

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature or fix
4. Make changes
5. Commit and push to your fork
6. Open a pull request targeting the main branch of the original repository
---
## Issue Guidelines

If you find a bug or would like to request a feature, please:

- Check to see if the issue already exists.
- If not, create a new issue with a descriptive title and clear explanation.
- Fill out the issue template with as much detail as possible.
---
## Pull Request Guidelines

- Make sure your PR includes only related changes.
- Add relevant unit tests for your changes.
- Make sure all tests pass before submitting a PR.
---
## Code Style

Follow the code style used throughout the project.
---
## Testing

To run tests, execute this command in the project's root directory:

```bash
invoke test
```
---
## Documentation

To build the HTML documentation:

```bash
invoke docs
```

Find the generated documentation in the `docs/_build/` directory.
