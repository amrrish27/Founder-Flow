"use strict";
const API_URL="http://127.0.0.1:8000";
const $=s=>document.querySelector(s), $$=s=>document.querySelectorAll(s);
const titles={dashboard:"Overview",idea:"Idea Analyzer",finance:"Financial Planner",competitor:"Competitor Benchmark",prediction:"ML Prediction",importance:"Model Insights"};
const state={metrics:null,importance:[]};

function toast(msg,icon="✓"){ $("#toastIcon").textContent=icon; $("#toastMessage").textContent=msg; $("#toast").classList.add("show"); setTimeout(()=>$("#toast").classList.remove("show"),2600); }
function showSection(id){
  $$('.page-section').forEach(x=>x.classList.toggle('active',x.id===id));
  $$('.nav-link').forEach(x=>x.classList.toggle('active',x.dataset.section===id));
  $("#pageTitle").textContent=titles[id]||"FounderFlow";
  $("#sidebar").classList.remove('open'); $("#mobileOverlay").classList.remove('show');
  window.scrollTo({top:0,behavior:'smooth'});
}
$$('[data-section]').forEach(b=>b.addEventListener('click',()=>showSection(b.dataset.section)));
$$('[data-go]').forEach(b=>b.addEventListener('click',()=>showSection(b.dataset.go)));
$("#openSidebar").onclick=()=>{$("#sidebar").classList.add('open');$("#mobileOverlay").classList.add('show')};
$("#closeSidebar").onclick=()=>showSection($(".nav-link.active")?.dataset.section||'dashboard');
$("#mobileOverlay").onclick=()=>$("#closeSidebar").click();

function applyTheme(theme){
  document.body.classList.toggle('light',theme==='light');
  localStorage.setItem('founderflow-theme',theme);
  $("#themeLabel").textContent=theme==='light'?'Light':'Dark';
  $("#themeToggle").firstChild.textContent=theme==='light'?'☀ ':'☾ ';
}
applyTheme(localStorage.getItem('founderflow-theme')||'dark');
$("#themeToggle").onclick=()=>applyTheme(document.body.classList.contains('light')?'dark':'light');

async function api(path,opts={}){
  const r=await fetch(API_URL+path,{headers:{'Content-Type':'application/json',...(opts.headers||{})},...opts});
  if(!r.ok)throw new Error((await r.json().catch(()=>({}))).detail||`API error ${r.status}`);
  return r.json();
}

function pretty(s){return String(s).replaceAll('_',' ').replace(/\b\w/g,c=>c.toUpperCase())}

async function boot(){
  try{
    const h=await api('/health');
    $("#apiStatus").innerHTML='<span class="status-indicator ok"></span>API Online';
    $("#apiMiniStatus").textContent='online'; $("#dashboardStatus").textContent=h.status==='healthy'?'Healthy':'Offline';
    const [m,imp]=await Promise.all([api('/model-metrics'),api('/feature-importance')]);
    state.metrics=m; state.importance=imp.features||[];
    $("#dashboardModel").textContent=m.model||'Classifier';
    $("#dashboardModelVersion").textContent=`Model v${m.model_version||'5.0'} · leakage-safe`;
    $("#dashboardRows").textContent=(m.dataset_rows||0).toLocaleString();
    const auc=(m.results?.[m.model]?.roc_auc);
    $("#dashboardAuc").textContent=auc!=null?(auc*100).toFixed(1)+'%':'—';
    renderImportance(); renderDashboardBars();
  }catch(e){
    $("#apiStatus").innerHTML='<span class="status-indicator error"></span>API Offline';
    $("#apiMiniStatus").textContent='offline'; $("#dashboardStatus").textContent='Offline';
    toast('Start FastAPI on 127.0.0.1:8000','!');
  }
}
boot();

// Loading screen: fixed 5 seconds, independent of API response time.
setTimeout(()=>$("#introScreen").classList.add('hide'),5000);

function renderDashboardBars(){
  const el=$("#dashboardImportance");
  el.innerHTML=state.importance.slice(0,5).map(x=>`<div class="bar-row"><span>${pretty(x.feature)}</span><div class="bar"><i style="width:${Math.max(4,x.importance*100)}%"></i></div><b>${(x.importance*100).toFixed(1)}%</b></div>`).join('');
}
function renderImportance(){
  const el=$("#importanceList");
  el.innerHTML=state.importance.map(x=>`<div class="importance-item"><span>${pretty(x.feature)}</span><div class="bar"><i style="width:${Math.max(2,x.importance*100)}%"></div><b>${(x.importance*100).toFixed(1)}%</b></div>`).join('');
  const m=state.metrics;if(!m)return;
  const r=m.results?.[m.model]||{};
  const cards=[['accuracy','Accuracy'],['precision','Precision'],['recall','Recall'],['f1','F1'],['roc_auc','ROC-AUC']];
  $("#modelMetrics").innerHTML=cards.map(([k,label])=>`<div class="metric-card"><small>${label}</small><strong>${r[k]!=null?(r[k]*100).toFixed(1)+'%':'—'}</strong><span>${m.model}</span></div>`).join('');
  $("#modelNote").innerHTML=`<p class="muted">Model version <b>${m.model_version||'3.0.0'}</b> · ${m.dataset_rows?.toLocaleString()||'—'} training rows · ${m.test_rows?.toLocaleString()||'—'} test rows.</p>`;
}

