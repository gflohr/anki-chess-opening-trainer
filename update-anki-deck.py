from __future__ import annotations

import gettext
import os
import sys
import yaml
from typing import Any
import chess.pgn
import chess.svg
from anki.collection import Collection
from importer import Importer


def read_config() -> dict[str, Any]:
	with open('config.yaml', 'r') as file:
		config = yaml.safe_load(file)
		return config

def read_collection(dir: str) -> Collection:
	collection_path = os.path.join(dir, 'collection.anki2')
	if not os.path.exists(collection_path):
		raise Exception(f"Collection '{collection_path}' does not exist")

	return Collection(collection_path)


if __name__ == '__main__':
	if len(sys.argv) < 3:
		print(f'Usage: {sys.argv[0]} WHITE|BLACK STUDY_PGN...', file=sys.stderr)
		sys.exit(1)

	colour_arg = sys.argv[1].lower()[0]
	if colour_arg == 'w':
		colour: chess.Color = chess.WHITE
	else:
		colour: chess.Color = chess.BLACK

	config = read_config()

	localedir = os.path.join(os.path.dirname(__file__), 'locale')
	t = gettext.translation('opening-trainer', localedir=localedir, languages=[config['locale']])
	t.install(names=['ngettext'])

	col = read_collection(config['anki']['path'])

	notetype: str = config['anki']['notetype']

	if (colour == chess.WHITE):
		deck_name = config['anki']['decks']['white']
	else:
		deck_name = config['anki']['decks']['black']

	importer = Importer(
		filenames=sys.argv[2:],
		collection=col,
		colour=colour,
		deck_name=deck_name,
		notetype=notetype,
	)

	[inserted, updated, deleted, images_inserted, images_deleted] = importer.run()
	print(ngettext('%d note inserted.', '%d notes inserted.', inserted) % (inserted))
	print(ngettext('%d note updated.', '%d notes updated.', updated) % (updated))
	print(ngettext('%d note deleted.', '%d notes deleted.', deleted) % (deleted))
	print(ngettext('%d image created.', '%d images created.', images_inserted) % (images_inserted))
	print(ngettext('%d image deleted.', '%d images deleted.', images_deleted) % (images_deleted))

