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
						'blue-marble', 'blue-marble.thumbnail', 'blue2',
						'blue2.thumbnail', 'blue3', 'blue3.thumbnail',
						'canvas2', 'canvas2.thumbnail', 'green-plastic',
						'green-plastic.thumbnail', 'grey', 'grey.thumbnail',
						'horsey', 'horsey.current-premove', 'horsey.last-move',
						'horsey.move-dest', 'horsey.selected',
						'horsey.thumbnail', 'leather', 'leather.thumbnail',
						'maple', 'maple.thumbnail', 'maple2',
						'maple2.thumbnail', 'marble', 'marble.thumbnail',
						'metal', 'metal.thumbnail', 'ncf-board', 'olive',
						'olive.thumbnail', 'pink-pyramid',
						'pink-pyramid.thumbnail', 'purple-diag',
						'purple-diag.thumbnail', 'svg/blue', 'svg/brown',
						'svg/green', 'svg/ic', 'svg/newspaper', 'svg/purple',
						'wood', 'wood.thumbnail', 'wood2', 'wood2.thumbnail',
						'wood3', 'wood3.thumbnail', 'wood4', 'wood4.thumbnail'
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
						'Black-White-Aluminium',
						'Black-White-Aluminium.thumbnail', 'Brushed-Aluminium',
						'Brushed-Aluminium.thumbnail', 'China-Blue',
						'China-Blue.thumbnail', 'China-Green',
						'China-Green.thumbnail', 'China-Grey',
						'China-Grey.thumbnail', 'China-Scarlet',
						'China-Scarlet.thumbnail', 'China-Yellow',
						'China-Yellow.thumbnail', 'Classic-Blue',
						'Classic-Blue.thumbnail', 'Glass', 'Glass.thumbnail',
						'Gold-Silver', 'Gold-Silver.thumbnail', 'Green-Glass',
						'Green-Glass.thumbnail', 'Jade', 'Jade.thumbnail',
						'Light-Wood', 'Light-Wood.thumbnail', 'Marble',
						'Marble.thumbnail', 'Power-Coated',
						'Power-Coated.thumbnail', 'Purple-Black',
						'Purple-Black.thumbnail', 'Rosewood',
						'Rosewood.thumbnail', 'Wax', 'Wax.thumbnail',
						'Wood-Glass', 'Wood-Glass.thumbnail', 'Woodi',
						'Woodi.thumbnail'
					],
					'default':
					'Black-White-Aluminium'
				}
			},
			'default': {}
		}
	}
}

