from src.pgn_import.collector import Collector


def test_collector_initialization() -> None:
	'''Test that the Collector initializes with an empty games dictionary.'''
	collector = Collector()

	assert isinstance(collector.games, dict)
	assert len(collector.games) == 0
