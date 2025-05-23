# AI Code Mentor - Contribution Instructions

This file describes how to work on the project and with the sources.

## Package Management

List outdated packages:
```shell
pip list --outdated
```

To update the python packages use:
```shell
pip freeze | %{$_.split('==')[0]} | %{pip install --upgrade $_}
```