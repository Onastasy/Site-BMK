(function () {
  const KEY = "theme";
  function applyTheme(v){ const h=document.documentElement; v==="a11y"?h.setAttribute("data-theme","a11y"):h.removeAttribute("data-theme"); }
  function getSaved(){ try{return localStorage.getItem(KEY)||"standard"}catch(e){return"standard"} }
  function save(v){ try{localStorage.setItem(KEY,v)}catch(e){} }
  document.addEventListener("DOMContentLoaded", ()=>{
    const cur=getSaved(); applyTheme(cur);
    const el=document.getElementById("themeSelect"); if(!el) return;
    el.value=cur; el.addEventListener("change", ()=>{ const v=el.value==="a11y"?"a11y":"standard"; applyTheme(v); save(v); });
  });
})();
