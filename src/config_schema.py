# This file is generated! Do NOT edit!

config_schema = {
	'$schema': 'http://json-schema.org/draft-07/schema#',
	'$id':
	'https://www.guido-flohr.net/schema/anki-chess-opening-trainer-config.json',
	'title': 'Config',
	'description': 'Configuration for the Anki Chess Opening Trainer Add-On',
	'type': 'object',
	'additionalProperties': False,
	'required': ['version', 'board'],
	'properties': {
		'version': {
			'description':
			'The add-on version that has generated this configuration.',
			'type': 'string',
			'minLength': 5,
			'default': '0.0.0'
		},
		'board': {
			'description': 'The board style',
			'type': 'object',
			'additionalProperties': False,
			'required': ['3D', '2Dpieces', '2Dboard', '3Dpieces', '3Dboard'],
			'properties': {
				'3D': {
					'description': 'Whether to use a 3D board.',
					'type': 'boolean',
					'default': False
				},
				'2Dpieces': {
					'description':
					'Style for 2D pieces',
					'type':
					'string',
					'enum': [
						'alpha', 'anarcandy', 'caliente', 'california',
						'cardinal', 'cburnett', 'celtic', 'chess7', 'chessnut',
						'companion', 'cooke', 'disguised', 'dubrovny',
						'fantasy', 'fresca', 'gioco', 'governor', 'horsey',
						'icpieces', 'kiwen-suwi', 'kosal', 'leipzig', 'letter',
						'libra', 'maestro', 'merida', 'monarchy', 'mpchess',
						'pirouetti', 'pixel', 'reillycraig', 'riohacha',
						'shapes', 'spatial', 'staunty', 'tatiana'
					],
					'default':
					'cburnett'
				},
				'2Dboard': {
					'description':
					'Style for 2D board',
					'type':
					'string',
					'enum': [
						'blue-marble', 'blue2', 'blue3', 'canvas2',
						'green-plastic', 'grey', 'horsey', 'leather', 'maple',
						'maple2', 'marble', 'metal', 'olive', 'pink-pyramid',
						'purple-diag', 'svg/blue', 'svg/brown', 'svg/green',
						'svg/ic', 'svg/newspaper', 'svg/purple', 'wood',
						'wood2', 'wood3', 'wood4'
					],
					'default':
					'blue3'
				},
				'3Dpieces': {
					'description':
					'Style for 3D pieces',
					'type':
					'string',
					'enum': [
						'Basic', 'CubesAndPi', 'Experimental', 'Glass',
						'Metal', 'ModernJade', 'ModernWood', 'RedVBlue',
						'Staunton', 'Trimmed', 'Wood'
					],
					'default':
					'Basic'
				},
				'3Dboard': {
					'description':
					'Style for 3D board',
					'type':
					'string',
					'enum': [
						'Black-White-Aluminium', 'Brushed-Aluminium',
						'China-Blue', 'China-Green', 'China-Grey',
						'China-Scarlet', 'China-Yellow', 'Classic-Blue',
						'Glass', 'Gold-Silver', 'Green-Glass', 'Jade',
						'Light-Wood', 'Marble', 'Power-Coated', 'Purple-Black',
						'Rosewood', 'Wax', 'Wood-Glass', 'Woodi'
					],
					'default':
					'Black-White-Aluminium'
				}
			},
			'default': {}
		}
	}
}

