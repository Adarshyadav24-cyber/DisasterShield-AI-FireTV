/**
 * DisasterShield AI - Fire TV Spatial Navigation & Remote Control Engine
 * Provides 10-foot 2D spatial navigation for Fire TV D-pad, Android TV Leanback,
 * and keyboard arrow keys, with virtual remote simulation and audio feedback.
 */

class TVNavigationEngine {
  constructor() {
    this.currentFocused = null;
    this.historyStack = [];
    this.soundEnabled = true;
    this.audioCtx = null;
    this.virtualRemoteVisible = true;
    
    // Key codes
    this.KEYS = {
      UP: [38, 'ArrowUp', 'Up'],
      DOWN: [40, 'ArrowDown', 'Down'],
      LEFT: [37, 'ArrowLeft', 'Left'],
      RIGHT: [39, 'ArrowRight', 'Right'],
      ENTER: [13, 'Enter', 'Select', 'Accept'],
      BACK: [8, 27, 461, 10009, 'Backspace', 'Escape', 'GoBack', 'Back'],
      FAST_FWD: [228, 'FastForward'],
      REWIND: [227, 'Rewind'],
      INFO: [170, 73, 'i', 'KeyI'],
      REMOTE_TOGGLE: [82, 'r', 'KeyR']
    };
  }

  init() {
    this.bindEvents();
    this.createAudioContext();
    this.setupVirtualRemote();
    
    // Auto-focus the first navigable element
    setTimeout(() => {
      this.focusFirstAvailable();
    }, 150);
  }

