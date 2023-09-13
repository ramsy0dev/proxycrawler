<div align="center">

# proxycrawler

![GitHub commits since latest release (by SemVer including pre-releases)](https://img.shields.io/github/commits-since/ramsy0dev/proxycrawler/latest?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/ramsy0dev/proxycrawler?style=for-the-badge)
![GitHub](https://img.shields.io/github/license/ramsy0dev/proxycrawler?style=for-the-badge)
![GitHub all releases](https://img.shields.io/github/downloads/ramsy0dev/proxycrawler/total?style=for-the-badge)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/ramsy0dev/proxycrawler?style=for-the-badge)

</div>

# Table of content

* [What is proxycrawler?](#what-is-proxycrawler)
* [What services does it scrap from?](#what-services-does-it-scrap-from)
* [Installation](#installation)
    * [Prerequisites](#prerequisites)
    * [Install manually](#install-manually)
* [Usage](#usage)
* [Contributing](#contributing)
* [License](#license)

# What is proxycrawler?

proxycrawler, is as the name suggest is a proxy crawler and validator. proxycrawler scrapes services (as of v0.1.0 it supports only 2 services) that offer free proxies either displaied in a table so you can then go in the hell of trying to copy each one them and validate them, or by directly sending out requests to the API that these services use (like [geonode.com](https://geonode.com))

# What services does it scrap from?

As of v0.1.0 proxycrawler usilizes two services:

* [free-proxy-list.net](https://free-proxy-list.net)
* [Geonode.net](https:/geonode.net)

# Installation

* ## Prerequisites

    * Python3.10>=+
    * poetry
* ## Install manually

To install manually you will need `poetry` in order to build from source after you clone the repo:

``` bash
git clone https://github.com/ramsy0dev/proxycrawler
cd proxycrawler
poetry build
pip install dist/proxycrawler-*.tar.gz
```

# Usage

To see how to use proxycrawler and get a basic guide on how to get started. Please checkout the [wiki]()

# Contributing

All contributations are acceptable.

# License

GPL-V3.0
