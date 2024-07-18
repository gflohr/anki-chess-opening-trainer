import * as path from 'path';
import * as fs from 'fs';
import { fileURLToPath } from 'url';
import Ajv from 'ajv';

let format = 'json';
if (process.argv.length > 2 && process.argv[2] === '--typescript') {
	format = 'typescript';
}
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const schema_file = path.join(__dirname, '..', 'src', 'config.schema.json');
const schema_json = fs.readFileSync(schema_file, { encoding: 'utf-8' })
const schema = JSON.parse(schema_json);

const ajv = new Ajv({ strict: true, useDefaults: true })
const validate = ajv.compile(schema);
const data = {};
if (!validate(data)) {
	throw validate.errors;
}

const formatted = JSON.stringify(data, null, '\t');
if (format == 'json') {
	console.log(formatted);
} else {
	console.log('// This file is generated! Do NOT edit!\n')
	console.log("import { type Config } from './config';\n");
	console.log(`export const defaultConfig: Config = ${formatted};`);
}