  createAudioContext() {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        this.audioCtx = new AudioContext();
      }
    } catch (e) {
      console.warn('AudioContext not supported on this platform', e);
    }
  }

  playFocusSound() {
    if (!this.soundEnabled || !this.audioCtx) return;
    try {
      if (this.audioCtx.state === 'suspended') {
        this.audioCtx.resume();
      }
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(440, this.audioCtx.currentTime); // A4
      osc.frequency.exponentialRampToValueAtTime(880, this.audioCtx.currentTime + 0.04);
      gain.gain.setValueAtTime(0.04, this.audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.audioCtx.currentTime + 0.04);
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start();
      osc.stop(this.audioCtx.currentTime + 0.045);
    } catch (e) {}
  }

  playSelectSound() {
    if (!this.soundEnabled || !this.audioCtx) return;
    try {
      if (this.audioCtx.state === 'suspended') {
        this.audioCtx.resume();
      }
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(523.25, this.audioCtx.currentTime); // C5
      osc.frequency.exponentialRampToValueAtTime(1046.5, this.audioCtx.currentTime + 0.08); // C6
      gain.gain.setValueAtTime(0.07, this.audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.audioCtx.currentTime + 0.08);
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start();
      osc.stop(this.audioCtx.currentTime + 0.085);
    } catch (e) {}
  }

  bindEvents() {
    window.addEventListener('keydown', (e) => this.handleKeyDown(e), { passive: false });
    
    // Also track pointer focus to keep synchronized
    document.addEventListener('focusin', (e) => {
      if (this.isFocusable(e.target)) {
        this.setFocus(e.target, false);
      }
    });

    // Handle window resize for TV viewport
    window.addEventListener('resize', () => {
      if (this.currentFocused) {
        this.ensureVisible(this.currentFocused);
      }
    });
  }

  isKey(event, keyType) {
    const list = this.KEYS[keyType];
    return list.includes(event.keyCode) || list.includes(event.key) || list.includes(event.code);
  }

  handleKeyDown(e) {
    // If active in a standard text input and typing, let typing work
    if (this.currentFocused && this.currentFocused.tagName === 'INPUT' && !this.isKey(e, 'BACK')) {
      if (!this.isKey(e, 'UP') && !this.isKey(e, 'DOWN')) {
        return;
      }
    }

    if (this.isKey(e, 'UP')) {
      e.preventDefault();
      this.moveDirection('UP');
    } else if (this.isKey(e, 'DOWN')) {
      e.preventDefault();
      this.moveDirection('DOWN');
    } else if (this.isKey(e, 'LEFT')) {
      e.preventDefault();
      this.moveDirection('LEFT');
    } else if (this.isKey(e, 'RIGHT')) {
      e.preventDefault();
      this.moveDirection('RIGHT');
    } else if (this.isKey(e, 'ENTER')) {
      e.preventDefault();
      this.handleSelect();
    } else if (this.isKey(e, 'BACK')) {
      e.preventDefault();
      this.handleBack();
    } else if (this.isKey(e, 'REMOTE_TOGGLE')) {
      // Toggle virtual remote visibility
      this.toggleVirtualRemote();
    }
  }

  getFocusableElements() {
    // Look inside active screen / modal
    const activeModal = document.querySelector('.tv-modal.active');
    const container = activeModal || document.querySelector('.screen.active') || document.body;
    
    const selector = [
      'button:not([disabled]):not([style*="display: none"])',
      '[tabindex="0"]',
      'a[href]',
      'input:not([disabled]):not([type="hidden"])',
      'select:not([disabled])',
      '.tv-focusable:not(.disabled)'
    ].join(',');

    const elements = Array.from(container.querySelectorAll(selector));
    
    // Also include top navigation bar buttons if no modal is active
    if (!activeModal) {
      const navButtons = Array.from(document.querySelectorAll('.tv-nav-bar button, .header-action-btn'));
      for (const btn of navButtons) {
        if (!elements.includes(btn)) elements.push(btn);
      }
    }

    return elements.filter(el => {
      const style = window.getComputedStyle(el);
      return style.display !== 'none' && style.visibility !== 'hidden' && el.offsetWidth > 0 && el.offsetHeight > 0;
    });
  }

  isFocusable(el) {
    if (!el) return false;
    const focusables = this.getFocusableElements();
    return focusables.includes(el);
  }

  setFocus(el, shouldPlaySound = true) {
    if (!el) return;
    
    if (this.currentFocused && this.currentFocused !== el) {
      this.currentFocused.classList.remove('tv-focused');
      this.currentFocused.blur();
    }

    this.currentFocused = el;
    el.classList.add('tv-focused');
    el.focus({ preventScroll: true });
    this.ensureVisible(el);

    if (shouldPlaySound) {
      this.playFocusSound();
    }

    // Trigger custom focus listener if provided
    if (typeof el.onTVFocus === 'function') {
      el.onTVFocus();
    }
  }

  ensureVisible(el) {
    if (!el) return;
    el.scrollIntoView({
      behavior: 'smooth',
      block: 'nearest',
      inline: 'nearest'
    });
  }

  focusFirstAvailable() {
    const focusables = this.getFocusableElements();
    if (focusables.length > 0) {
      // Prefer elements marked default-focus
      const defaultEl = focusables.find(el => el.classList.contains('default-focus')) || focusables[0];
      this.setFocus(defaultEl, false);
    }
  }

  handleSelect() {
    if (this.currentFocused) {
      this.playSelectSound();
      this.currentFocused.classList.add('tv-pressed');
      setTimeout(() => {
        if (this.currentFocused) {
          this.currentFocused.classList.remove('tv-pressed');
        }
      }, 180);

      // Execute click
      this.currentFocused.click();
    }
  }

  handleBack() {
    this.playSelectSound();
    // Check if modal is open
    const openModal = document.querySelector('.tv-modal.active');
    if (openModal) {
      if (window.TVApp && typeof window.TVApp.closeModal === 'function') {
        window.TVApp.closeModal();
      } else {
        openModal.classList.remove('active');
        this.focusFirstAvailable();
      }
      return;
    }

    // Check if on sub-screen -> go back to Home
    if (window.TVApp && window.TVApp.currentScreen !== 'home') {
      window.TVApp.navigateTo('home');
      return;
    }

    // Show exit confirmation toast
    if (window.TVApp && typeof window.TVApp.showToast === 'function') {
      window.TVApp.showToast('Press Back again to exit DisasterShield AI', 'info');
    }
  }

  moveDirection(direction) {
    const focusables = this.getFocusableElements();
    if (focusables.length === 0) return;

    if (!this.currentFocused || !focusables.includes(this.currentFocused)) {
      this.focusFirstAvailable();
      return;
    }

    const currentRect = this.currentFocused.getBoundingClientRect();
    const currentCenter = {
      x: currentRect.left + currentRect.width / 2,
      y: currentRect.top + currentRect.height / 2
    };

    let bestCandidate = null;
    let minDistance = Infinity;

    for (const candidate of focusables) {
      if (candidate === this.currentFocused) continue;

      const candRect = candidate.getBoundingClientRect();
      const candCenter = {
        x: candRect.left + candRect.width / 2,
        y: candRect.top + candRect.height / 2
      };

      const dx = candCenter.x - currentCenter.x;
      const dy = candCenter.y - currentCenter.y;

      let isCandidateInDirection = false;
      let primaryDiff = 0;
      let secondaryDiff = 0;

      switch (direction) {
        case 'UP':
          isCandidateInDirection = dy < -8;
          primaryDiff = Math.abs(dy);
          secondaryDiff = Math.abs(dx);
          break;
        case 'DOWN':
          isCandidateInDirection = dy > 8;
          primaryDiff = Math.abs(dy);
          secondaryDiff = Math.abs(dx);
          break;
        case 'LEFT':
          isCandidateInDirection = dx < -8;
          primaryDiff = Math.abs(dx);
          secondaryDiff = Math.abs(dy);
          break;
        case 'RIGHT':
          isCandidateInDirection = dx > 8;
          primaryDiff = Math.abs(dx);
          secondaryDiff = Math.abs(dy);
          break;
      }

      if (isCandidateInDirection) {
        // Weighted distance metric favors elements along primary axis
        const weightedDist = primaryDiff + (secondaryDiff * 1.8);
        if (weightedDist < minDistance) {
          minDistance = weightedDist;
          bestCandidate = candidate;
        }
      }
    }

    if (bestCandidate) {
      this.setFocus(bestCandidate, true);
    }
  }

  setupVirtualRemote() {
    // Creates an on-screen Fire TV Remote controller for desktop evaluation
    const remote = document.createElement('div');
    remote.id = 'firetv-virtual-remote';
    remote.className = 'virtual-remote';
    remote.innerHTML = `
      <div class="remote-header">
        <span class="remote-title">🎮 Fire TV Remote</span>
        <button class="remote-close" id="btn-toggle-remote" title="Toggle Remote (Press R)">✕</button>
      </div>
      <div class="remote-body">
        <div class="dpad-container">
          <button class="dpad-btn dpad-up" id="remote-dpad-up" title="Up (▲)">▲</button>
          <div class="dpad-mid-row">
            <button class="dpad-btn dpad-left" id="remote-dpad-left" title="Left (◀)">◀</button>
            <button class="dpad-btn dpad-center" id="remote-dpad-center" title="Select / OK">OK</button>
            <button class="dpad-btn dpad-right" id="remote-dpad-right" title="Right (▶)">▶</button>
          </div>
          <button class="dpad-btn dpad-down" id="remote-dpad-down" title="Down (▼)">▼</button>
        </div>
        <div class="remote-controls">
          <button class="remote-action-btn" id="remote-btn-back" title="Back (Esc/Backspace)">↩ BACK</button>
          <button class="remote-action-btn" id="remote-btn-home" title="Home">⌂ HOME</button>
        </div>
        <div class="remote-hint">
          <span>Keys: Arrow Keys, Enter, Esc/Backspace</span>
        </div>
      </div>
    `;

    document.body.appendChild(remote);

    // Bind virtual buttons
    document.getElementById('remote-dpad-up').addEventListener('click', () => this.moveDirection('UP'));
    document.getElementById('remote-dpad-down').addEventListener('click', () => this.moveDirection('DOWN'));
    document.getElementById('remote-dpad-left').addEventListener('click', () => this.moveDirection('LEFT'));
    document.getElementById('remote-dpad-right').addEventListener('click', () => this.moveDirection('RIGHT'));
    document.getElementById('remote-dpad-center').addEventListener('click', () => this.handleSelect());
    document.getElementById('remote-btn-back').addEventListener('click', () => this.handleBack());
    document.getElementById('remote-btn-home').addEventListener('click', () => {
      if (window.TVApp) window.TVApp.navigateTo('home');
    });
    document.getElementById('btn-toggle-remote').addEventListener('click', () => this.toggleVirtualRemote());
  }

  toggleVirtualRemote() {
    const el = document.getElementById('firetv-virtual-remote');
    if (el) {
      el.classList.toggle('minimized');
    }
  }
}

// Global instance
window.TVNav = new TVNavigationEngine();
document.addEventListener('DOMContentLoaded', () => {
  window.TVNav.init();
});
