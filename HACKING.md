# Hacking

If you want to play around with the sources, or if you want to contribute
to the project, follow the steps described below.

The instructions are tested on macOS. They should work on other Un*x systems
as well. Instructions for Windows are from hear-say only.

## Prerequisites

You need:

- `uv`
- Python 3.12 or better
- Anki
- `make`

## Setup

### Virtual Environment

Create a virtual environment:

```sh
uv venv
```

### Activate the Virtual Environment

Source the activation script:

```sh
source ./.venv/bin/activate
```

On Windows, do one of the following:

```sh
.\.venv\Scripts\activate.ps1
.\.venv\Scripts\activate.bat
```

You have to do that in every shell that you are using for development.

### Install Dependencies

```sh
uv sync --all-groups 
```

### Run Tests

```sh
make test
```

### Terminate all Other Anki Instances

Anki may just switch the focused window, if another version of it is already
running.

### Run Local Anki

Test that you can run Anki locally in your virtual environment:

```sh
uv run anki --version
```

That should print the Anki version. Ignore warnings about failure to load some
`ankihelper` shared library.

### Generate Initial Configuration

You have to generate some files initially. This is done by the `Makefile`.

```sh
make
```

Verify that `src/basic_names.py`, `src/config.py`, and `src/version.py` exists.

### Create Data Directories

You should create at least one data directory, and use it instead of your
actual Anki data:

```sh
mkdir -p ankidata-local/addons21
ln -s ../../src ankidata-local/addons21/
uv run anki --base ankidata-local
```

### Run Development Version

Test the setup:

```sh
uv run anki --base ankidata-local
```

If Anki prompts you to update to a more recent version, do _not_ update.
Update the Anki version by modifying the entries in `requirements/dev.txt`.

Verify that the addon is listed (with its id 705507113 instead of the name)
under `Tools` -> `Add-Ons` and that the menu entry `Tools` -> `Chess Opening
Trainer` exists.

### Run Tests

The tests are best run from the `Makefile`:

```
make test
```

### Update Anki

To update Anki to a more recent version, edit `requirements/dev.txt` and
change the version numbers for `anki` and `aqt`. Then re-install the
dependencies:

```sh
uv sync --all-groups
```
