schema = {
	'$schema': 'http://json-schema.org/draft-07/schema#',
	'$id':
	'https://www.guido-flohr.net/schema/anki-chess-opening-trainer.json',
	'title': 'Config',
	'description': 'Configuration for the Anki Chess Opening Trainer Add-On',
	'type': 'object',
	'additionalProperties': False,
	'required': ['version', 'colour', 'decks', 'imports', 'notetype'],
	'properties': {
		'version': {
			'description':
			'The add-on version that has generated this configuration',
			'type':
			'string',
			'pattern':
			'^(?:0|[1-9][0-9]*)\\.(?:0|[1-9][0-9]*)\\.(?:0|[1-9][0-9]*)$'
		},
		'colour': {
			'description':
			'The side (black or white) that this game collection contains good moves for.',
			'type': 'string',
			'enum': ['white', 'black'],
			'default': 'white'
		},
		'decks': {
			'description': 'The currently selected deck for each colour.',
			'type': 'object',
			'additionalProperties': False,
			'required': ['white', 'black'],
			'properties': {
				'white': {
					'description': 'Currently selected deck for white',
					'type': ['integer', 'null'],
					'default': None,
					'minimum': 1
				},
				'black': {
					'description': 'Currently selected deck for black',
					'type': ['integer', 'null'],
					'default': None,
					'minimum': 1
				}
			}
		},
		'imports': {
			'type': 'object',
			'additionalProperties': False,
			'description': 'The previous imports by deck id',
			'patternProperties': {
				'[1-9][0-9]*': {
					'type': 'object',
					'additionalProperties': False,
					'description': 'One import',
					'properties': {
						'colour': {
							'type': 'string',
							'description':
							'The colour (either black or white)',
							'enum': ['black', 'white']
						},
						'files': {
							'type': 'array',
							'description': 'The list of imported file names',
							'items': {
								'type': 'string'
							}
						}
					},
					'required': ['colour', 'files']
				}
			}
		},
		'notetype': {
			'description': 'The notetype to use for card generation.',
			'type': ['integer', 'null'],
			'default': None,
			'minimum': 1
		}
	}
}
