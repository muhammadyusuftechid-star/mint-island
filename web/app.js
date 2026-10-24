/**
 * Mint-Island Official Commercial Website
 * Interactive Dynamic Island Simulator & Landing Page Logic
 *
 * Modern Web Best Practices:
 * - Event delegation & efficient DOM updates
 * - Smooth CSS class toggling matching compositor animations
 * - Real-time synced karaoke lyrics simulation
 * - Interactive hardware HMAC license key validation demo
 * - Instant checkout modal flow
 */

(function () {
  'use strict';

  // ==========================================
  // 1. Clock Engine (Syncs System Time)
  // ==========================================
  function updateClocks() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const timeStr = `${hours}:${minutes}`;

    const mockClock = document.getElementById('mock-clock');
    const islandClock = document.getElementById('island-clock');

    if (mockClock) mockClock.textContent = timeStr;
    if (islandClock) islandClock.textContent = timeStr;
  }

  setInterval(updateClocks, 1000);
  updateClocks();

  // ==========================================
  // 2. Interactive Island Simulator Engine
  // ==========================================
  const island = document.getElementById('live-island');
  const viewIdle = document.getElementById('view-idle');
  const viewHud = document.getElementById('view-hud');
  const viewExpanded = document.getElementById('view-expanded');

  // HUD elements
  const hudIcon = document.getElementById('hud-icon');
  const hudTitle = document.getElementById('hud-title');
  const hudFill = document.getElementById('hud-fill');
  const hudVal = document.getElementById('hud-val');

  // Simulator Toolbar Buttons
  const btnIdle = document.getElementById('sim-btn-idle');
  const btnVol = document.getElementById('sim-btn-vol');
  const btnBright = document.getElementById('sim-btn-bright');
  const btnBattery = document.getElementById('sim-btn-battery');
  const btnMusic = document.getElementById('sim-btn-music');
  const allSimBtns = [btnIdle, btnVol, btnBright, btnBattery, btnMusic];

  let currentSimState = 'idle';
  let hudAutoDismissTimer = null;

  function setActiveSimBtn(activeBtn) {
    allSimBtns.forEach(btn => {
      if (btn) btn.classList.remove('active');
    });
    if (activeBtn) activeBtn.classList.add('active');
  }

  function hideAllViews() {
    if (viewIdle) viewIdle.style.display = 'none';
    if (viewHud) viewHud.style.display = 'none';
    if (viewExpanded) viewExpanded.style.display = 'none';
    if (island) {
      island.classList.remove('state-idle', 'state-hud', 'state-expanded');
    }
  }

  function setSimulatorState(state, options = {}) {
    if (!island) return;
    if (hudAutoDismissTimer) {
      clearTimeout(hudAutoDismissTimer);
      hudAutoDismissTimer = null;
    }

    currentSimState = state;
    hideAllViews();

    switch (state) {
      case 'idle':
        island.classList.add('state-idle');
        if (viewIdle) viewIdle.style.display = 'flex';
        setActiveSimBtn(btnIdle);
        break;

      case 'vol':
        island.classList.add('state-hud');
        if (viewHud) viewHud.style.display = 'flex';
        if (hudIcon) hudIcon.textContent = '🔊';
        if (hudTitle) hudTitle.textContent = 'Volume';
        const volVal = options.val !== undefined ? options.val : 72;
        if (hudFill) hudFill.style.width = `${volVal}%`;
        if (hudVal) hudVal.textContent = `${volVal}%`;
        setActiveSimBtn(btnVol);

        // Auto-shrink back to idle after 3.2s HUD timeout
        hudAutoDismissTimer = setTimeout(() => {
          setSimulatorState('idle');
        }, 3200);
        break;

      case 'bright':
        island.classList.add('state-hud');
        if (viewHud) viewHud.style.display = 'flex';
        if (hudIcon) hudIcon.textContent = '☀️';
        if (hudTitle) hudTitle.textContent = 'Brightness';
        const brightVal = options.val !== undefined ? options.val : 85;
        if (hudFill) hudFill.style.width = `${brightVal}%`;
        if (hudVal) hudVal.textContent = `${brightVal}%`;
        setActiveSimBtn(btnBright);

        hudAutoDismissTimer = setTimeout(() => {
          setSimulatorState('idle');
        }, 3200);
        break;

      case 'battery':
        island.classList.add('state-hud');
        if (viewHud) viewHud.style.display = 'flex';
        if (hudIcon) hudIcon.textContent = '⚡';
        if (hudTitle) hudTitle.textContent = 'AC Connected (Charging)';
        const batVal = options.val !== undefined ? options.val : 94;
        if (hudFill) hudFill.style.width = `${batVal}%`;
        if (hudVal) hudVal.textContent = `${batVal}%`;
        setActiveSimBtn(btnBattery);

        hudAutoDismissTimer = setTimeout(() => {
          setSimulatorState('idle');
        }, 3200);
        break;

      case 'music':
        island.classList.add('state-expanded');
        if (viewExpanded) viewExpanded.style.display = 'flex';
        setActiveSimBtn(btnMusic);
        startKaraokePlayback();
        break;
    }
  }

  // Hook simulator buttons
  if (btnIdle) btnIdle.addEventListener('click', () => setSimulatorState('idle'));
  if (btnVol) btnVol.addEventListener('click', () => setSimulatorState('vol', { val: 76 }));
  if (btnBright) btnBright.addEventListener('click', () => setSimulatorState('bright', { val: 85 }));
  if (btnBattery) btnBattery.addEventListener('click', () => setSimulatorState('battery', { val: 92 }));
  if (btnMusic) btnMusic.addEventListener('click', () => setSimulatorState('music'));

  // Clicking on island directly expands or minimizes
  if (island) {
    island.addEventListener('click', (e) => {
      // Don't trigger if clicked on child control buttons
      if (e.target.closest('.ctrl-btn')) return;

      if (currentSimState === 'idle') {
        setSimulatorState('music');
      } else if (currentSimState === 'expanded' || currentSimState === 'music') {
        setSimulatorState('idle');
      }
    });

    island.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        island.click();
      }
    });
  }

  // ==========================================
  // 3. Karaoke Lyrics Synchronization Engine
  // ==========================================
  const lyricLyrics = [
    { time: 0, text: 'Is this the real life?' },
    { time: 3, text: 'Is this just fantasy? 🎤' },
    { time: 6, text: 'Caught in a landslide, no escape from reality' },
    { time: 11, text: 'Open your eyes, look up to the skies and see...' },
    { time: 16, text: "I'm just a poor boy, I need no sympathy" },
    { time: 21, text: "Because I'm easy come, easy go, little high, little low" },
    { time: 28, text: "Anyway the wind blows doesn't really matter to me, to me" },
    { time: 35, text: 'Mama, just killed a man... 🎶' },
    { time: 42, text: 'Put a gun against his head, pulled my trigger, now he is dead' },
    { time: 49, text: 'Mama, life had just begun...' },
    { time: 55, text: 'But now I have gone and thrown it all away!' }
  ];

  let currentLyricIndex = 1;
  let isPlaying = true;
  let songSeconds = 24; // starting at 00:24
  const songTotalSeconds = 354; // 05:54
  let karaokeInterval = null;

  const lyricPrevEl = document.getElementById('lyric-prev');
  const lyricCurrEl = document.getElementById('lyric-curr');
  const lyricNextEl = document.getElementById('lyric-next');
  const pillLyricEl = document.getElementById('island-pill-lyric');
  const curTimeEl = document.getElementById('cur-time');
  const totTimeEl = document.getElementById('tot-time');
  const musicProgressEl = document.getElementById('music-progress');
  const btnPlay = document.getElementById('btn-play');
  const btnPrev = document.getElementById('btn-prev');
  const btnNext = document.getElementById('btn-next');

  function formatTime(secs) {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  }

  function updateKaraokeUI() {
    const prev = lyricLyrics[currentLyricIndex - 1] ? lyricLyrics[currentLyricIndex - 1].text : '—';
    const curr = lyricLyrics[currentLyricIndex] ? lyricLyrics[currentLyricIndex].text : '—';
    const next = lyricLyrics[currentLyricIndex + 1] ? lyricLyrics[currentLyricIndex + 1].text : '—';

    if (lyricPrevEl) lyricPrevEl.textContent = prev;
    if (lyricCurrEl) lyricCurrEl.textContent = curr;
    if (lyricNextEl) lyricNextEl.textContent = next;

    if (pillLyricEl) {
      pillLyricEl.style.display = 'inline-block';
      pillLyricEl.textContent = `🎵 ${curr}`;
    }

    if (curTimeEl) curTimeEl.textContent = formatTime(songSeconds);
    if (totTimeEl) totTimeEl.textContent = formatTime(songTotalSeconds);

    const progressPct = ((songSeconds / songTotalSeconds) * 100).toFixed(1);
    if (musicProgressEl) musicProgressEl.style.width = `${progressPct}%`;
  }

  function nextLyric() {
    if (currentLyricIndex < lyricLyrics.length - 1) {
      currentLyricIndex++;
    } else {
      currentLyricIndex = 0;
      songSeconds = 0;
    }
    updateKaraokeUI();
  }

  function prevLyric() {
    if (currentLyricIndex > 0) {
      currentLyricIndex--;
    } else {
      currentLyricIndex = lyricLyrics.length - 1;
    }
    updateKaraokeUI();
  }

  function startKaraokePlayback() {
    if (karaokeInterval) clearInterval(karaokeInterval);
    isPlaying = true;
    if (btnPlay) btnPlay.textContent = '⏸';

    karaokeInterval = setInterval(() => {
      if (!isPlaying) return;
      songSeconds += 1;

      // Check if we hit the next lyric threshold
      if (
        currentLyricIndex < lyricLyrics.length - 1 &&
        songSeconds >= lyricLyrics[currentLyricIndex + 1].time
      ) {
        currentLyricIndex++;
      } else if (songSeconds >= 60) {
        // loop back for demo
        songSeconds = 0;
        currentLyricIndex = 0;
      }

      updateKaraokeUI();
    }, 1000);
  }

  if (btnPlay) {
    btnPlay.addEventListener('click', (e) => {
      e.stopPropagation();
      isPlaying = !isPlaying;
      btnPlay.textContent = isPlaying ? '⏸' : '▶';
    });
  }

  if (btnPrev) {
    btnPrev.addEventListener('click', (e) => {
      e.stopPropagation();
      prevLyric();
    });
  }

  if (btnNext) {
    btnNext.addEventListener('click', (e) => {
      e.stopPropagation();
      nextLyric();
    });
  }

  // Initialize lyric text
  updateKaraokeUI();

  // ==========================================
  // 4. Terminal Quick Install Copy Button
  // ==========================================
  const btnCopyInstall = document.getElementById('btn-copy-install');
  const copyText = document.getElementById('copy-text');
  const copyIcon = document.getElementById('copy-icon');
  const cmdInstall = document.getElementById('cmd-install');

  if (btnCopyInstall && cmdInstall) {
    btnCopyInstall.addEventListener('click', async () => {
      const textToCopy = cmdInstall.textContent.trim();
      try {
        await navigator.clipboard.writeText(textToCopy);
        if (copyText) copyText.textContent = 'Copied!';
        if (copyIcon) copyIcon.textContent = '✅';
        btnCopyInstall.classList.add('copied');

        setTimeout(() => {
          if (copyText) copyText.textContent = 'Copy';
          if (copyIcon) copyIcon.textContent = '📋';
          btnCopyInstall.classList.remove('copied');
        }, 2200);
      } catch (err) {
        console.error('Failed to copy command:', err);
      }
    });
  }

  // Copy helper for any .btn-copy elements in download cards
  document.querySelectorAll('.copy-cmd-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const targetId = btn.getAttribute('data-target');
      const targetEl = document.getElementById(targetId);
      if (!targetEl) return;

      try {
        await navigator.clipboard.writeText(targetEl.textContent.trim());
        const originalText = btn.textContent;
        btn.textContent = 'Copied! ✓';
        setTimeout(() => {
          btn.textContent = originalText;
        }, 2000);
      } catch (e) {
        console.error('Copy failed:', e);
      }
    });
  });

  // ==========================================
  // 5. Interactive Demo License Key Validator
  // ==========================================
  window.validateDemoKey = function () {
    const input = document.getElementById('demo-key-input');
    const resultBox = document.getElementById('tryout-result');
    if (!input || !resultBox) return;

    const rawKey = input.value.trim().toUpperCase();

    if (!rawKey) {
      resultBox.style.display = 'block';
      resultBox.className = 'tryout-result error';
      resultBox.innerHTML = `
        <span class="res-badge red">ERROR</span>
        <span>Please enter a license key to verify (try: <code>ISL-DEV-PROTEST-2026</code>).</span>
      `;
      return;
    }

    // Check key format or test key
    const isValidFormat = rawKey.startsWith('ISL-PRO-') || rawKey.startsWith('ISL-DEV-') || rawKey === 'ISL-DEV-PROTEST-2026';

    if (isValidFormat) {
      const mockHmac = 'a7f3c9e1...4b2d (HMAC-SHA256 Machine Token)';
      resultBox.style.display = 'block';
      resultBox.className = 'tryout-result success';
      resultBox.innerHTML = `
        <div class="result-header">
          <span class="res-badge green">VALID PRO LICENSE ✅</span>
          <span class="res-title">Key Authenticated via Cryptographic Hardware Signature</span>
        </div>
        <div class="result-details">
          <div><strong>License Key:</strong> <code>${rawKey}</code></div>
          <div><strong>Hardware Token:</strong> <code>${mockHmac}</code></div>
          <div><strong>Status:</strong> Active (3/3 Activations Remaining) • Pro Features Unlocked</div>
        </div>
      `;

      // Trigger simulator celebration
      setSimulatorState('music');
      const pillLyric = document.getElementById('island-pill-lyric');
      if (pillLyric) {
        pillLyric.style.display = 'inline-block';
        pillLyric.textContent = '🌟 PRO LICENSE ACTIVE';
      }
    } else {
      resultBox.style.display = 'block';
      resultBox.className = 'tryout-result error';
      resultBox.innerHTML = `
        <div class="result-header">
          <span class="res-badge red">INVALID LICENSE KEY ✖</span>
          <span class="res-title">Format mismatch or checksum failed</span>
        </div>
        <div class="result-details">
          <span>Expected pattern: <code>ISL-PRO-XXXX-YYYY</code> or test with <code>ISL-DEV-PROTEST-2026</code>.</span>
        </div>
      `;
    }
  };

  // ==========================================
  // 6. Checkout Modal & Purchase Simulator
  // ==========================================
  const modal = document.getElementById('checkout-modal');

  window.openCheckoutModal = function () {
    if (modal) {
      modal.style.display = 'flex';
      document.body.style.overflow = 'hidden'; // prevent scroll behind modal
      const emailInput = document.getElementById('buyer-email');
      if (emailInput) setTimeout(() => emailInput.focus(), 100);
    }
  };

  window.closeCheckoutModal = function () {
    if (modal) {
      modal.style.display = 'none';
      document.body.style.overflow = '';
    }
  };

  window.closeModalOnBackdrop = function (e) {
    if (e.target === modal) {
      window.closeCheckoutModal();
    }
  };

  window.handleCheckoutSubmit = function (e) {
    e.preventDefault();
    const emailInput = document.getElementById('buyer-email');
    const submitBtn = document.getElementById('btn-confirm-checkout');
    const modalBody = document.querySelector('.modal-body');

    if (!emailInput || !submitBtn || !modalBody) return;

    const email = emailInput.value.trim();
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span>Processing Secure Order... ⏳</span>`;

    setTimeout(() => {
      // Generate a mock realistic license key
      const randHex = Math.random().toString(36).substring(2, 6).toUpperCase();
      const generatedKey = `ISL-PRO-${randHex}-2026`;

      modalBody.innerHTML = `
        <div class="checkout-success-box">
          <div class="success-icon">🎉</div>
          <h4 class="success-title">Payment Successful!</h4>
          <p class="success-desc">Thank you! Your Mint-Island Pro Lifetime license has been issued and sent to <strong>${email}</strong>.</p>
          
          <div class="generated-key-box">
            <span class="key-label">Your Personal License Key:</span>
            <code class="key-val" id="generated-key">${generatedKey}</code>
            <button class="btn btn-secondary btn-sm" onclick="navigator.clipboard.writeText('${generatedKey}'); this.textContent='Copied! ✓';">Copy Key</button>
          </div>

          <div class="activation-instructions">
            <h5>How to Activate on Linux Mint:</h5>
            <ol>
              <li>Open <strong>Mint-Island Control Panel</strong> → <strong>Lisensi & Aktivasi</strong></li>
              <li>Paste your key and click <strong>Aktifkan Lisensi Pro</strong></li>
              <li>Or run in your terminal:</li>
            </ol>
            <div class="terminal-inline">
              <code>mint-island --activate ${generatedKey}</code>
            </div>
          </div>

          <button class="btn btn-primary btn-block" onclick="window.closeCheckoutModal(); window.location.hash='#simulator';">
            Return to Mint-Island & Try Features
          </button>
        </div>
      `;
    }, 1400);
  };

  // Close modal with Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal && modal.style.display === 'flex') {
      window.closeCheckoutModal();
    }
  });

  // Smooth scroll helper for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#' || targetId === '#pricing' && this.id === 'btn-hero-buy') {
        // Let normal anchor jump or modal happen
        return;
      }
      const targetEl = document.querySelector(targetId);
      if (targetEl) {
        e.preventDefault();
        targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

})();
