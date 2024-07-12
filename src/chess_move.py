import re
import chess
from typing import Any, Dict, List

ARROWS_REGEX = re.compile(
    r"""
	(?P<prefix>[ \t\n\v\f\r]*?)
	\[%(?P<type>c[as]l)\s(?P<arrows>
		[RGYB]?[a-h][1-8](?:[a-h][1-8])?
		(?:[ \t\n\v\f\r]*,[ \t\n\v\f\r]*[RGYB]?[a-h][1-8](?:[a-h][1-8])?)*
	)\]
	(?P<postfix>[ \t\n\v\f\r]*?)
	""", re.VERBOSE)


class ChessMove:
	def __init__(self, move: chess.Move):
		self._move = move
		self._comments: List[str] = []
		self._nag = 0
		self._markers: List[str] = []

	@property
	def move(self):
		return self._move

	@property
	def comments(self):
		return self._comments

	def _process_markers(self, comment: str) -> str:
		def purge_markers(match):
			if not match.group() in self._markers:
				self._markers.append(match.group())

			return ''

		return re.sub(ARROWS_REGEX, purge_markers, comment)

	def add_comment(self, comment: str):
		comment = self._process_markers(comment)

		if not re.match('^[ \t\n\v\\f]*$', comment) and not comment in self._comments:
			self._comments.append(comment)

	@property
	def nag(self):
		return self._nag

	@nag.setter
	def nag(self, nag):
		self._nag = nag

	def dump(self) -> Dict[str, Any]:
		return {
			'move': str(self._move),
			'comments': self._comments,
			'nag': self._nag,
		}
