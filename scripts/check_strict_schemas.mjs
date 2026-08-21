import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function filesBelow(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const target = path.join(directory, entry.name);
    if (entry.isDirectory()) return filesBelow(target);
    return entry.isFile() && entry.name.endsWith(".json") ? [target] : [];
  });
}

const schemas = [
  ...filesBelow(path.join(root, "schemas")).filter(
    (file) => !file.includes(`${path.sep}examples${path.sep}`),
  ),
  ...filesBelow(path.join(root, "specs", "extensions")).filter(
    (file) => path.basename(file) === "schema.json",
  ),
  ...filesBelow(path.join(root, "governance")).filter((file) =>
    file.endsWith(".schema.json"),
  ),
  ...filesBelow(path.join(root, "status")).filter((file) =>
    file.endsWith(".schema.json"),
  ),
].sort();

let failed = false;
for (const file of schemas) {
  const label = path.relative(root, file);
  try {
    const schema = JSON.parse(fs.readFileSync(file, "utf8"));
    const ajv = new Ajv2020({ allErrors: true, strict: true });
    addFormats(ajv);
    ajv.compile(schema);
    console.log(`strict schema OK: ${label}`);
  } catch (error) {
    failed = true;
    console.error(`strict schema FAILED: ${label}`);
    console.error(error instanceof Error ? error.message : String(error));
  }
}

if (failed) process.exitCode = 1;
