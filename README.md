[![Python 3.11](https://github.com/gut-space/svarog-server/actions/workflows/pytest-3.11.yml/badge.svg)](https://github.com/gut-space/svarog-server/actions/workflows/pytest-3.11.yml)
[![Python 3.12](https://github.com/gut-space/svarog-server/actions/workflows/pytest-3.12.yml/badge.svg)](https://github.com/gut-space/svarog-server/actions/workflows/pytest-3.12.yml)
[![Pylint](https://github.com/gut-space/svarog-server/actions/workflows/pylint.yml/badge.svg)](https://github.com/gut-space/svarog-server/actions/workflows/pylint.yml)
[![Flake8](https://github.com/gut-space/svarog-server/actions/workflows/flake8.yml/badge.svg)](https://github.com/gut-space/svarog-server/actions/workflows/flake8.yml)
[![CodeQL](https://github.com/gut-space/svarog-server/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/gut-space/svarog-server/actions/workflows/github-code-scanning/codeql.yml)

<img align="right" width="128" height="128" src="https://github.com/gut-space/svarog/blob/master/doc/logo.png">

The goal of this project is to build a fully functional automated VHF satellite ground station, loosely based on [satnogs](https://satnogs.org) project.

Project founders: [Sławek Figiel](https://github.com/fivitti) and [Tomek Mrugalski](https://github.com/tomaszmrugalski/)

# Project status

As of Feb 2021, the following features are working:

- WiMo TA-1 antenna, SDR and RPi4 are working
- Automated reception and transmission decoding for NOAA-15, NOAA-18 and NOAA-19 satellites (APT)
- Support for Meteor M2 transmissions (LRPT)
- Transmissions are decoded and uploaded automatically to our content server (see https://svarog.space)
- Automated updates for the server and station
- Orbital TLE data is recorded and prestend in several formats (native TLE, easy to understand orbital parameters etc.)
- Pass over charts (azimuth/elevation)

Work in progress and plans for the near future:

- quality assessment for decoded images
- user management
- georeferencing
- telemetry reception

# Documentation

- [Installation](doc/install.md)
- [Architecture](doc/arch.md)
- [Developer's guide](doc/devel.md)
- [User Management](doc/users.md)
- [Project report](doc/prototype-phase/satnogs-gdn-report.pdf) - a report from the early days when this was a team university project
- [Project poster 1](doc/prototype-phase/poster1-pl.jpg)
- [Project poster 2](doc/prototype-phase/poster2-en.jpg)
- For older files see https://github.com/gut-space/satnogs.
