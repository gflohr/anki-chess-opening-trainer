from typing import Any, Dict


class Collector:
	'''Collects and aggregates PGN chess games for Anki note generation.'''

	def __init__(self):
		self.games: Dict[str, Any] = {}
