import re
import json
from glob import glob

# This script compiles the current set of assets into the configuration schema.
# It would be smarter to use the $ref keyword and just generate the snippets
# but the JavaScript and Python schema validators disagree about their usage.

id = 'https://www.guido-flohr.net/schema/anki-chess-opening-trainer.json'

piece_css_2d = glob('public/assets/css/pieces/*.css')
piece_css_2d = [re.sub('\\.css$', '', p) for p in piece_css_2d]
piece_css_2d = [re.sub('^public/assets/css/pieces/', '', p) for p in piece_css_2d]
piece_css_2d = sorted(piece_css_2d)

board_image_2d = list(map(
	lambda thumb: thumb.replace('.thumbnail.', '.'),
	glob('assets/images/2d/board/*.thumbnail.*')
))
board_image_2d.extend(glob('assets/images/2d/board/svg/*.svg'))
board_image_2d = [re.sub('\\.[^.]+$', '', p) for p in board_image_2d]
board_image_2d = [re.sub('^assets/images/2d/board/', '', p) for p in board_image_2d]
board_image_2d = sorted(board_image_2d)

piece_images_3d = glob('assets/images/3d/piece/*')
piece_images_3d = [re.sub('^assets/images/3d/piece/', '', p) for p in piece_images_3d]
piece_images_3d = sorted(piece_images_3d)

board_image_3d = list(map(
	lambda thumb: thumb.replace('.thumbnail.', '.'),
	glob('assets/images/3d/board/*.thumbnail.*')
))
board_image_3d = [re.sub('\\.[^.]+$', '', p) for p in board_image_3d]
board_image_3d = [re.sub('^assets/images/3d/board/', '', p) for p in board_image_3d]
board_image_3d = sorted(board_image_3d)

schema = {
	'$schema': 'http://json-schema.org/draft-07/schema#',
	'$id': 'https://www.guido-flohr.net/schema/anki-chess-opening-trainer-config.json',
	'title': 'Config',
	'description': 'Configuration for the Anki Chess Opening Trainer Add-On',
	'type': 'object',
	'additionalProperties': False,
	'required': ['version', 'board' ],
	'properties': {
		'version': {
			'description': 'The add-on version that has generated this configuration.',
			'type': 'string',
			'minLength': 5,
			'default': '0.0.0',
		},
		'board': {
			'description': 'The board style',
			'type': 'object',
			'additionalProperties': False,
			'required': ['3D', '2Dpieces', '2Dboard', '3Dpieces', '3Dboard' ],
			'properties': {
				'3D': {
					'description': 'Whether to use a 3D board.',
					'type': 'boolean',
					'default': False,
				},
				'2Dpieces': {
					'description': 'Style for 2D pieces',
					'type': 'string',
					'enum': piece_css_2d,
					'default': 'cburnett',
				},
				'2Dboard': {
					'description': 'Style for 2D board',
					'type': 'string',
					'enum': board_image_2d,
					'default': 'blue3',
				},
				'3Dpieces': {
					'description': 'Style for 3D pieces',
					'type': 'string',
					'enum': piece_images_3d,
					'default': 'Basic',
				},
				'3Dboard': {
					'description': 'Style for 3D board',
					'type': 'string',
					'enum': board_image_3d,
					'default': 'Black-White-Aluminium',
				},
			},
			'default': {},
		},
	},
}

print(json.dumps(schema, indent='\t'))

