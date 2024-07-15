import os

from anki.collection import Collection
from anki.notes import NotetypeId
from anki.models import TemplateDict

from .utils import get_addon_dir

name = 'Chess Opening Trainer'
template_name = 'Chess Opening Trainer Card'


def get_chess_model(collection: Collection) -> NotetypeId:
	models = collection.models
	model = models.by_name(name)
	if model is None:
		model = models.new(name)

	got = models.field_names(model)
	wanted = ['Moves', 'Responses', 'Line']

	dirty = False

	for field_name in wanted:
		if not field_name in got:
			field = models.new_field(field_name)
			models.add_field(model, field)
			dirty = True

	page_template = _get_page_template(collection)

	template_exists = [t for t in model['tmpls'] if t.get('name') == template_name]
	if template_exists:
		old_template = template_exists[0]
		if not old_template['qfmt'] == page_template['qfmt']:
			dirty = True
			old_template['qfmt'] = page_template['qfmt']
		if not old_template['afmt'] == page_template['afmt']:
			dirty = True
			old_template['afmt'] = page_template['afmt']
	else:
		dirty = True
		models.add_template(model, page_template)

	# New model?
	if model['id'] == 0:
		models.add_dict(model)
		model = models.by_name(name)
	elif dirty:
		models.update_dict(model)

	return model['id']

def _get_page_template(collection: Collection) -> TemplateDict:
	addon_dir = get_addon_dir()
	filename = os.path.join(addon_dir, 'assets', 'html', 'page.html')
	with open(filename, 'r') as file:
		html = file.read()

	# Always replace the addon URL.
	html = html.replace(
		'{{addon}}',
		__name__.split('.')[0]
	)

	template = collection.models.new_template(template_name)

	template['qfmt'] = '{{Moves}}'

	template['afmt'] = '{{Responses}}'

	return template
