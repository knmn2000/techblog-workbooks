// batch.mjs - runs many scenarios against real React in one process.
//
//   node tools/oracle/batch.mjs < jobs.json > results.json
//
// jobs.json is a list of {"text": "<scenario text>", "todo": true|false (optional)}. The result is a list, in
// the same order, of {"lines": [...]} or {"error": "<message>"}. Starting jsdom and React costs more than
// running a scenario, so the generators send all their scenarios in one call.

import { runOracle, closeOracle } from "./run.mjs";

const chunks = [];
for await (const chunk of process.stdin) chunks.push(chunk);
const jobs = JSON.parse(Buffer.concat(chunks).toString("utf8"));

const results = [];
for (const job of jobs) {
  const warnings = [];
  try {
    const lines = await runOracle(job.text, { todo: job.todo, warnings });
    results.push({ lines, warnings });
  } catch (err) {
    const where = err?.scenarioLine ? `scenario line ${err.scenarioLine} (${err.scenarioText}): ` : "";
    results.push({ error: where + (err?.message ?? String(err)) });
  }
}
await closeOracle();
process.stdout.write(JSON.stringify(results));
