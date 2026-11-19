(() => {
const el=id=>document.getElementById(id);
let token='',models=[];
const log=(who,text)=>{const welcome=el('chat').querySelector('.welcome');if(welcome)welcome.remove();
 const node=document.createElement('div');node.className='message '+who;
 const title=document.createElement('div');title.className='author';title.textContent=who==='user'?'YOU':who==='assistant'?'LOCAL MODEL':'STUDIO';
 const body=document.createElement('div');body.textContent=text;
 node.append(title,body);el('chat').append(node);el('chat').scrollTop=el('chat').scrollHeight;};
const request=async (route,obj)=>{const r=await fetch(route,{method:'POST',headers:{'Content-Type':'application/json','X-FRD-Session':token},body:JSON.stringify(obj)});
 const x=await r.json();if(!r.ok)throw Error(x.error||'Request failed');return x;};
async function boot(){try{const r=await fetch('/api/bootstrap');const x=await r.json();token=x.token;models=x.models;
 el('workspace').value=(x.capabilities.roots||[])[0]||'';el('status').textContent='Local bridge available';
 el('model').replaceChildren();models.forEach(m=>{const opt=document.createElement('option');opt.value=m;opt.textContent=m;el('model').append(opt);});
 if(!models.length){const opt=document.createElement('option');opt.textContent='No models installed';opt.value='';el('model').append(opt);
 log('system','No Ollama models installed. In a terminal run: ollama pull <model-name> then Refresh. Local recipes work without an AI model.');}
 el('recipes').replaceChildren();x.recipes.forEach(r=>{const b=document.createElement('button');b.className='recipe';
 b.textContent=r.name.replaceAll('_',' ');const s=document.createElement('small');s.textContent=r.requires_test_execution?'Opt-in code execution':'No model call';b.append(s);
 b.onclick=()=>runRecipe(r.name);el('recipes').append(b);});}catch(e){el('status').textContent='Offline';log('system',e.message);}}
async function runRecipe(recipe){const workspace=el('workspace').value.trim();if(!workspace)return log('system','Select an approved workspace in the permissions panel first.');
 log('user','Run '+recipe+' in '+workspace);try{const r=await request('/api/recipes',{recipe,workspace});log('system',JSON.stringify(r,null,2).slice(0,10000));}catch(e){log('system',e.message);}}
const approvals=proposals=>{for(const x of proposals){const row=document.createElement('div');row.className='approval';const code=document.createElement('code');
 code.textContent=x.tool+' '+JSON.stringify(x.arguments).slice(0,900);
 const approve=document.createElement('button');approve.textContent='Approve once';approve.onclick=async()=>{approve.disabled=true;try{
  const result=await request('/api/approve',{id:x.id});log('system',JSON.stringify(result).slice(0,10000));row.remove();if(!el('pending').children.length)el('approvals').hidden=true;
 }catch(e){log('system',e.message);approve.disabled=false;}};row.append(code,approve);el('pending').append(row);el('approvals').hidden=false;}}
el('composer').addEventListener('submit',async ev=>{ev.preventDefault();const msg=el('prompt').value.trim();if(!msg)return;
 el('prompt').value='';log('user',msg);el('send').disabled=true;try{const x=await request('/api/chat',{message:msg,model:el('model').value});log('assistant',x.reply||'No text returned.');approvals(x.proposed||[]);
 }catch(e){log('system',e.message);}finally{el('send').disabled=false;el('prompt').focus();}});
el('prompt').addEventListener('keydown',ev=>{if(ev.key==='Enter'&&!ev.shiftKey){ev.preventDefault();el('composer').requestSubmit();}});
let previewTimer=null,previewUrl=null;
async function updatePreview(){
 try{const r=await fetch('/api/screen',{headers:{'X-FRD-Session':token}});
 if(!r.ok){const e=await r.json();throw Error(e.error||'Screen capture blocked');}
 const blob=await r.blob(),next=URL.createObjectURL(blob);el('screenImage').src=next;
 if(previewUrl)URL.revokeObjectURL(previewUrl);previewUrl=next;
 }catch(e){stopPreview();log('system','Preview: '+e.message);}}
function stopPreview(){
 if(previewTimer){clearInterval(previewTimer);previewTimer=null;}
 el('screenFrame').hidden=true;el('previewBtn').firstChild.textContent='Start private preview';
 if(previewUrl)URL.revokeObjectURL(previewUrl);previewUrl=null;}
el('previewBtn').onclick=()=>{
 if(previewTimer){stopPreview();return;}
 if(!confirm('Screen capture may include other open applications. Start local-only preview?'))return;
 el('screenFrame').hidden=false;el('previewBtn').firstChild.textContent='Stop private preview';
 updatePreview();previewTimer=setInterval(updatePreview,1800);
};
el('browserBtn').onclick=async()=>{
 const url=el('url').value.trim();if(!url)return;
 try{const r=await request('/api/browser',{operation:'browser_navigate',url});
 log('system',JSON.stringify(r).slice(0,12000));}catch(e){log('system','Browser: '+e.message);}
};
el('refresh').onclick=boot;boot();
})();