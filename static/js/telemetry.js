// Real-time Browser Telemetry & Device Fingerprint Harvester
const TelemetryEngine = {
  getCanvasFingerprint: function() {
    try {
      const canvas = document.createElement('canvas');
      canvas.width = 200;
      canvas.height = 50;
      const ctx = canvas.getContext('2d');
      ctx.textBaseline = 'top';
      ctx.font = "14px 'Arial'";
      ctx.fillStyle = '#f60';
      ctx.fillRect(125, 1, 62, 20);
      ctx.fillStyle = '#069';
      ctx.fillText('RevGuard-Telemetry-2026', 2, 15);
      ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
      ctx.fillText('Secure-Identity-Sig', 4, 17);
      
      const b64 = canvas.toDataURL();
      let hash = 0;
      for (let i = 0; i < b64.length; i++) {
        const char = b64.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash |= 0;
      }
      return 'canvas_fp_' + Math.abs(hash).toString(16);
    } catch(e) {
      return 'canvas_fp_generic_' + Math.floor(Math.random() * 100000);
    }
  },

  getDeviceSignals: async function() {
    const canvasHash = this.getCanvasFingerprint();
    const signals = {
      user_agent: navigator.userAgent,
      screen_res: `${window.screen.width}x${window.screen.height}`,
      color_depth: `${window.screen.colorDepth}-bit`,
      language: navigator.language || 'en-US',
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Kolkata',
      device_hash: canvasHash,
      gps_lat: 12.9716, // Default baseline coords
      gps_lng: 77.5946,
      gps_city: 'Bengaluru, India',
      ip_address: '103.21.124.55',
      is_vpn: false
    };

    // Attempt live browser geolocation if permitted
    if ('geolocation' in navigator) {
      try {
        const pos = await new Promise((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 2500 });
        });
        if (pos && pos.coords) {
          signals.gps_lat = parseFloat(pos.coords.latitude.toFixed(4));
          signals.gps_lng = parseFloat(pos.coords.longitude.toFixed(4));
        }
      } catch(err) {
        // Fallback to baseline default
      }
    }

    return signals;
  }
};
window.TelemetryEngine = TelemetryEngine;
