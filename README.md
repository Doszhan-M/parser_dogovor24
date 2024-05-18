# Parser for dogovor24

`Dogovor24Parser` is an asynchronous parser for the website [dogovor24.kz](https://new.dogovor24.kz) that automatically collects and saves documents. This tool is designed to simplify the process of collecting legal documentation from the website.

## Features

- Asynchronous parsing using `aiohttp` and `playwright` for fast and efficient performance.
- Saving documents to the local file system.
- Logging the parsing progress.

## Installation

Before starting, make sure you have Python 3.10+ and the necessary libraries installed:

```sh
pip install -r requirements.txt
python -m playwright install
