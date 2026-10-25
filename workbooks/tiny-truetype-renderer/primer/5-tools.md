# Building and checking

The programs you run while you work: the compiler and the build tools that turn your project
into programs, the terminal you run them from, and the workbook's checker and study server.

## The C++ compiler: g++ and clang
<!--
id: compiler
also: compiler; g++; gcc; clang; MinGW; MinGW-w64; WinLibs; MSYS2; Xcode command line tools; C++20
-->
A compiler turns C++ source code into a program the computer can run. The workbook uses g++,
the C++ compiler of GCC:

- On Windows, g++ from MinGW-w64, a build of GCC that makes Windows programs. WinLibs and MSYS2
  provide it.
- On Linux, GCC from the system's package manager (for example `sudo apt install g++`).
- On macOS, the command line tools of Xcode (`xcode-select --install`). Their `g++` command is
  Apple's clang under another name, which works the same way for this project.

On Windows, WinLibs is the shortest route, because its download also holds
[CMake](#primer/cmake) and [Ninja](#primer/ninja) in the same `bin` folder as g++. In
PowerShell:

```
winget install BrechtSanders.WinLibs.POSIX.UCRT
```

winget unpacks it and adds its `mingw64\bin` folder to your `PATH`, the list of folders the
terminal searches for programs. Without winget, download the 64-bit UCRT build with POSIX
threads from [winlibs.com](https://winlibs.com/), unzip it to a folder whose path has no
spaces, such as `C:\winlibs`, and add `C:\winlibs\mingw64\bin` to `PATH` yourself:

1. Open Settings, search for "environment" and choose "Edit the system environment variables".
2. Click Environment Variables.
3. Under the variables for your user, select Path and click Edit.
4. Click New, paste the folder, and click OK in each window.

A terminal keeps the `PATH` it started with, so open a new PowerShell window afterwards.

The project needs C++20 (`set(CMAKE_CXX_STANDARD 20)` in its build file), so the compiler must
be recent enough: GCC 10 or newer, or a current Xcode. Type `g++ --version` in PowerShell (or
any terminal) to see which one you have. If the terminal answers that it doesn't know `g++`,
the folder holding it isn't on your `PATH` yet.

You rarely call the compiler yourself. [CMake](#primer/cmake) works out the commands, and the
checker's setup tells CMake to use `g++` (`-DCMAKE_CXX_COMPILER=g++`). A command it runs looks
roughly like this:

```
g++ -std=c++20 -Wall -Wextra -Isrc -Ithird_party -c src/font/ByteReader.cpp -o ByteReader.o
```

`-std=c++20` picks the language version, `-Wall -Wextra` turn on
[warnings](#primer/compiler-warnings), `-I` adds an include directory and `-c` means "compile
only", the first of the two steps described under
[compiling and linking](#primer/compile-and-link).

Learn more:
- [Introduction to the compiler, linker, and libraries](https://www.learncpp.com/cpp-tutorial/introduction-to-the-compiler-linker-and-libraries/)
  on learncpp.com
- [WinLibs](https://winlibs.com/), standalone MinGW-w64 builds of GCC for Windows
- [GCC command options](https://gcc.gnu.org/onlinedocs/gcc/Invoking-GCC.html) in the GCC manual

## Compiling and linking
<!--
id: compile-and-link
also: compile; link; linker; object file; .o; compile error; link error; undefined reference; multiple definition; ld returned 1 exit status
-->
Building a C++ program takes two steps.

1. Compiling: the compiler turns each `.cpp` file, with the headers it includes, into an
   object file (`.o`) of machine code. It looks at one `.cpp` at a time. A call to a function
   in another file compiles as long as a declaration is in view; the compiler leaves a note
   that the function must be found later.
2. Linking: the linker joins the object files and libraries into one program and connects
   each such call to the function's definition. GCC's linker is a program called `ld`, which
   g++ starts through a small helper, `collect2` (`collect2.exe` on Windows).

The two steps fail in different ways. A compile error comes from your code in one file and
names the file, line and column:

```
src/font/Loca.cpp:12:5: error: 'numGlyps' was not declared in this scope
```

A link error comes after every file has compiled, from the linker, and names a function instead
of a line:

```
undefined reference to `loadGlyphLocations(ByteReader&, std::map<...> const&)'
multiple definition of `lerp(Vec2, Vec2, double)'
collect2.exe: error: ld returned 1 exit status
```

The last line comes from `collect2` and only says that `ld` failed; the lines above it say why.
"Undefined reference" means something is declared and called but never defined: the body is
missing, its parameter types or a `const` differ from the declaration's (which makes it a
different function to the linker), or its `.cpp` isn't part of the build. "Multiple definition" means a function is defined in two
places, often a function in a header without [`inline`](#primer/inline). A program with no
`main` fails at this step too.

The checker reports both as `Compile Error` and shows the messages. Read the first error first;
later ones often follow from it. All `.cpp` files under `src/` are built together, so an error
in another assignment's file stops this one, and the checker says which file it was.

Learn more:
- [Introduction to the compiler, linker, and libraries](https://www.learncpp.com/cpp-tutorial/introduction-to-the-compiler-linker-and-libraries/)
  on learncpp.com
- [Forward declarations and definitions](https://www.learncpp.com/cpp-tutorial/forward-declarations/)
  on learncpp.com, with the errors a missing definition causes

## Compiler warnings
<!--
id: compiler-warnings
also: warning; -Wall; -Wextra; -Wno-unused-parameter; sign-compare; Wnarrowing; compiler warnings
-->
A warning is the compiler pointing at code that is legal but probably wrong. Unlike an error,
it doesn't stop the build. The project's `CMakeLists.txt` turns on two large groups,
`-Wall` and `-Wextra`, and turns one off, `-Wno-unused-parameter`, because the Boilerplate's
unfinished functions don't use their parameters yet.

Warnings you are likely to meet here:

| Warning | What it usually means |
|---|---|
| comparison of integer expressions of different signedness | an `int` compared with a `size_t`; −1 would become huge |
| narrowing conversion of 'r' from 'int' to 'uint8_t' | a value in braces that may not fit |
| suggest parentheses around comparison in operand of '&' | `flags & MASK == 0`, which tests the wrong thing |
| '...' will be initialized after | a member initializer list in a different order from the members |
| '...' may be used uninitialized | a variable read before anything was stored in it |

When the build succeeds with warnings, the checker prints the first ten under
`Compiler warnings:` before it runs the tests. Read them, in particular when a test fails for no
reason you can see: several of the classic C++ bugs in a font reader, such as a signed/unsigned
mix-up, show up as a warning first. Code that compiles without warnings is the goal.

Learn more:
- [Configuring your compiler: Warning and error levels](https://www.learncpp.com/cpp-tutorial/configuring-your-compiler-warning-and-error-levels/)
  on learncpp.com
- [Options to request or suppress warnings](https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html)
  in the GCC manual, which lists what `-Wall` and `-Wextra` include

## CMake and `CMakeLists.txt`
<!--
id: cmake
also: CMake; CMakeLists.txt; cmake -S -B; cmake --build; target; configure; build system generator; static library; tiny_ttf_core
-->
CMake reads a description of a project, `CMakeLists.txt`, and writes the build files for a
build tool such as [Ninja](#primer/ninja). It works in two steps, each one command:

```
cmake -S solutions -B build/solutions -G Ninja -DCMAKE_CXX_COMPILER=g++
cmake --build build/solutions --target assignment_07
```

The first command is the configure step: it reads `solutions/CMakeLists.txt` and writes the
build files into `build/solutions`. The second builds one target, a program or library the file
defines. The checker runs the first when `build/solutions/build.ninja` doesn't exist yet and the
second on every check.

Your project's `CMakeLists.txt` (from `starters/project/`) says:

- C++20, without compiler extensions (GCC's own additions to the language, which other
  compilers reject), and a Debug build unless you ask for another (see
  [debug builds](#primer/debug-build)).
- Warnings `-Wall -Wextra`, without the unused-parameter warning.
- On Windows with MinGW, link with `-static`: copy the parts of the compiler's own libraries
  that a program uses into its `.exe`. Without it, each program needs the compiler's DLLs
  (Windows library files that programs load when they start) on the `PATH`.
- `tiny_ttf_core`: a static library, a bundle of compiled `.cpp` files that programs link
  with, made from every `.cpp` under `src/` except `main.cpp`, with `src/` and `third_party/`
  as include directories. New files are picked up at the next build.
- `tiny_ttf`: the finished program, from `src/main.cpp`, once that file exists (18).
- One program per assignment: `assignments/assignment_07_simple_glyph.cpp` becomes the target
  `assignment_07`, linked with the library.

So building any one assignment compiles every `.cpp` in `src/`. You can leave
`CMakeLists.txt` as it is for the whole workbook.

CMake 3.20 or newer is needed. On Windows the WinLibs download (see
[the compiler](#primer/compiler)) includes it. Otherwise install it with
`winget install Kitware.CMake`, or download the Windows x64 installer (`.msi`) from
[cmake.org/download](https://cmake.org/download/) and choose the option that adds CMake to the
`PATH`. On macOS Homebrew has `cmake`, and on Linux the package manager does. Check it in a new
PowerShell window with `cmake --version`.

On its own, for example after you've put it on GitHub, the project builds with
`cmake -S . -B build` and `cmake --build build` from inside `solutions/`.

Learn more:
- [CMake tutorial](https://cmake.org/cmake/help/latest/guide/tutorial/index.html) on cmake.org
- [cmake command line](https://cmake.org/cmake/help/latest/manual/cmake.1.html) on cmake.org,
  for `-S`, `-B`, `-G` and `--build`

## Ninja
<!--
id: ninja
also: Ninja; ninja; build.ninja; -G Ninja; build tool; generator
-->
Ninja is a small, fast build tool. It reads a file of build rules, `build.ninja`, compares the
date of each output with the dates of the files it depends on, and runs only the compile and
link commands whose inputs have changed. Change one `.cpp`, and the next build compiles that
file and links the programs again, instead of rebuilding everything. It runs independent
commands in parallel on all your processor's cores.

You don't write `build.ninja` yourself: [CMake](#primer/cmake) generates it during configure,
when given `-G Ninja` (the G is for generator). You don't usually run `ninja` either, since
`cmake --build build/solutions` calls it for you. CMake can generate other kinds of build files
too, such as Makefiles or Visual Studio projects; the workbook uses Ninja because it behaves the
same on Windows, macOS and Linux.

Ninja has to be installed and on your `PATH`, like the compiler. On Windows the WinLibs download
(see [the compiler](#primer/compiler)) includes it. Otherwise install it with
`winget install Ninja-build.Ninja`, or download the Windows zip from the
[Ninja releases page](https://github.com/ninja-build/ninja/releases), unzip `ninja.exe` into a
folder and add that folder to `PATH`. MSYS2 has it as a separate package; on macOS Homebrew has
`ninja`, and on Linux the package is usually `ninja-build`.

`ninja --version` in a new PowerShell window shows whether the terminal finds it. If the
checker's setup fails with a message that CMake can't find Ninja (or `CMAKE_MAKE_PROGRAM` is
not set), install it and open a new terminal.

The README lists Ninja, CMake and g++ as the three tools the C++ project needs, and the study
server checks for them when it starts.

Learn more:
- [Ninja](https://ninja-build.org/), the project's home page
- [Ninja manual](https://ninja-build.org/manual.html), on how it decides what to rebuild
- [Ninja generator](https://cmake.org/cmake/help/latest/generator/Ninja.html) in the CMake
  documentation

## The `build` folder
<!--
id: build-folder
also: build folder; build directory; build/solutions; build/cases; build/fresh; out-of-source build; .gitignore
-->
Everything the tools produce goes into `build/` in the workbook folder, apart from your source
code. Keeping it separate (an out-of-source build) means you can delete it at any time without
losing work.

| Folder | What's in it |
|---|---|
| `build/solutions/` | Your project's build: `build.ninja`, CMake's cache, object files and the programs, such as `assignment_07.exe` and `tiny_ttf.exe` |
| `build/cases/07/` | The last check of assignment 07: each test's input (`.in`), your output (`.out`, or `.out.png` for pictures) and, for pictures, the diff image |
| `build/fresh/07/` | Tests made by `-Fresh` |
| `build/ref-src/`, `build/ref/` | The reference program, built to draw the expected pictures of fresh tests |

The files in `build/cases/` are useful when a test fails: open your `.out.png` next to the
expected picture in `tests/`, or run the program again on the same input with the command the
checker prints after `reproduce:`.

If the build gets into a strange state, for example after you install a different compiler,
delete `build/solutions/`. The next check configures the project again from scratch, which
takes a few seconds longer.

The project's own `.gitignore` (in `solutions/`) lists `build/`, so if you put the project in
[Git](#primer/git), the build output stays out of it.

Learn more:
- [cmake command line: generate a project buildsystem](https://cmake.org/cmake/help/latest/manual/cmake.1.html#generate-a-project-buildsystem)
  on cmake.org, on source and build trees
- [Configuring your compiler: Build configurations](https://www.learncpp.com/cpp-tutorial/configuring-your-compiler-build-configurations/)
  on learncpp.com

## Debug builds and bounds checks
<!--
id: debug-build
also: Debug build; Release build; CMAKE_BUILD_TYPE; _GLIBCXX_ASSERTIONS; bounds checking; assertion failed; out of range
-->
A build type sets how the compiler treats your code. A Debug build keeps the program close to
the source. It has no optimisation, the compiler's rewriting of your code to run faster, and it
has debug information, a map from the machine code back to your lines and variable names. A
debugger, a tool such as GDB that runs a program a line at a time and shows its variables, needs
that map. A Release build optimises for speed. The project's `CMakeLists.txt` picks Debug unless
you choose another type.

In Debug it also defines the [macro](#primer/preprocessor) `_GLIBCXX_ASSERTIONS`, which makes
GCC's standard library check
indexes. Without it, `v[i]` with `i` past the end of a vector reads whatever memory is there,
and the program carries on with a wrong number. With it, the program stops at once:

```
.../stl_vector.h:1263: ... operator[](size_type) ...: Assertion '__n < this->size()' failed.
```

The program then exits through [`abort()`](#primer/exceptions), and the checker reports a
Runtime Error, "abort() - often a failed bounds check". That message is the clue: look for an
index one too far, such as reading [`loca`](#primer/loca) entry `numGlyphs` without allocating
`numGlyphs + 1` (04), or a [contour](#primer/contour) end used as a count instead of an index
(07). The message names the line inside the library, not
in your code; a debugger, or a print before the suspect line, finds yours.

The macro is part of GCC's library. Apple's clang on macOS uses a different library, which
ignores it, so there an out-of-range index may go unnoticed.

Learn more:
- [Macros (libstdc++ manual)](https://gcc.gnu.org/onlinedocs/libstdc++/manual/using_macros.html),
  on `_GLIBCXX_ASSERTIONS`
- [Configuring your compiler: Build configurations](https://www.learncpp.com/cpp-tutorial/configuring-your-compiler-build-configurations/)
  on learncpp.com
- [CMAKE_BUILD_TYPE](https://cmake.org/cmake/help/latest/variable/CMAKE_BUILD_TYPE.html) in the
  CMake documentation

## Running a program from the terminal
<!--
id: command-line
also: terminal; PowerShell; command line; shell; arguments; .\; ./; working directory; quoting; PATH
-->
A terminal (PowerShell on Windows, Terminal on macOS, a shell on Linux) runs programs by name,
followed by their arguments separated by spaces. Each assignment's program takes two, the input
file and the output file:

```
build\solutions\assignment_07.exe build\cases\07\07-R7-repeat.in out.txt
```

Things that trip people up:

- Run commands from the workbook folder. The checker does, and the test inputs name files
  relative to it (`file fonts/JetBrainsMonoNerdFont-Bold.ttf`). `cd` changes folder, and
  PowerShell shows the current one in its prompt.
- PowerShell won't run a program from the current folder by bare name: type `.\check 07`,
  not `check 07`. A path with a folder in it, such as `build\solutions\tiny_ttf.exe`, works as
  it is. On macOS and Linux the same rule needs `./check.sh 07`, and programs have no `.exe`.
- Put quotes around an argument that contains spaces, or it becomes several arguments:
  `tiny_ttf.exe font.ttf "Hello, TrueType!" hello.png` passes three arguments. The program sees
  the text without the quotes, in `argv[2]`.
- Forward slashes work in paths on Windows too, which is why the workbook's commands use them.

When a check fails, the checker prints the command that reproduces it, after `reproduce:`.
Paste that line to run your program on that one input, then open the output file or add prints
to your code (to `std::cerr`, so they don't mix with the answer).

Learn more:
- [about_Command_Syntax](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_command_syntax)
  on Microsoft Learn
- [Command line arguments](https://www.learncpp.com/cpp-tutorial/command-line-arguments/) on
  learncpp.com, with how to pass them from a terminal

## Exit codes
<!--
id: exit-codes
also: exit code; exit status; return code; $LASTEXITCODE; $?; 99; not implemented; Runtime Error; abort; access violation
-->
When a program ends, it hands the system a number, its exit code. 0 means success; anything
else means something went wrong, and the number says what. In C++ the exit code is the value
`main` returns. In PowerShell, `$LASTEXITCODE` holds the last program's exit code; on macOS and
Linux, `echo $?`.

The assignment programs use these codes, and the checker reads them:

| Code | Meaning | What the checker says |
|---|---|---|
| 0 | the answer is written | compares the output |
| 1 | an error was caught; the message is on stderr | Runtime Error, with the message |
| 2 | wrong arguments, or the input or output file can't be opened | Runtime Error |
| 99 | a function still throws "not implemented" | Not implemented yet: the function's name |
| 3 | `abort()` on Windows: an uncaught exception or a failed bounds check | Runtime Error |
| 0xC0000005 | access violation: a bad pointer or index (Windows) | Runtime Error |
| 0xC00000FD | stack overflow, often endless recursion (Windows) | Runtime Error |

99 is the workbook's own convention. Each unfinished function in the Boilerplate throws
[`std::logic_error`](#primer/stdexcept)`("not implemented: lerp")`, the program's `main`
catches it and returns 99, and the checker tells you which TODO to write next instead of
reporting a crash. A function you haven't reached yet doesn't count as a wrong answer.

The last three rows are crashes. On Windows a crash ends the program with a large code that
names the kind of crash. 0xC0000005 is an access violation: the program read or wrote memory
it doesn't own, through a bad [pointer](#primer/pointers) or an index past the end of a vector.
0xC00000FD is a stack overflow: the call stack, the memory that holds the variables of the
function calls in progress, ran out, usually through [recursion](#primer/recursion) that never
stops. Code 3 comes from [`abort()`](#primer/exceptions).

On macOS and Linux a crash shows as a signal instead, the system's notice that stops the
program: SIGSEGV (segmentation fault) for a bad memory access, SIGABRT for `abort()`, and
SIGFPE for an arithmetic error such as an integer division by zero. A program that runs longer
than 10 seconds is stopped and reported as `Time Limit Exceeded`.

Learn more:
- [Exit status](https://en.wikipedia.org/wiki/Exit_status) on Wikipedia
- [about_Automatic_Variables: $LASTEXITCODE](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_automatic_variables#lastexitcode)
  on Microsoft Learn
- [Halts (exiting your program early)](https://www.learncpp.com/cpp-tutorial/halts-exiting-your-program-early/)
  on learncpp.com, on status codes and `std::exit`

## The checker: `.\check`
<!--
id: checker
also: check; .\check; check.sh; check.py; -Case; -Fresh; -Dispute; -Run; -Ref; verdict; Accepted; Wrong Answer
-->
The checker builds your project, runs one assignment's program on every test case and compares
what it writes with the expected answer. From the workbook folder in PowerShell (`./check.sh`
on macOS and Linux):

```
.\check 07                          every test
.\check 07 -Case 07-R7-repeat       one test in full: input, expected output, your output
.\check 07 -Fresh                   a newly generated set of tests (a new random seed)
.\check 07 -Dispute <test-id> "why" set aside a test you believe is wrong
```

The checker needs your project folder first. From the workbook folder,
`py -P tools/project.py setup` creates `solutions/` with its `CMakeLists.txt`, `README.md`,
`.gitignore` and [`third_party/stb_image_write.h`](#primer/stb-image-write). Then
`.\check 01` on an assignment you haven't started creates its files and stops. They start as
the Boilerplate, the declarations and input/output code with `TODO`s for you to fill in (the
default, set by `project.starter` in `workbook.json`). Write them and run `.\check 01` again.
A coding assistant can do all of this for you, starting with a check of the tools, if you ask
it to "set up my workbook".

Once an assignment has its files, the verdict is `Accepted`, `Wrong Answer`,
`Compile Error`, `Runtime Error` or `Time Limit Exceeded`, or "Not implemented yet" while a
TODO remains (see
[exit codes](#primer/exit-codes)). For each failing test it shows the line that differs, the
requirement it most likely breaks, where the expected value came from and the command that
reproduces it. Text is compared word by word, so spacing and line endings don't matter. Pictures
may differ by one pixel along an edge, and a diff image marks the rest: red for extra pixels,
blue for missing ones, yellow for forgiven ones.

`-Fresh` checks your code on data it has never seen, so passing it means more than passing the
fixed tests. It needs Python's `fontTools` package, and for picture assignments it also builds
the reference program to draw the expected pictures.

`-Dispute` is for a test you think is wrong. The test stops counting (the verdict reads
`Accepted (1 disputed)`) and is saved in `disputes.json`; then ask your coding assistant to
"review my disputes". `-Run "<command> {input} {output}"` checks any other program, for
example one in another language.

`check.ps1`, `check.cmd` and `check.sh` all call `tools/check.py`. Run `.\check` with no
arguments for the full list of options.

Learn more:
- [Competitive programming](https://en.wikipedia.org/wiki/Competitive_programming) on
  Wikipedia, on the online judges this checker is modelled on
- [Python's fontTools](https://fonttools.readthedocs.io/en/latest/), which the test generators
  use to read fonts

## The study server: `.\study`
<!--
id: study-server
also: study; study.cmd; study.command; study.ps1; study.sh; serve.py; problem book; Run; Submit
-->
The study server lets the problem book in your browser run your code. Start it by
double-clicking `study.cmd` (Windows) or `study.command` (macOS), or with `.\study` in
PowerShell or `./study.sh` on macOS and Linux. It runs `tools/serve.py`, which:

- checks that the tools the build needs (g++, CMake, Ninja) are on your `PATH`, and tells you
  which one is missing;
- does the first-time build setup if it's needed, and offers to create your C++ project if
  there isn't one yet;
- opens the book at `http://127.0.0.1:8787/`. 127.0.0.1 is an address only your own computer
  can reach, and 8787 is the port, a number that tells apart the programs on one computer that
  answer web requests.

With the server running, the book's Run button checks the selected example, and Submit runs
every test. Both call [the checker](#primer/checker), the same as `.\check` in a terminal, and
the verdict appears in the Test result tab. Accepted marks the assignment solved. The book's
editor loads your project's files and saves them as you type, and it notices changes you make
in another editor. The Re-check solved button runs every solved assignment again, which shows
when a change has broken an earlier one.

Leave the server's window open while you work. To stop it, close the window, press Ctrl+C in
it, or use the book's Exit button. Without the server, `book/problem-book.html` still opens as
a page to read, but Run and Submit don't work.

The server can load and save the files of your project, start an assignment and run the
checker, and nothing else. `py -P tools/serve.py --port 8790` starts it on another port if 8787
is taken.

Learn more:
- [localhost](https://en.wikipedia.org/wiki/Localhost) on Wikipedia, on the 127.0.0.1 address

## Python and `py -P`
<!--
id: python
also: Python; py; python3; py launcher; -P; fontTools; pip
-->
The workbook's tools are written in Python: the checker, the study server, the project set-up
and the test generators. They need Python 3.11 or newer. You don't need to know Python to use
them; the `.\check` and `.\study` scripts start them for you.

On Windows the commands start with `py`. It comes from the Python install manager, Python's
current installer for Windows, which installs Python versions and starts the right one when you
type `py`. Older installs got `py` from the Python launcher, which did the second half of that
job. On macOS and Linux the same commands use `python3`:

```
py -P tools/check.py 07          (Windows)
python3 -P tools/check.py 07     (macOS, Linux)
```

To install Python on Windows, get the install manager from the Microsoft Store, from
[python.org/downloads](https://www.python.org/downloads/), or in PowerShell with
`winget install Python.PythonInstallManager`. Then `py install default` installs the latest
Python. Check it in a new PowerShell window with `py --version`, which prints the version `py`
starts.

`-P` tells Python not to add the script's own folder to the places it imports modules from, a
safety option added in Python 3.11, which is one reason for the version requirement.

`-Fresh` needs one extra package, fontTools, which reads font files. Install it with
`py -m pip install fonttools` (or `python3 -m pip install fonttools`). `-m pip` runs pip,
Python's package installer, with the same Python that `py` starts, so the package lands where
the workbook's tools look for it. Everything else uses only Python's standard library.

Two other tools are worth knowing. `py -P tools/project.py status` shows how far your project
is, and `py -P tools/langs.py` lists the programming languages installed on your computer, if
you want to do the workbook in another one.

Learn more:
- [Using Python on Windows: the Python install manager](https://docs.python.org/3/using/windows.html#python-install-manager)
  in the Python documentation, on the `py` command
- [Command line option -P](https://docs.python.org/3/using/cmdline.html#cmdoption-P) in the
  Python documentation
- [Installing packages](https://packaging.python.org/en/latest/tutorials/installing-packages/)
  in the Python Packaging User Guide

## Git and GitHub
<!--
id: git
also: Git; GitHub; repository; commit; push; version control; .gitignore
-->
Git is a version control system: it records snapshots of a folder, called commits, so you can
see what changed, go back to an earlier state and share the history. GitHub is a website that
hosts Git repositories.

The workbook doesn't need Git, but it suits the project. After the last assignment,
`solutions/` holds a complete TrueType renderer laid out like a normal C++ project, with its
own `CMakeLists.txt`, `README.md` and `.gitignore`, which you can put on GitHub as it is.
Committing after each accepted assignment also gives you a way back when a later change breaks
something.

```
cd solutions
git init
git add .
git commit -m "Assignment 07: decode simple glyphs"
```

The `.gitignore` lists `build/`, so build output stays out of the repository. To publish it,
create an empty repository on GitHub and follow the commands it shows to push your commits.

The folder `solutions/` is yours. If the workbook folder itself came from a Git repository (a
shared collection you cloned), keep your project's history separate from it, or ask your coding
assistant how the collection expects you to work.

Learn more:
- [Getting started: About version control](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control)
  in the Pro Git book
- [Git basics: Recording changes to the repository](https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository)
  in the Pro Git book
- [Creating a new repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)
  in the GitHub documentation
