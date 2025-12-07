# Contributing to Cerberus

First off, thanks for taking the time to contribute! 🎉

The following is a set of guidelines for contributing to Cerberus. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## Code of Conduct

This project and everyone participating in it is governed by the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for Cerberus. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

*   **Use a clear and descriptive title** for the issue to identify the problem.
*   **Describe the exact steps which reproduce the problem** in as many details as possible.
*   **Provide specific examples** to demonstrate the steps.
*   **Describe the behavior you observed** after following the steps and point out what exactly is the problem with that behavior.
*   **Explain which behavior you expected to see instead** and why.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for Cerberus, including completely new features and minor improvements to existing functionality.

*   **Use a clear and descriptive title** for the issue to identify the suggestion.
*   **Provide a step-by-step description of the suggested enhancement** in as many details as possible.
*   **Explain why this enhancement would be useful** to most Cerberus users.

### Pull Requests

1.  Fork the repo and create your branch from `main`.
2.  If you've added code that should be tested, add tests.
3.  If you've changed APIs, update the documentation.
4.  Ensure the test suite passes.
5.  Make sure your code lints.
6.  Issue that pull request!

## Development Setup

### fast track (Docker)

The easiest way to develop is using Docker:

```bash
docker build -t cerberus:dev .
docker run --rm -v $(pwd):/app cerberus:dev ...
```

### Local Setup

You can use the standalone installation script for a quick development environment setup:

```bash
./install.sh
source ~/.cerberus/venv/bin/activate
pip install -r requirements.txt
```

## Style Guide

*   We use **PEP 8** for Python code.
*   We use **ShellCheck** for shell scripts.
*   Commits should follow [Conventional Commits](https://www.conventionalcommits.org/).

## License

By contributing, you agree that your contributions will be licensed under its MIT License.
