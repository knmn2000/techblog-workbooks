// Assignment 03: the checker runs this program as `node assignments/assignment_03_first_render.js <input-file> <output-file>`.
// It hands the scenario file to the harness together with the code under test.

import { render } from '../src/didact/renderSync.js'; // render (assignment 03): the recursive first draft under test
import { runScenarioFile } from '../harness/scenario.js'; // runScenarioFile: reads the scenario file, runs it against your code, writes the output file

await runScenarioFile(process.argv[2], process.argv[3], { render });
