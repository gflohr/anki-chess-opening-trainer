import sys
from yapf.yapflib.yapf_api import FormatCode

true = True
false = False
null = None

raw = f'schema = {eval(sys.stdin.read())}'
code, _ = FormatCode(raw, style_config='style.yapf')
code = code.replace('    ', '\t')
print(code)
