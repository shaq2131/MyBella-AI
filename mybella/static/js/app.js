document.addEventListener("DOMContentLoaded", () => {
  // Handle navigation from chat back to home sections
  const navLinks = document.querySelectorAll('a[href*="#"]');
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');
      if (href.includes('_anchor=')) {
        // Handle links with _anchor parameter (from chat page)
        e.preventDefault();
        window.location.href = '/#' + href.split('_anchor=')[1];
      } else if (href.startsWith('#')) {
        // Handle direct anchor links (on home page)
        const targetId = href.substring(1);
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
          e.preventDefault();
          targetElement.scrollIntoView({ behavior: 'smooth' });
        }
      }
    });
  });

  // Handle smooth scrolling when arriving from chat page with hash
  if (window.location.hash) {
    const targetElement = document.getElementById(window.location.hash.substring(1));
    if (targetElement) {
      setTimeout(() => {
        targetElement.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  }

  const sendBtn = document.querySelector(".card-footer button");
  const input = document.querySelector(".card-footer input");
  const chatWin = document.querySelector(".chat-window");
  // read the visible persona name from the header (fw-medium element)
  const personaNameEl = document.querySelector('.card-header .fw-medium');
  let persona = personaNameEl ? personaNameEl.textContent.trim().toLowerCase() : 'isabella';

  // Avatar selector (Isabella & Alex visible on frontend)
  const avatarButtons = document.querySelectorAll('.avatar-select button[data-persona]');
  function setPersona(p){
    persona = (p || 'isabella').toLowerCase();
    // update visible name in header
    if (personaNameEl) personaNameEl.textContent = persona.charAt(0).toUpperCase() + persona.slice(1);
    // mark active avatar
    avatarButtons.forEach(b => {
      if (b.dataset.persona === persona) b.classList.add('active'); else b.classList.remove('active');
    });
  }

  // wire avatar clicks
  avatarButtons.forEach(b => b.addEventListener('click', () => setPersona(b.dataset.persona)));

  // initialize active avatar state on load
  if (avatarButtons.length){
    setPersona(persona);
  }

  // carousel persona selectors
  document.querySelectorAll('.select-persona').forEach(btn => {
    btn.addEventListener('click', () => {
      const p = btn.dataset.persona;
      setPersona(p);
      // small system message
      addMsg(`(system) Switched companion to ${p.charAt(0).toUpperCase()+p.slice(1)}.`, 'bot');
    });
  });

  document.querySelectorAll('.reset-memory').forEach(btn => {
    btn.addEventListener('click', async () => {
      const p = btn.dataset.persona;
      // optimistic UI
      addMsg(`(system) Resetting memory for ${p}...`, 'bot');
      try {
        const r = await fetch('/api/reset-memory', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ persona: p }) });
        const j = await r.json().catch(()=>({ok:false}));
        if (j && j.ok){
          addMsg(`(system) Memory for ${p} reset.`, 'bot');
        } else {
          addMsg(`(system) Demo: memory reset request acknowledged for ${p}.`, 'bot');
        }
      } catch(e){
        addMsg(`(system) Network: memory reset queued for ${p}.`, 'bot');
      }
    });
  });

  function addMsg(text, who="user"){
    const div = document.createElement("div"); 
    div.className = "msg " + (who === "bot" ? "bot" : "user");
    div.textContent = text;
    chatWin.appendChild(div);
    chatWin.scrollTop = chatWin.scrollHeight;
  }

  async function callChatAPI(text){
    try {
      const r = await fetch("/api/chat", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ text, persona, mode: "Companion" })
      });
      const j = await r.json();
      return j.text || j.error || "(demo) No response";
    } catch(e){
      return "(demo) Error contacting server";
    }
  }

  async function callTTS(text){
    try {
      const r = await fetch("/api/tts", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ text, persona })
      });
      const j = await r.json();
      if (j.audio_b64){
        const byteChars = atob(j.audio_b64);
        const byteNumbers = new Array(byteChars.length);
        for (let i = 0; i < byteChars.length; i++) byteNumbers[i] = byteChars.charCodeAt(i);
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: "audio/mpeg" });
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        audio.addEventListener('ended', () => URL.revokeObjectURL(url), { once: true });
        audio.play();
      }
    } catch(e){
      console.warn("TTS error", e);
    }
  }

  sendBtn.addEventListener("click", async () => {
    const text = input.value.trim();
    if(!text) return;
    addMsg(text, "user");
    input.value = "";
    const reply = await callChatAPI(text);
    addMsg(reply, "bot");
    callTTS(reply);
  });

  input.addEventListener("keydown", (e) => { if(e.key === "Enter"){ sendBtn.click(); }});

  // Voice upload handler
  const uploadBtn = document.getElementById("uploadVoiceBtn");
  if (uploadBtn){
    uploadBtn.addEventListener("click", async () => {
      uploadBtn.disabled = true; const oldTxt = uploadBtn.textContent; uploadBtn.textContent = "Uploading...";
      const status = document.getElementById("voiceUploadStatus");
      const personaInput = document.getElementById("voicePersona");
      const nameInput = document.getElementById("voiceName");
      const fileInput = document.getElementById("voiceFile");
      status.textContent = "";

      const file = fileInput.files && fileInput.files[0];
      if(!file){
        status.textContent = "Please choose an audio file.";
        status.className = "text-danger small";
        uploadBtn.disabled = false; uploadBtn.textContent = oldTxt;
        return;
      }
      const form = new FormData();
      form.append("persona", personaInput.value || persona);
      if (nameInput.value) form.append("voice_name", nameInput.value);
      form.append("file", file);

      try {
        const r = await fetch("/api/voice-upload", { method: "POST", body: form });
        const j = await r.json();
        if (j.ok){
          status.textContent = "Voice uploaded! Custom voice will now be used for this persona.";
          status.className = "text-success small";
        } else {
          status.textContent = "Upload failed: " + (j.error || "Unknown error");
          status.className = "text-danger small";
        }
      } catch(e){
        status.textContent = "Network error during upload.";
        status.className = "text-danger small";
      }
      uploadBtn.disabled = false; uploadBtn.textContent = oldTxt;
    });
  }
});
