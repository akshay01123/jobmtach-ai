// Frontend logic for JobMatch AI
// - Handles drag/drop and file selection
// - Shows selected filenames
// - Posts data to /api/analyze (placeholder for now)

const resumeDrop = document.getElementById('resumeDrop');
const jobDrop = document.getElementById('jobDrop');
const resumeInput = document.getElementById('resumeInput');
const jobInput = document.getElementById('jobInput');
const resumeInfo = document.getElementById('resumeInfo');
const jobInfo = document.getElementById('jobInfo');
const jobText = document.getElementById('jobText');
const analyzeBtn = document.getElementById('analyzeBtn');
const results = document.getElementById('results');
const matchScore = document.getElementById('matchScore');

const matcherRadios = () => document.querySelector('input[name="matcher"]:checked')?.value || 'backend';
const modelInput = document.getElementById('modelInput');
const modelRow = document.getElementById('modelRow');
const loadingOverlay = document.createElement('div');
loadingOverlay.className = 'loading-overlay';
loadingOverlay.innerHTML = '<div class="spinner" role="status" aria-label="Loading"></div>';
document.body.appendChild(loadingOverlay);

function showLoading(){
  loadingOverlay.classList.add('show');
}
function hideLoading(){
  loadingOverlay.classList.remove('show');
}

// Result fields
const overallMatch = document.getElementById('overallMatch');
const skillsMatch = document.getElementById('skillsMatch');
const experienceMatch = document.getElementById('experienceMatch');
const educationMatch = document.getElementById('educationMatch');
const missingSkills = document.getElementById('missingSkills');
const strengths = document.getElementById('strengths');
const aiRecommendation = document.getElementById('aiRecommendation');

// Utility to attach drag/drop to an element and its associated input
function makeDropzone(zone, input, infoEl){
  zone.addEventListener('click', ()=> input.click());

  ;['dragenter','dragover'].forEach(evt=>{
    zone.addEventListener(evt, e=>{
      e.preventDefault();
      e.stopPropagation();
      zone.classList.add('dragover');
    });
  });
  ;['dragleave','drop'].forEach(evt=>{
    zone.addEventListener(evt, e=>{
      e.preventDefault();
      e.stopPropagation();
      zone.classList.remove('dragover');
    });
  });

  zone.addEventListener('drop', e=>{
    const file = e.dataTransfer.files[0];
    if(file) handleFileSelected(file, input, infoEl);
  });

  input.addEventListener('change', e=>{
    const file = e.target.files[0];
    if(file) handleFileSelected(file, input, infoEl);
  });
}

function handleFileSelected(file, input, infoEl){
  // store file reference on the input element for later upload
  input._file = file;
  infoEl.textContent = `${file.name} (${Math.round(file.size/1024)} KB)`;
}

makeDropzone(resumeDrop, resumeInput, resumeInfo);
makeDropzone(jobDrop, jobInput, jobInfo);

analyzeBtn.addEventListener('click', async ()=>{
  // show a simple loading state
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = 'Analyzing...';
  showLoading();
  const selected = matcherRadios();
  const form = new FormData();
  if(resumeInput._file) form.append('resume', resumeInput._file);
  if(jobInput._file) form.append('job_file', jobInput._file);
  if(jobText.value.trim()) form.append('job_text', jobText.value.trim());

  try{
    let resp;
    if(selected === 'ollama'){
      // call ollama_match endpoint (expects form with job_text and optional resume)
      // append model name if available
      if(modelInput && modelInput.value) form.append('model', modelInput.value);
      resp = await fetch('/api/ollama_match', { method: 'POST', body: form });
    }else{
      resp = await fetch('/api/analyze', { method: 'POST', body: form });
    }

    if(!resp.ok) throw new Error('Server error');
    const data = await resp.json();
    // Populate results (these keys come from the backend placeholder)
    // Support responses from both the simple backend and Ollama JSON
    const score = data.match_percentage || data.overall_match || (data.score ? `${data.score}%` : '--%');
    matchScore.textContent = score || '--%';
    overallMatch.textContent = data.overall_match || (data.score ? `${data.score}%` : '--%');
    skillsMatch.textContent = data.skills_match || '--%';
    experienceMatch.textContent = data.experience_match || (data.experience_match === 0 ? '0%' : (data.experience ? `${data.experience}%` : '--%'));
    educationMatch.textContent = data.education_match || '--%';

    // Lists
    missingSkills.innerHTML = '';
    (data.missing_skills || data.missingSkills || []).forEach(s=>{
      const li = document.createElement('li'); li.textContent = s; missingSkills.appendChild(li);
    });
    strengths.innerHTML = '';
    (data.strengths || data.strengths || data.strengths || []).forEach(s=>{
      const li = document.createElement('li'); li.textContent = s; strengths.appendChild(li);
    });

    aiRecommendation.textContent = data.ai_recommendation || data.recommendation || 'AI analysis not yet implemented.';

    // show results
    results.classList.add('show');
    results.setAttribute('aria-hidden','false');
    // animate score if available
    const raw = (data.match_percentage || data.overall_match || (data.score ? `${data.score}%` : '--%')).toString();
    const n = parseInt(raw.replace('%',''));
    if(!isNaN(n)){
      let start = 0;
      const el = matchScore;
      const step = Math.max(1, Math.round(n/20));
      const iv = setInterval(()=>{
        start = Math.min(n, start + step);
        el.textContent = `${start}%`;
        if(start >= n) clearInterval(iv);
      }, 12);
    }
  }catch(err){
    console.error(err);
    alert('Failed to analyze. Backend may not be running.');
  }finally{
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = 'Analyze Match';
    hideLoading();
  }
});

// Small enhancement: allow pressing Ctrl+Enter in job text to trigger analyze
jobText.addEventListener('keydown', e=>{
  if((e.ctrlKey||e.metaKey) && e.key === 'Enter') analyzeBtn.click();
});

// show/hide model input when matcher changes
document.querySelectorAll('input[name="matcher"]').forEach(r=>{
  r.addEventListener('change', ()=>{
    if(matcherRadios() === 'ollama') modelRow.style.display = 'inline-flex';
    else modelRow.style.display = 'none';
  });
});

// initial toggle
if(matcherRadios() === 'ollama') modelRow.style.display = 'inline-flex';
