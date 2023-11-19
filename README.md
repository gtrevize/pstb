# pstb: Python Simple ToolBox

<img src="https://github.com/gtrevize/ImageRepo/blob/main/pstb8_small_transparent.png?raw=true" alt="pstb logo" width="200"/>

## Table of contents

- [pstb: Python Simple ToolBox](#pstb-python-simple-toolbox)
  - [Table of contents](#table-of-contents)
  - [Disclaimer](#disclaimer)
  - [Description](#description)
  - [Motivation](#motivation)
  - [Designing principles](#designing-principles)
  - [Usage](#usage)
  - [Testing](#testing)
  - [Requirements](#requirements)
  - [Sub-packages](#sub-packages)
  - [Known issues and limitations](#known-issues-and-limitations)
  - [TODO](#todo)
  - [Roadmap](#roadmap)
  - [License](#license)

---

## Disclaimer

I'm a coder by nature. I've been coding both as professionally and as a hobby for more than 40 years.
I'm proficient in more than a couple of dozen programming and scripting languages. __However, Python is not one of them.__
Python is very new for me, and this was part of my self-learning process. In summary, **don't expect this to be *Pythonic*.**
As much as possible I try to follow [PEP-8](http://www.python.org/dev/peps/pep-0008/) guidelines. I use [Black Formatter](https://black.readthedocs.io/en/stable/). However, as a I prefer longer variable names and verbose error messages and comments, I don't follow the 79 characters [maximum line length](https://peps.python.org/pep-0008/#maximum-line-length) because it leads to one line of readable code turning into several. I use 119 instead. IMHO the benefits of a longer line length outweigh the potential issues. This has been an ongoing an heated debate for many years.
As I'm learning the ropes you'll might still find code heavy influenced by C, TypeScript, Java, etc. Use at your own risk.

Is this an original work? Well that's a hard question to answer, isn't it? As I'm learning the language, I have used a lot of different sources and tools, too many to mention all. A partial list will be [^1]: online courses, eBooks, online videos, generative AI tools, online forums, etc. However, I will venture to say that there is no single piece of code that is a copy paste from any source. At least variable naming, comments, error messages, docstrings, logic structure have been modified to fit my personal preferences.

[^1]: All trademarks, service marks, and trade names referenced in this [document/website/material] are the property of their respective owners and are included here solely as a reference.

## Description

Several simple (hopefully easy to use) utilities that come in handy for multiple python projects.

---

## Motivation

First and foremost learn Python. Beyond that, create a library that simplifies common repetitive coding tasks found in many python projects, like file handling, random numbers, files, etc.

## Designing principles

1. Most functions should be one-liners and require as little arguments as possible.
2. Provide sensible defaults for functions requiring multiple arguments.
3. At the same time, do not limit callers ability to use full functionality by overriding the arguments defaults.
4. As much as possible use pure python.
5. Be portable across native Linux, Mac OS and Windows[^2].
6. Use as little dependencies as possible.
7. Be modular to allow "pick and choose".
8. Provide a full suite of unit tests and code coverage report.
9. Provide full docstring documentation.
10. Provide command line utils to consume the library's utilities, when it makes sense to do so.

[^2]: For Windows, the aim is to use avoid the use any kind of Unix like subsystem or emulation environment i.e., [WSL](https://learn.microsoft.com/en-us/windows/wsl/), [git for Windows](https://gitforwindows.org/) a.k.a. *git bash*, or [Cygwin](https://www.cygwin.com/index.html). 

## Usage

See each sub-package for specific usage of available command line utils

## Testing

See each sub-package for available unit tests

## Requirements

See each sub-package for specific requirements

## Sub-packages

- __file__: File related utilities, i.e., finder that allows to navigate an storage hierarchy
- __number__: Number related utilities, including true random numbers

## Known issues and limitations

None known at this time

## TODO

- Add support for compression
- Add support for *curses* for a console interface with mouse support for some command line utils

## Roadmap

Add more sub-packages for database, entity, html, messaging, email, etc.

## License

The MIT License (MIT)

Copyright © 2023

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.