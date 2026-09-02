document.addEventListener('DOMContentLoaded', async () => {
  const signals = await TelemetryEngine.getDeviceSignals();
  if (signals) {
    document.getElementById('telemetryGps').innerText = `${signals.gps_lat}, ${signals.gps_lng}`;
    document.getElementById('telemetryCity').innerText = signals.gps_city;
    document.getElementById('telemetryCanvas').innerText = signals.device_hash;
  }
});

function simulateDocUpload(input) {
  if (input.files && input.files[0]) {
    document.getElementById('uploadLabel').innerText = 'Selected: ' + input.files[0].name + ' (Vision AI Ready)';
  }
}

async function handleOnboardingSubmit(e) {
  e.preventDefault();
  const btn = document.getElementById('submitKycBtn');
  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>Vision AI Agent Verifying ID & Face...</span>';

  const signals = await TelemetryEngine.getDeviceSignals();

  const formData = new FormData();
  formData.append('name', document.getElementById('kycName').value);
  formData.append('email', document.getElementById('kycEmail').value);
  formData.append('phone', document.getElementById('kycPhone').value);
  formData.append('gov_id_type', document.getElementById('kycIdType').value);
  formData.append('gps_lat', signals.gps_lat);
  formData.append('gps_lng', signals.gps_lng);
  formData.append('gps_city', signals.gps_city);
  formData.append('ip_address', signals.ip_address);
  formData.append('device_hash', signals.device_hash);

  try {
    const res = await fetch('/api/kyc/onboard', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    
    if (data.success) {
      document.getElementById('onboardingForm').classList.add('hidden');
      const card = document.getElementById('kycSuccessCard');
      card.classList.remove('hidden');
      document.getElementById('resUserId').innerText = data.user_id;
      document.getElementById('resBioHash').innerText = data.biometric_hash;
      document.getElementById('resRiskScore').innerText = `${data.risk_baseline} / 100 (Safe)`;
    } else {
      alert('Onboarding failed: ' + data.message);
    }
  } catch(err) {
    alert('Error during onboarding: ' + err);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-user-shield"></i> <span>Process e-KYC & Generate Secure UserID</span>';
  }
}