$("#ideaForm").onsubmit=async e=>{
  e.preventDefault(); const box=$("#ideaResult");
  box.innerHTML='<div class="result-placeholder"><div class="spinner"></div><h2>Analyzing your startup hypothesis…</h2><p>Checking completeness, customer specificity, problem-solution clarity and validation risks.</p></div>';
  try{
    const r=await api('/idea/analyze',{method:'POST',body:JSON.stringify({idea:$("#ideaText").value,industry:$("#ideaIndustry").value,customer:$("#ideaCustomer").value,budget:+$("#ideaBudget").value,problem:$("#ideaProblem").value,solution:$("#ideaSolution").value})});
    box.classList.remove('empty-state'); box.innerHTML=ideaHtml(r); box.classList.add("reveal"); toast(`Idea score: ${r.feasibility_score}/100`);
  }catch(err){box.innerHTML=`<div class="result-placeholder"><h2>Analysis failed</h2><p>${err.message}</p></div>`}
};
function ideaHtml(r){
  const components=(r.score_components||[]).map(x=>`<div class="score-component"><div><b>${x.label}</b><span>${x.note}</span></div><strong>${x.score}%</strong></div>`).join('');
  return `<div class="result-head reveal"><div class="score-ring" style="--score:${r.feasibility_score*3.6}deg"><div class="score-value">${r.feasibility_score}</div></div><h2>${r.score_label}</h2><p>${r.disclaimer}</p></div>
  <div class="result-box score-breakdown"><h3>SCORE BREAKDOWN</h3>${components}</div>
  <div class="result-columns"><div class="result-box"><h3>STRENGTHS</h3><ul>${r.strengths.map(x=>`<li>${x}</li>`).join('')}</ul></div>
  <div class="result-box"><h3>WHAT TO IMPROVE</h3><ul>${r.weaknesses.map(x=>`<li>${x}</li>`).join('')}</ul></div>
  <div class="result-box"><h3>NEXT STEPS</h3><ul>${r.next_steps.map(x=>`<li>${x}</li>`).join('')}</ul></div></div>`;
}

$("#financeForm").onsubmit=async e=>{
  e.preventDefault();
  try{
    const r=await api('/financial/plan',{method:'POST',body:JSON.stringify({initial_investment:+$("#finInvestment").value,monthly_revenue:+$("#finRevenue").value,monthly_expenses:+$("#finExpenses").value,monthly_revenue_growth:+$("#finRevenueGrowth").value,monthly_expense_growth:+$("#finExpenseGrowth").value,price_per_unit:+$("#finPrice").value,variable_cost_per_unit:+$("#finVariable").value,fixed_monthly_costs:+$("#finFixed").value})});
    const max=Math.max(...r.projection.map(x=>Math.max(x.revenue,x.expenses)),1);
    $("#financeResult").innerHTML=`<div class="finance-cards"><div class="metric-card"><small>BURN RATE</small><strong>$${r.burn_rate.toLocaleString()}</strong><span>monthly</span></div><div class="metric-card"><small>RUNWAY</small><strong>${r.runway_months??'∞'}</strong><span>months</span></div><div class="metric-card"><small>BREAK-EVEN</small><strong>${r.break_even_units??'—'}</strong><span>units / month</span></div><div class="metric-card"><small>12M CASH</small><strong>$${r.ending_cash.toLocaleString()}</strong><span>projected</span></div></div><div class="panel finance-panel"><div class="section-heading"><div><small>PROJECTION</small><h2>12-month revenue vs expenses</h2></div></div><div class="projection-chart">${r.projection.map(x=>`<div class="projection-bar" title="M${x.month}: revenue $${x.revenue}, expenses $${x.expenses}"><i style="height:${Math.max(4,(x.revenue/max)*150)}px"></i><span>M${x.month}</span></div>`).join('')}</div></div>`;
    toast('Financial projection built');
  }catch(err){toast(err.message,'!')}
};

