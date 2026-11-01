// Assignment 02: the checker runs this program as `node assignments/assignment_02_dom_props.js <input-file> <output-file>`.
// It hands the scenario file to the harness together with the code under test.

import { createDom, updateDom } from '../src/didact/dom.js'; // createDom and updateDom (assignment 02): the functions under test
import { runScenarioFile } from '../harness/scenario.js'; // runScenarioFile: reads the scenario file, runs it against your code, writes the output file

await runScenarioFile(process.argv[2], process.argv[3], { createDom, updateDom });
