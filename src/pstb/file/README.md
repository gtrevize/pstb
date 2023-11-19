# file: File Utilities

---

## Table of contents

- [file: File Utilities](#file-file-utilities)
  - [Table of contents](#table-of-contents)
  - [Description](#description)
  - [Motivation](#motivation)
  - [Usage](#usage)
  - [Testing](#testing)
  - [Requirements](#requirements)
  - [Files](#files)
  - [Known issues and limitations](#known-issues-and-limitations)
  - [TODO](#todo)
  - [Roadmap](#roadmap)
  - [License](#license)

---

## Description

Simple portable utility written in Python to perform several tasks related to file security, including hashing, encryption and shredding

## Motivation

I work a lot on the command line across multiple platforms (Linux, Mac OS, Windows, etc.) and I need to verify, protect and safely dispose of all sorts of files.

Granted there are already many utilities that can perform all these task on the each of those platforms. However, that approach presents several hurdles; namely:

1. Installing additional utilities (e.g., homebrew or port in Mac OS, or Powershell extensions in Windows [^1])
2. Learning and switching to and from completely different syntax for some of the platforms (Windows I'm looking at you)
3. Hard to automate with simple portable scripts
4. Performance varies significantly due totally different implementations for each platform. I'm not claiming that this utility will outperform any other (specially native) utilities, but rather that the expected Performance should be more consistent across platforms

[^1]: For Windows, one can arguably install [WSL](https://learn.microsoft.com/en-us/windows/wsl/), [git for Windows](https://gitforwindows.org/) a.k.a. *git bash*, or [Cygwin](https://www.cygwin.com/index.html) and work with the same (or similar) existing utilities as in Linux and Mac OS, but that's a hurdle in itself. 

## Usage

    foo@bar:~$ pytest finder.py

## Testing

pytest is provided to test all main functionality. Run it like this:

## Requirements

- [pycriptodome](https://www.pycryptodome.org/)

## Files

- **test.txt**: Randomly generated text file
- **test.bin**: Randomly generated binary file
- **test.txt.fse**: Multi-hash file for test.txt
- **test.bin.fse**: Multi-hash file for test.bin
- **filesec.fse**: Multi-hash file for multiple files

## Known issues and limitations

None known at this time

## TODO

- Add support for compression
- Add support for *curses* for a console interface with mouse support

## Roadmap

- Add support for true random using random.org
- Self adapting read and write *block size* to achieve better performance 

## License

The MIT License (MIT)

Copyright © 2023

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.