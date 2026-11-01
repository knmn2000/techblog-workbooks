// Assignment 09: the checker runs this program as `node assignments/assignment_09_function_components.js <input-file> <output-file>`.
// It hands the scenario file to the harness together with the code under test.

import '../harness/env.js'; // first: installs document and a requestIdleCallback the tests control, before the library loads
import Didact from '../src/didact/index.js'; // Didact: the library under test
import { runScenarioFile } from '../harness/scenario.js'; // runScenarioFile: reads the scenario file, runs it against your code, writes the output file

await runScenarioFile(process.argv[2], process.argv[3], Didact);
