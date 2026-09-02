async function execute1ClickPayment(token) {
  const btn = document.getElementById('payBtn');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>Processing Secure Razorpay UPI Rail...</span>';
  }

  try {
    const res = await fetch('/api/recovery/complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        recovery_token: token,
        payment_method: 'Razorpay UPI 1-Click (Recovered)'
      })
    });
    const data = await res.json();
    if (data.success) {
      document.getElementById('paymentActionsBox').classList.add('hidden');
      document.getElementById('recoverySuccessScreen').classList.remove('hidden');
      document.getElementById('recSuccessMsg').innerText = data.message;
    } else {
      alert('Payment failed: ' + data.message);
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-bolt text-amber-300"></i> <span>1-Click Pay via Razorpay UPI</span>';
      }
    }
  } catch(err) {
    alert('Error completing payment: ' + err);
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-bolt text-amber-300"></i> <span>1-Click Pay via Razorpay UPI</span>';
    }
  }
}

async function askCopilot(question) {
  document.getElementById('copilotInput').value = question;
  await handleCopilotSubmit(new Event('submit'));
}

async function handleCopilotSubmit(e) {
  if (e) e.preventDefault();
  const input = document.getElementById('copilotInput');
  const query = input.value.trim();
  if (!query) return;

  const chatBox = document.getElementById('copilotChatBox');

  // Append user message
  const userBubble = document.createElement('div');
  userBubble.className = 'bg-brand-600/30 border border-brand-500/30 p-2.5 rounded-xl text-white text-xs ml-4 text-right';
  userBubble.innerText = query;
  chatBox.appendChild(userBubble);
  input.value = '';
  chatBox.scrollTop = chatBox.scrollHeight;

  // Append typing indicator
  const typingBubble = document.createElement('div');
  typingBubble.className = 'bg-slate-950/70 border border-slate-800 p-2.5 rounded-xl text-slate-400 text-xs italic mr-4';
  typingBubble.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> RevGuard AI Copilot thinking...';
  chatBox.appendChild(typingBubble);
  chatBox.scrollTop = chatBox.scrollHeight;

  try {
    const res = await fetch('/api/recovery/copilot-chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question: query,
        recovery_token: window.RECOVERY_TOKEN
      })
    });
    const data = await res.json();
    typingBubble.className = 'bg-slate-950/70 border border-slate-800 p-3 rounded-xl text-slate-200 text-xs mr-4 space-y-1';
    typingBubble.innerHTML = `<div class="font-bold text-brand-400 text-[10px]">RevGuard AI Copilot</div><div>${data.answer}</div>`;
  } catch(err) {
    typingBubble.innerText = 'Unable to reach AI assistant right now.';
  }
  chatBox.scrollTop = chatBox.scrollHeight;
}
