async function runScenario(scenarioId) {
  const consoleBox = document.getElementById('simConsoleOutput');
  const status = document.getElementById('simCurrentStatus');
  
  status.innerText = 'Executing scenario: ' + scenarioId + '...';
  consoleBox.innerHTML = `[RevGuard Agent Pipeline Initiated]\n> Scenario: ${scenarioId}\n> Gathering live context signals & telemetry...\n> Querying user database e-KYC baseline...\n`;

  const formData = new FormData();
  formData.append('scenario_id', scenarioId);

  try {
    const res = await fetch('/api/simulator/run-scenario', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();

    status.innerText = 'Execution Complete: ' + data.scenario;
    consoleBox.innerHTML += `\n[Agent Execution Result]\n` + JSON.stringify(data, null, 2);
  } catch(err) {
    status.innerText = 'Error running scenario';
    consoleBox.innerHTML += `\n[ERROR]: ` + err;
  }
}
