"use strict";
async function loadExperimentResults() {
  let refresh = true;
  const set = (id, text) => { const node = document.getElementById(id); if (node.textContent !== text) node.textContent = text; };
  const minutes = n => `${(n / 60).toFixed(1)} min`;
  const number = n => Number(n).toLocaleString("en-US");
  const row = (values, heading = false) => {
    const tr = document.createElement("tr");
    values.forEach((value, i) => { const el = document.createElement(heading && i === 0 ? "th" : "td"); if (heading && i === 0) el.scope = "row"; el.textContent = value; tr.append(el); });
    return tr;
  };
  try {
    const response = await fetch("assets/experiments/unit-testing/results.json", {cache:"no-store"});
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const d = await response.json();
    refresh = d.status !== "complete";
    set("run-status", d.status_text);
    set("result-takeaway", d.takeaway);
    set("provenance", `Updated ${d.updated_at}. Model: ${d.model}; ${d.reasoning_effort} reasoning. ${d.manifest_sha256 ? `Frozen manifest SHA-256: ${d.manifest_sha256}.` : "Task selection is being validated."}`);
    if (!d.runs.length) return;
    document.getElementById("result-content").hidden = false;
    document.getElementById("empty-results").hidden = true;
    const chartUrl = `assets/experiments/unit-testing/results-chart.png?v=${encodeURIComponent(d.updated_at)}`;
    document.getElementById("result-chart").src = chartUrl;
    const chartDownload = document.querySelector('a[download][href^="assets/experiments/unit-testing/results-chart.png"]');
    if (chartDownload) chartDownload.href = chartUrl;
    set("metric-runs", `${d.evaluated} / ${d.planned}`);
    set("metric-coverage", `${d.task_count} selected issues · ${d.completed} completed agent runs`);
    set("metric-delta", d.paired_difference_pp === null ? "Pending" : `${d.paired_difference_pp > 0 ? "+" : ""}${d.paired_difference_pp.toFixed(1)} pp`);
    set("metric-regressions", d.regression.valid_reference ? `${d.regression.original_caught} / ${d.regression.valid_reference}` : "Pending");
    set("chart-caption", d.chart_caption);
    const a = d.arms["no-new-tests"], b = d.arms["write-tests"];
    const solved = arm => `${arm.solved} / ${arm.evaluated} evaluated${arm.evaluated ? ` (${(100*arm.solved/arm.evaluated).toFixed(1)}%)` : ""}`;
    const body = document.getElementById("aggregate-body");
    body.replaceChildren();
    [ ["Full acceptance passes", solved(a), solved(b)], ["Agent runs completed", `${a.completed} / ${a.scheduled}`, `${b.completed} / ${b.scheduled}`], ["Timeouts / infrastructure failures", `${a.timeouts} / ${a.errors}`, `${b.timeouts} / ${b.errors}`], ["Mean elapsed time (all attempts)", a.attempted ? minutes(a.mean_attempt_seconds) : "Pending", b.attempted ? minutes(b.mean_attempt_seconds) : "Pending"], ["Total input tokens reported", number(a.input_tokens), number(b.input_tokens)], ["Cached input tokens (included above)", number(a.cached_input_tokens), number(b.cached_input_tokens)], ["Total output tokens reported", number(a.output_tokens), number(b.output_tokens)], ["Policy compliant (audited)", `${a.compliant} / ${a.audited} audited`, `${b.compliant} / ${b.audited} audited`] ].forEach(values => body.append(row(values, true)));
    set("regression-detail", d.regression_text);
    set("statistical-note", d.statistical_note);
    const attempts = document.getElementById("attempt-body"); attempts.replaceChildren();
    for (const run of d.runs) attempts.append(row([run.instance_id.replace("sympy__sympy-", "SymPy #"), run.condition === "write-tests" ? "Write a test" : "No new tests", run.repetition, run.status === "infrastructure-error" ? "Infrastructure failure" : run.evaluation_error ? "Grader error" : `${run.solved ? "Solved" : "Not solved"}${run.status === "timeout" ? " · timed out" : ""}`, minutes(run.elapsed_seconds)]));
    if (d.bundle_available) document.getElementById("bundle-link").hidden = false;
  } catch (error) {
    set("run-status", "Results could not be loaded. Refresh or use the data links below.");
    console.error("Experiment results:", error);
  } finally {
    if (refresh) window.setTimeout(() => {
      if (document.hidden) {
        document.addEventListener("visibilitychange", loadExperimentResults, {once:true});
      } else loadExperimentResults();
    }, 30000);
  }
}
loadExperimentResults();
