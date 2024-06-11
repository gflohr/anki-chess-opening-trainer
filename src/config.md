# Configuration for Opening-Trainer

This is not really a configuration but rather a cache for the last options you
have selection via the graphical user interface.  Consequently, all
modifications that you make here will be overwritten as soon as you import
another deck.

## `colour`

The last colour that you had selected, either "white" or "black".

## `decks`

This holds the last deck that you have selected for each colour of the board.

### `decks.white`
`
The last deck that you have selected for white.

### `decks.black`

The last deck that you have selected for black.

## `files`

This holds the last filenames for each colour.

### `files.white`

The last list of files you had selected for white.

### `files.white`

The last list of files you had selected for black.

## `notetype`

The last notetype that you have selected. This should be a note type with
two blank sides, each with exactly one field.  This normally ships with Anki
and is called "Basic".

# New Configuration for Chess Opening Trainer

This is not really a configuration but rather a cache for the last options you
have selection via the graphical user interface.  It contains no
user-serviceable parts and this documentation serves informational purposes
only.

## `version`

The version of the add-on that this configuration had been created with.

## `colour`

The last colour that you had selected, either `false` for "white" or
`true` for "black".

## `decks`

This holds the last deck that you have selected for each colour of the board.

### `decks.white`
`
The id of the last deck that you have selected for white.

### `decks.black`

The id of the last deck that you have selected for black.

## `imports`

A collection of previously imported PGN files.  The keys are the deck ids
and the values are a data structure holding information about that particular
input.  The deck id is denoted as `ID` in the following:

### `imports.ID.colour`

One of "black" or "white"

### `imports.ID.files`

This list of imported filenames.

## `notetype`

The note type that you had selected. This should be a note type with
two blank sides, each with exactly one field.  This normally ships with Anki
and is called "Basic".
