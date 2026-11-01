// Assignment 12: the checker runs this program as `node assignments/assignment_12_todo_app.js <input-file> <output-file>`.
// It hands the scenario file to the harness together with the code under test.

import '../harness/env.js'; // first: installs document and a requestIdleCallback the tests control, before the library loads
import Didact from '../src/didact/index.js'; // Didact: the library under test
import { TodoApp } from '../src/app/TodoApp.js'; // TodoApp (assignment 12): the application under test
import { runScenarioFile } from '../harness/scenario.js'; // runScenarioFile: reads the scenario file, runs it against your code, writes the output file

await runScenarioFile(process.argv[2], process.argv[3], { ...Didact, components: { TodoApp } });
