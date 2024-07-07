import json

with open('package.json', 'r') as file:
	pkg = json.load(file)
	version = pkg['version']
	print(f"__version__ = '{version}'")
