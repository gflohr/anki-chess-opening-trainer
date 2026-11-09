# Configuration for Opening-Trainer<!-- omit in toc -->

This is not really a configuration but rather a cache for the last options you
have selection via the graphical user interface. It contains no
user-serviceable parts and this documentation serves informational purposes
only.

- [`version`](#version)
- [`colour`](#colour)
- [`decks`](#decks)
	- [`decks.white`](#deckswhite)
	- [`decks.black`](#decksblack)
- [`imports`](#imports)
	- [`imports.ID.colour`](#importsidcolour)
	- [`imports.ID.files`](#importsidfiles)
	- [`imports.ID.tag`](#importsidtag)
	- [`imports.ID.drop-variations`](#importsiddrop-variations)
- [`notetype`](#notetype)


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

A collection of previously imported PGN files. The keys are the deck ids
and the values are a data structure holding information about that particular
input. The deck id is denoted as `ID` in the following:

### `imports.ID.colour`

One of "black" or "white"

### `imports.ID.files`

This list of imported filenames.

### `imports.ID.tag`

An optional tag that is added to all notes in this opening.

### `imports.ID.drop-variations`

Boolean flag that controls whether variations should be dropped, and only
the main line of each game be imported.

## `notetype`

The note type that you had selected. This should be a note type with
two blank sides, each with exactly one field. This normally ships with Anki
and is called "Basic".
