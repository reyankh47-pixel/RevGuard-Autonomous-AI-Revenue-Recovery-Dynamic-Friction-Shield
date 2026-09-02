let currentProduct = null;
let currentOrderId = null;

function initiateCheckout(id, name, price) {
  currentProduct = { id, name, price };
  currentOrderId = 'ORD-' + Math.floor(100000 + Math.random() * 900000);
  
  document.getElementById('checkoutItemName').innerText = name;
  document.getElementById('checkoutItemPrice').innerText = '₹' + price.toLocaleString('en-IN', {minimumFractionDigits: 2});
  
  document.getElementById('stageSummary').classList.remove('hidden');
  document.getElementById('stageEvaluation').classList.add('hidden');
  document.getElementById('stepUpChallengeBox').classList.add('hidden');
  
  document.getElementById('checkoutModal').classList.remove('hidden');
}

function closeCheckoutModal() {
  document.getElementById('checkoutModal').classList.add('hidden');
}

async function executeRiskEvaluation(forceStepUp = false) {
  const userSelect = document.getElementById('userSelector');
  const userId = userSelect.value;
  const simulateGeo = document.getElementById('simulateGeoDrift').checked;
  const simulateVpn = document.getElementById('simulateVpn').checked;

  const rawTelemetry = await TelemetryEngine.getDeviceSignals();

  // Apply user-selected simulation toggles
  if (simulateGeo) {
    rawTelemetry.gps_lat = 28.6139; // Delhi (1,700km from Bangalore)
    rawTelemetry.gps_lng = 77.2090;
    rawTelemetry.gps_city = 'Delhi, India (Simulated Drift)';
  }
  if (simulateVpn) {
    rawTelemetry.is_vpn = true;
    rawTelemetry.ip_address = '185.220.101.5 (Datacenter VPN)';
  }

  const payload = {
    user_id: userId,
    order_id: currentOrderId,
    amount: currentProduct ? currentProduct.price : 4999.0,
    payment_method: document.querySelector('input[name="paymentOption"]:checked')?.value || 'UPI',
    telemetry: rawTelemetry
  };

  try {
    const res = await fetch('/api/checkout/evaluate-risk', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    renderEvaluationResults(data);
  } catch(err) {
    alert('Error evaluating risk: ' + err);
  }
}

function renderEvaluationResults(data) {
  document.getElementById('stageSummary').classList.add('hidden');
  document.getElementById('stageEvaluation').classList.remove('hidden');

  const badge = document.getElementById('evalStatusBadge');
  const challengeBox = document.getElementById('stepUpChallengeBox');
  const reasonsList = document.getElementById('aiReasonsList');
  const score = data.risk_score;

  let badgeHtml = '';
  if (data.decision === 'APPROVED_SAFE') {
    badgeHtml = `
      <div class="inline-flex p-3 rounded-full bg-emerald-500/20 text-emerald-400 mb-2">
        <i class="fa-solid fa-circle-check text-2xl"></i>
      </div>
      <h4 class="text-base font-bold text-white">Payment Approved (Zero Friction)</h4>
      <div class="flex items-center justify-center space-x-2 text-xs font-mono">
        <span class="text-slate-400">AI Risk Score:</span>
        <span class="font-bold text-emerald-400">${score} / 100 (Safe)</span>
      </div>
      <p class="text-xs text-slate-300 mt-2">${data.explainable_log.summary}</p>
    `;
    challengeBox.classList.add('hidden');
  } else if (data.decision === 'DYNAMIC_FRICTION_REQUIRED') {
    badgeHtml = `
      <div class="inline-flex p-3 rounded-full bg-amber-500/20 text-amber-400 mb-2">
        <i class="fa-solid fa-triangle-exclamation text-2xl"></i>
      </div>
      <h4 class="text-base font-bold text-white">Dynamic Step-Up Friction Required</h4>
      <div class="flex items-center justify-center space-x-2 text-xs font-mono">
        <span class="text-slate-400">AI Risk Score:</span>
        <span class="font-bold text-amber-400">${score} / 100 (Suspicious)</span>
      </div>
      <p class="text-xs text-slate-300 mt-2">${data.explainable_log.summary}</p>
    `;
    challengeBox.classList.remove('hidden');
  } else {
    badgeHtml = `
      <div class="inline-flex p-3 rounded-full bg-rose-500/20 text-rose-400 mb-2">
        <i class="fa-solid fa-shield-xmark text-2xl"></i>
      </div>
      <h4 class="text-base font-bold text-white">Transaction Blocked (Fraud Prevented)</h4>
      <div class="flex items-center justify-center space-x-2 text-xs font-mono">
        <span class="text-slate-400">AI Risk Score:</span>
        <span class="font-bold text-rose-400">${score} / 100 (Critical)</span>
      </div>
      <p class="text-xs text-slate-300 mt-2">${data.explainable_log.summary}</p>
    `;
    challengeBox.classList.add('hidden');
  }
  badge.innerHTML = badgeHtml;

  // Render Explainable AI reasons
  reasonsList.innerHTML = '<div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1 flex items-center space-x-1"><i class="fa-solid fa-brain text-brand-400"></i><span>Explainable AI Signals Log:</span></div>' +
    data.explainable_log.reasons.map(r => `
      <div class="text-xs bg-slate-950/60 border border-slate-800 rounded-lg p-2 flex items-start space-x-2 text-slate-300">
        <i class="fa-solid fa-circle-dot text-[10px] text-brand-400 mt-1"></i>
        <span>${r}</span>
      </div>
    `).join('');
}

async function submitStepUpVerification(type) {
  const code = type === 'OTP' ? (document.getElementById('stepUpOtpInput').value || '4321') : 'VALID_SELFIE';
  try {
    const res = await fetch('/api/checkout/verify-step-up', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        order_id: currentOrderId,
        verification_type: type,
        code_or_hash: code
      })
    });
    const data = await res.json();
    if (data.success) {
      alert('🎉 Step-Up Verification Passed! Order #' + currentOrderId + ' is successfully completed.');
      closeCheckoutModal();
    } else {
      alert('❌ Verification Failed: ' + data.message);
    }
  } catch(e) {
    alert('Verification error: ' + e);
  }
}

async function abandonStepUpFriction() {
  if (confirm('Simulate customer hesitating and dropping off during step-up friction? This will trigger the autonomous AI Revenue Recovery Agent!')) {
    await simulateFailure('FRICTION_DROPOUT', 'Customer hesitated at OTP step-up challenge');
  }
}

async function simulateFailure(reason, detail) {
  const userId = document.getElementById('userSelector').value;
  try {
    const res = await fetch('/api/recovery/trigger', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        order_id: currentOrderId,
        failure_reason: reason,
        failure_detail: detail,
        user_id: userId
      })
    });
    const data = await res.json();
    if (data.success) {
      closeCheckoutModal();
      window.location.href = data.recovery_url;
    }
  } catch(e) {
    alert('Error triggering recovery: ' + e);
  }
}
