// Jobpatra client-side logic (complete package)
let DATA = null;
function qs(id){return document.getElementById(id)}
function createOption(value,text){const o=document.createElement('option');o.value=value;o.textContent=text;return o}
async function loadData(){
  try{
    const res = await fetch('data.json');
    DATA = await res.json();
    populateStates();
  }catch(e){
    console.error('Failed to load data.json',e);
    qs('results').innerHTML = '<div class="empty">Failed to load dataset.</div>';
  }
}
function populateStates(){
  const stateSelect = qs('stateSelect');
  stateSelect.innerHTML = '<option value="">Select state</option>';
  Object.keys(DATA).sort().forEach(st=>{
    stateSelect.appendChild(createOption(st,st));
  });
  stateSelect.disabled = false;
}
qs('stateSelect')?.addEventListener('change', function(){
  const s = this.value;
  const citySelect = qs('citySelect');
  citySelect.innerHTML = '<option value="">Select city</option>';
  qs('sectorSelect').innerHTML = '<option value="">Select sector</option>';
  qs('results').innerHTML = '<div class="empty">Select city to view companies.</div>';
  if(!s){ citySelect.disabled=true; qs('sectorSelect').disabled=true; return;}
  const cities = Object.keys(DATA[s]||{}).sort();
  cities.forEach(c=> citySelect.appendChild(createOption(c,c)));
  citySelect.disabled = false;
});
qs('citySelect')?.addEventListener('change', function(){
  const s = qs('stateSelect').value;
  const c = this.value;
  const sectors = new Set();
  qs('sectorSelect').innerHTML = '<option value="">Select sector</option>';
  if(!c){ qs('sectorSelect').disabled=true; qs('results').innerHTML = '<div class="empty">Select city to view companies.</div>'; return; }
  const cityObj = DATA[s][c]||{};
  Object.keys(cityObj).sort().forEach(sec=>{ sectors.add(sec); });
  Array.from(sectors).sort().forEach(sec=> qs('sectorSelect').appendChild(createOption(sec,sec)));
  qs('sectorSelect').disabled = false;
  renderCompaniesForCity(s,c);
});
qs('filterBtn')?.addEventListener('click', ()=>applyFilters());
qs('resetBtn')?.addEventListener('click', ()=>{ qs('stateSelect').value=''; qs('citySelect').innerHTML='<option value="">Select city</option>'; qs('citySelect').disabled=true; qs('sectorSelect').innerHTML='<option value="">Select sector</option>'; qs('sectorSelect').disabled=true; qs('searchInput').value=''; qs('results').innerHTML='<div class="empty">Select a state & city to view companies.</div>'; });
function renderCompaniesForCity(state,city){
  const container = qs('results');
  container.innerHTML='';
  const cityObj = DATA[state][city]||{};
  let any=false;
  Object.keys(cityObj).sort().forEach(sec=>{
    (cityObj[sec]||[]).forEach(comp=>{
      any=true;
      const card = document.createElement('div'); card.className='card';
      const roles = (comp.roles||[]).slice(0,12).join(', ');
      card.innerHTML = `<h3>${comp.company}</h3><div class="meta">${sec} • ${city}, ${state}</div><div class="roles"><strong>Roles:</strong> ${roles}</div>
        ${comp.link? `<a class="btn small" href="${comp.link}" target="_blank">Careers</a>` : ''}
        ${comp.linkedin? `<a class="btn small" href="${comp.linkedin}" target="_blank">LinkedIn</a>` : ''}
      `;
      container.appendChild(card);
    });
  });
  if(!any) container.innerHTML = '<div class="empty">No companies found for this city.</div>';
}
function applyFilters(){
  const s = qs('stateSelect').value; const c = qs('citySelect').value; const sec = qs('sectorSelect').value; const q = qs('searchInput').value.trim().toLowerCase();
  if(!s || !c){ alert('Please select state and city first'); return; }
  const cityObj = DATA[s][c]||{};
  const container = qs('results'); container.innerHTML='';
  let results=[];
  Object.keys(cityObj).forEach(sectorKey=>{
    (cityObj[sectorKey]||[]).forEach(comp=>{
      if(sec && sectorKey!==sec) return;
      if(q){
        const inCompany = comp.company.toLowerCase().includes(q);
        const inRoles = (comp.roles||[]).join(' ').toLowerCase().includes(q);
        if(!(inCompany || inRoles)) return;
      }
      results.push({comp,sectorKey});
    });
  });
  if(results.length===0){ container.innerHTML='<div class="empty">No matches found.</div>'; return; }
  results.forEach(r=>{
    const comp=r.comp; const sectorKey=r.sectorKey;
    const card=document.createElement('div'); card.className='card';
    card.innerHTML = `<h3>${comp.company}</h3><div class="meta">${sectorKey} • ${c}, ${s}</div><div class="roles"><strong>Roles:</strong> ${(comp.roles||[]).slice(0,12).join(', ')}</div>
      ${comp.link? `<a class="btn small" href="${comp.link}" target="_blank">Careers</a>` : ''}
      ${comp.linkedin? `<a class="btn small" href="${comp.linkedin}" target="_blank">LinkedIn</a>` : ''}`;
    container.appendChild(card);
  });
}
loadData();
