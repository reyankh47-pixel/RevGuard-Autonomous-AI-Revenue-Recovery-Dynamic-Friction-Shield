document.addEventListener('DOMContentLoaded', () => {
  loadDashboardData();
  // Auto refresh every 5 seconds
  setInterval(loadDashboardData, 5000);
});

async function refreshDashboard() {
  const icon = document.getElementById('refreshIcon');
  if (icon) icon.classList.add('fa-spin');
  await loadDashboardData();
  if (icon) setTimeout(() => icon.classList.remove('fa-spin'), 600);
}

async function loadDashboardData() {
  try {
    const [statsRes, eventsRes, workflowsRes] = await Promise.all([
      fetch('/api/dashboard/stats'),
      fetch('/api/dashboard/events'),
      fetch('/api/dashboard/workflows')
    ]);

    const stats = await statsRes.json();
    const eventsData = await eventsRes.json();
    const workflowsData = await workflowsRes.json();

    renderStats(stats);
    renderWorkflows(workflowsData.workflows || []);
    renderEvents(eventsData.events || []);
  } catch(err) {
    console.error('Error fetching dashboard data:', err);
  }
}

function renderStats(stats) {
  document.getElementById('statAtRisk').innerText = '₹' + stats.total_at_risk.toLocaleString('en-IN', {minimumFractionDigits: 2});
  document.getElementById('statAtRiskCount').innerText = `${stats.total_at_risk_count} failed/abandoned orders`;
  
  document.getElementById('statRecovered').innerText = '₹' + stats.total_recovered.toLocaleString('en-IN', {minimumFractionDigits: 2});
  document.getElementById('statRecoveredCount').innerText = `${stats.total_recovered_count} recovered transactions`;

  document.getElementById('statRecoveryRate').innerText = `${stats.recovery_rate}%`;

  document.getElementById('statFraud').innerText = '₹' + stats.fraud_prevented.toLocaleString('en-IN', {minimumFractionDigits: 2});
  document.getElementById('statFraudCount').innerText = `${stats.fraud_count} malicious blocks`;
}

function renderWorkflows(workflows) {
  const tbody = document.getElementById('workflowsTableBody');
  if (!workflows || workflows.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="p-6 text-center text-slate-500">No active recovery workflows yet. Trigger a payment failure in the Store or Test Lab.</td></tr>';
    return;
  }

  tbody.innerHTML = workflows.map(wf => {
    const isCompleted = wf.status === 'COMPLETED';
    const statusBadge = isCompleted
      ? '<span class="px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold">RECOVERED</span>'
      : '<span class="px-2.5 py-1 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 text-[10px] font-bold animate-pulse">ACTIVE RECOVERY</span>';

    return `
      <tr class="hover:bg-slate-800/40 transition-colors">
        <td class="p-4">
          <div class="font-bold text-white font-mono text-xs">${wf.order_id}</div>
          <div class="text-slate-400 text-[11px]">${wf.user_name || 'Customer'} (${wf.user_id})</div>
        </td>
        <td class="p-4">
          <div class="font-semibold text-slate-200">${wf.strategy_type.replace(/_/g, ' ')}</div>
          <div class="text-[11px] text-brand-400 flex items-center space-x-1">
            <i class="fa-brands fa-${wf.channel_dispatched.toLowerCase() === 'whatsapp' ? 'whatsapp text-emerald-400' : 'envelope'}"></i>
            <span>Dispatched via ${wf.channel_dispatched}</span>
          </div>
        </td>
        <td class="p-4">
          <div class="text-white font-bold">₹${wf.recovery_amount.toLocaleString('en-IN', {minimumFractionDigits: 2})}</div>
          <div class="text-slate-500 line-through text-[11px]">₹${wf.original_amount.toLocaleString('en-IN', {minimumFractionDigits: 2})}</div>
        </td>
        <td class="p-4">
          <div class="font-bold text-brand-400">${wf.recovery_probability}%</div>
          <div class="text-[10px] text-slate-500">AI Est. Success</div>
        </td>
        <td class="p-4">
          ${statusBadge}
        </td>
        <td class="p-4 text-right">
          <a href="/recover/${wf.recovery_token}" target="_blank" class="inline-flex items-center space-x-1 px-3 py-1.5 bg-brand-500/20 hover:bg-brand-500/40 text-brand-300 border border-brand-500/30 rounded-lg text-xs font-semibold transition-all">
            <span>Open Link</span>
            <i class="fa-solid fa-arrow-up-right-from-square text-[10px]"></i>
          </a>
        </td>
      </tr>
    `;
  }).join('');
}

function renderEvents(events) {
  const container = document.getElementById('telemetryStreamList');
  if (!events || events.length === 0) {
    container.innerHTML = '<p class="text-xs text-slate-500">Awaiting real-time telemetry events...</p>';
    return;
  }

  container.innerHTML = events.map(ev => {
    let iconClass = 'fa-brain text-brand-400';
    let borderClass = 'border-slate-800';

    if (ev.event_type.includes('SUCCESS') || ev.event_type.includes('RECOVERED')) {
      iconClass = 'fa-circle-check text-emerald-400';
      borderClass = 'border-emerald-500/20 bg-emerald-950/10';
    } else if (ev.event_type.includes('DISPATCHED') || ev.event_type.includes('FRICTION')) {
      iconClass = 'fa-bolt text-amber-400';
      borderClass = 'border-amber-500/20 bg-amber-950/10';
    } else if (ev.action_taken === 'BLOCKED_FRAUD') {
      iconClass = 'fa-shield-xmark text-rose-400';
      borderClass = 'border-rose-500/30 bg-rose-950/10';
    }

    return `
      <div class="p-3.5 rounded-xl border ${borderClass} bg-slate-950/60 text-xs space-y-1.5">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2 font-bold text-white">
            <i class="fa-solid ${iconClass}"></i>
            <span>${ev.event_type.replace(/_/g, ' ')}</span>
          </div>
          <span class="text-[10px] font-mono text-slate-500">${ev.created_at || 'Just now'}</span>
        </div>
        <div class="text-slate-300">
          Order: <span class="font-mono text-brand-400">${ev.order_id || 'N/A'}</span> &bull; Action: <span class="font-semibold text-white">${ev.action_taken}</span>
        </div>
        ${ev.details && ev.details.reasons ? `
          <div class="text-[11px] text-slate-400 border-t border-slate-800/80 pt-1.5 mt-1">
            ${ev.details.reasons.slice(0, 2).map(r => `<div>&bull; ${r}</div>`).join('')}
          </div>
        ` : ''}
        ${ev.details && ev.details.ai_rationale ? `
          <div class="text-[11px] text-indigo-300 border-t border-slate-800/80 pt-1.5 mt-1 italic">
            AI Rationale: ${ev.details.ai_rationale}
          </div>
        ` : ''}
      </div>
    `;
  }).join('');
}
