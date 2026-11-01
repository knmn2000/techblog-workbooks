// Assignment 01: the checker runs this program as `node assignments/assignment_01_create_element.js <input-file> <output-file>`.
// It hands the scenario file to the harness together with the code under test.

import { createElement } from '../src/didact/createElement.js'; // createElement (assignment 01): the function under test
import { runScenarioFile } from '../harness/scenario.js'; // runScenarioFile: reads the scenario file, runs it against your code, writes the output file

await runScenarioFile(process.argv[2], process.argv[3], { createElement });
