'use strict';
// Shared tooltip lives outside scroll containers, so tables cannot clip it.
const aliasPopover=document.createElement('div');
aliasPopover.id='alias-popover';aliasPopover.className='alias-popover';
aliasPopover.setAttribute('role','tooltip');aliasPopover.hidden=true;
document.body.append(aliasPopover);
let aliasTarget=null,aliasTimer=null,aliasPointerType='mouse';
const aliasIndex={characters:new Map(),items:new Map(),locations:new Map()};
function indexAliases(){
  for(const [scope,index] of Object.entries(aliasIndex)){
    index.clear();
    for(const entry of D.nameAliases?.[scope]||[]){
      for(const name of [entry.canonicalName,entry.nameJa,entry.nameEn,...entry.aliases])if(name)index.set(name,entry);
    }
  }
}
function nameWithAliases(scope,item,inControl=false){
  const entry=aliasIndex[scope].get(item.nameJa)||aliasIndex[scope].get(item.name);
  const aliases=[...new Set([...(entry?.aliases||[]),...(item.aliases||[]),...(item.sourceObservations||[]).map(o=>o.rawName)])].filter(n=>n&&n!==item.name);
  if(!aliases.length)return esc(item.name);
  return `<span class="alias-trigger" data-alias-name="${esc(item.name)}" data-aliases="${esc(JSON.stringify(aliases))}"${inControl?'':' tabindex="0"'}>${esc(item.name)}</span>`;
}
function hideAliasPopover(){
  clearTimeout(aliasTimer);
  if(aliasTarget){
    for(const node of [aliasTarget,aliasTarget.closest('button,a')].filter(Boolean)){
      const ids=(node.getAttribute('aria-describedby')||'').split(/\s+/).filter(id=>id&&id!==aliasPopover.id);
      if(ids.length)node.setAttribute('aria-describedby',ids.join(' '));else node.removeAttribute('aria-describedby');
    }
  }
  aliasTarget=null;aliasPopover.hidden=true;
}
function showAliasPopover(target){
  if(!target?.isConnected)return;
  clearTimeout(aliasTimer);
  if(aliasTarget===target&&!aliasPopover.hidden)return;
  hideAliasPopover();aliasTarget=target;
  aliasPopover.innerHTML=`<strong>${esc(target.dataset.aliasName)}</strong><div class="alias-popover-label">其他名称</div><ul>${JSON.parse(target.dataset.aliases).map(n=>`<li>${esc(n)}</li>`).join('')}</ul>`;
  for(const node of [target,target.closest('button,a')].filter(Boolean)){
    node.setAttribute('aria-describedby',[...(node.getAttribute('aria-describedby')||'').split(/\s+/).filter(Boolean),aliasPopover.id].join(' '));
  }
  aliasPopover.hidden=false;
  const rect=target.getBoundingClientRect(),width=aliasPopover.offsetWidth,height=aliasPopover.offsetHeight;
  const left=Math.max(12,Math.min(rect.left,innerWidth-width-12));
  const top=rect.bottom+8+height<=innerHeight-12?rect.bottom+8:Math.max(12,rect.top-height-8);
  aliasPopover.style.left=left+'px';aliasPopover.style.top=top+'px';
}
function scheduleAliasHide(){
  clearTimeout(aliasTimer);
  aliasTimer=setTimeout(()=>{
    const focused=document.activeElement;
    if(aliasTarget&&(focused===aliasTarget||focused?.contains(aliasTarget)))return;
    hideAliasPopover();
  },160);
}
document.addEventListener('pointerover',e=>{
  if(e.pointerType==='touch')return;
  const target=e.target.closest('.alias-trigger');
  if(target)showAliasPopover(target);
  else if(aliasPopover.contains(e.target))clearTimeout(aliasTimer);
});
document.addEventListener('pointerout',e=>{
  if(e.pointerType==='touch')return;
  if(e.target.closest('.alias-trigger')||aliasPopover.contains(e.target)){
    if(aliasTarget?.contains(e.relatedTarget)||aliasPopover.contains(e.relatedTarget))return;
    scheduleAliasHide();
  }
});
document.addEventListener('focusin',e=>{
  if(aliasPointerType==='touch')return;
  const target=e.target.closest('.alias-trigger')||e.target.querySelector('.alias-trigger');
  if(target)showAliasPopover(target);else hideAliasPopover();
});
document.addEventListener('focusout',e=>{
  if(aliasTarget&&(e.target===aliasTarget||e.target.contains(aliasTarget)))scheduleAliasHide();
});
document.addEventListener('pointerdown',e=>{aliasPointerType=e.pointerType},true);
document.addEventListener('click',e=>{
  const target=e.target.closest('.alias-trigger');
  if(target){
    // First touch reveals aliases; a second touch retains the existing link/button action.
    if(aliasPointerType==='touch'&&(aliasTarget!==target||aliasPopover.hidden)){
      e.preventDefault();e.stopImmediatePropagation();showAliasPopover(target);return;
    }
    if(!target.closest('button,a')){showAliasPopover(target);return}
  }
  if(!aliasPopover.contains(e.target))hideAliasPopover();
},true);
document.addEventListener('keydown',e=>{
  if(e.key==='Escape'){hideAliasPopover();return}
  if((e.key==='Enter'||e.key===' ')&&e.target.matches('.alias-trigger')){e.preventDefault();showAliasPopover(e.target)}
});
document.addEventListener('scroll',e=>{if(!aliasPopover.contains(e.target))hideAliasPopover()},true);
window.addEventListener('resize',hideAliasPopover);
