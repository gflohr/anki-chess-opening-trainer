#! /usr/bin/env python3

# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

# pylint: disable=invalid-name

from __future__ import annotations

import gettext
import os
import sys
from typing import Any

import chess.pgn
import chess.svg
import yaml
from anki.collection import Collection

from src.importer import Importer


def read_config() -> dict[str, Any]:
	with open('config.yaml', 'r', encoding='utf-8') as file:
		return yaml.safe_load(file)


def read_collection(directory: str) -> Collection:
	collection_path = os.path.join(directory, 'collection.anki2')
	if not os.path.exists(collection_path):
		raise KeyError(f"Collection '{collection_path}' does not exist")

	return Collection(collection_path)


if __name__ == '__main__':
	if len(sys.argv) < 3:
		print(f'Usage: {sys.argv[0]} WHITE|BLACK STUDY_PGN...',
		      file=sys.stderr)
		sys.exit(1)

	colour_arg = sys.argv[1].lower()[0]
	colour: chess.Color
	if colour_arg == 'w':
		colour = chess.WHITE
	else:
		colour = chess.BLACK

	config = read_config()

	localedir = os.path.join(os.path.dirname(__file__), 'locale')
	t = gettext.translation(
	    'anki-chess-opening-trainer',
	    localedir=localedir,
	    languages=[config['locale']],
	)
	t.install(names=['ngettext'])

	col = read_collection(config['anki']['path'])

	notetype: str = config['anki']['notetype']

	if colour == chess.WHITE:
		deck_name = config['anki']['decks']['white']
	else:
		deck_name = config['anki']['decks']['black']

	importer = Importer(filenames=sys.argv[2:],
	                    collection=col,
	                    colour=colour,
	                    deck_name=deck_name,
	                    notetype=notetype,
	                    do_print=True)

	[inserted, updated, deleted, images_inserted,
	 images_deleted] = importer.run()
	print(
	    ngettext('%d note inserted.', '%d notes inserted.', inserted) %
	    (inserted))
	print(
	    ngettext('%d note updated.', '%d notes updated.', updated) % (updated))
	print(
	    ngettext('%d note deleted.', '%d notes deleted.', deleted) % (deleted))
	print(
	    ngettext('%d image created.', '%d images created.', images_inserted) %
	    (images_inserted))
	print(
	    ngettext('%d image deleted.', '%d images deleted.', images_deleted) %
	    (images_deleted))