$("#predictionForm").onsubmit=async e=>{
  e.preventDefault(); const ids=['founded_year','country','region','industry','employee_count','estimated_revenue_usd','estimated_valuation_usd','funding_round','funding_amount_usd','lead_investor','co_investors','funding_year','funding_month','tags'];
  const payload=Object.fromEntries(ids.map(id=>[id,+$("#"+id).value]));
  $("#resultPanel").innerHTML='<div class="panel prediction-card"><div class="result-placeholder"><div class="spinner"></div><h2>Running ML model…</h2><p>Scoring the startup against the trained feature space.</p></div></div>';
  try{
    const r=await api('/predict',{method:'POST',body:JSON.stringify(payload)});
    const success=(r.success_probability*100).toFixed(1), failure=(r.failure_probability*100).toFixed(1);
    $("#resultPanel").innerHTML=`<div class="panel prediction-card">
      <div><div class="eyebrow">PREDICTION RESULT</div><div class="prediction-status">${r.outcome}</div>
      <p class="muted">Model confidence: ${(r.confidence*100).toFixed(1)}%</p>
      <div class="prob-grid"><div class="prob success"><small>SUCCESS RATE</small><b>${success}%</b></div><div class="prob failure"><small>FAILURE RATE</small><b>${failure}%</b></div></div></div>
      <div><div class="section-heading"><div><small>EXPLAINABILITY</small><h2>Top contributing signals</h2></div></div>
      ${r.explanations.map(x=>`<div class="bar-row"><span>${pretty(x.feature)}</span><div class="bar"><i style="width:${Math.max(4,x.importance*100)}%"></i></div><b>${(x.importance*100).toFixed(1)}%</b></div>`).join('')}
      <div class="notice">${r.disclaimer}</div></div></div>
      <div class="panel improvement-panel"><div class="section-heading"><div><small>AFTER PREDICTION</small><h2>What to improve next</h2></div></div><p class="muted">These are practical validation actions based on the submitted startup data and model output. They are not guarantees that changing a feature will cause success.</p><div class="improvement-list">${(r.improvements||[]).map((x,i)=>`<div class="improvement-item"><span>${String(i+1).padStart(2,'0')}</span><p>${x}</p></div>`).join('')}</div></div>`;
    toast('ML prediction completed');
  }catch(err){$("#resultPanel").innerHTML=`<div class="panel empty-state"><div><h2>Prediction failed</h2><p>${err.message}</p></div></div>`}
};


$("#competitorForm").onsubmit=async e=>{
  e.preventDefault(); const box=$("#competitorResult");
  box.innerHTML='<div class="result-placeholder"><div class="spinner"></div><h2>Comparing your positioning…</h2><p>Checking product overlap, customer focus, pricing position and differentiation.</p></div>';
  try{
    const payload={startup_name:$("#compStartupName").value,startup_product:$("#compStartupProduct").value,startup_customer:$("#compStartupCustomer").value,startup_price:+$("#compStartupPrice").value||0,startup_advantage:$("#compStartupAdvantage").value,competitor_name:$("#compName").value,competitor_product:$("#compProduct").value,competitor_customer:$("#compCustomer").value,competitor_price:+$("#compPrice").value||0,competitor_strengths:$("#compStrengths").value,competitor_weaknesses:$("#compWeaknesses").value};
    const r=await api('/competitor/compare',{method:'POST',body:JSON.stringify(payload)});
    const dims=(r.dimensions||[]).map(x=>`<div class="score-component"><div><b>${x.label}</b><span>${x.note}</span></div><strong>${x.score}%</strong></div>`).join('');
    const actions=(r.how_to_compete||[]).map((x,i)=>`<div class="improvement-item"><span>${String(i+1).padStart(2,'0')}</span><p>${x}</p></div>`).join('');
    box.innerHTML=`<div class="result-head reveal"><div class="score-ring" style="--score:${r.benchmark_score*3.6}deg"><div class="score-value">${r.benchmark_score}</div></div><h2>Competitive benchmark</h2><p>Structured comparison with <b>${r.competitor_name}</b>.</p></div><div class="result-box score-breakdown"><h3>BENCHMARK DIMENSIONS</h3>${dims}</div><div class="panel improvement-panel"><div class="section-heading"><div><small>AFTER COMPARING</small><h2>How to build a stronger position</h2></div></div><p class="muted">Use these actions to test and strengthen your differentiation. They are not guarantees of beating a competitor.</p><div class="improvement-list">${actions}</div></div><div class="notice">${r.disclaimer}</div>`;
    toast('Competitor comparison completed');
  }catch(err){box.innerHTML=`<div class="result-placeholder"><h2>Comparison failed</h2><p>${err.message}</p></div>`}
};
