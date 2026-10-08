'use strict';
const $ = id => document.getElementById(id);
const cfg = window.APP_CONFIG || {};
const demo = [
  {id:'demo1',name:'Kaffee Crema',market:'Lidl',city:'Aalen',category:'Getränke',quantity:'1 kg',price:9.99,old_price:13.99,valid_from:'2026-01-01',valid_until:'2099-12-31',emoji:'☕',tint:'#f4eee4',demo:true},
  {id:'demo2',name:'Deutsche Markenbutter',market:'ALDI SÜD',city:'Aalen',category:'Molkerei',quantity:'250 g',price:1.49,old_price:2.29,valid_from:'2026-01-01',valid_until:'2099-12-31',emoji:'🧈',tint:'#fff7df',demo:true},
  {id:'demo3',name:'Frische Vollmilch',market:'REWE',city:'Essingen',category:'Molkerei',quantity:'1 l',price:0.99,old_price:1.39,valid_from:'2026-01-01',valid_until:'2099-12-31',emoji:'🥛',tint:'#e9f2fa',demo:true},
  {id:'demo4',name:'Pizza Margherita',market:'Kaufland',city:'Aalen',category:'Tiefkühl',quantity:'350 g',price:1.79,old_price:2.99,valid_from:'2026-01-01',valid_until:'2099-12-31',emoji:'🍕',tint:'#fff0e7',demo:true},
  {id:'demo5',name:'Bananen',market:'Netto',city:'Oberkochen',category:'Obst & Gemüse',quantity:'1 kg',price:1.29,old_price:1.79,valid_from:'2026-01-01',valid_until:'2099-12-31',emoji:'🍌',tint:'#fff5db',demo:true},
  {id:'demo6',name:'Spaghetti',market:'EDEKA',city:'Westhausen',category:'Vorrat',quantity:'500 g',price:0.79,old_price:1.29,valid_from:'2026-01-01',valid_until:'2099-12-31',emoji:'🍝',tint:'#f2eee5',demo:true}
];
let allOffers = []; let isDemo = false;
const today = () => new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Berlin',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
const euro = n => Number(n).toLocaleString('de-DE',{style:'currency',currency:'EUR'});
const dateDE = s => s && /^\d{4}-\d{2}-\d{2}$/.test(s) ? s.slice(8,10)+'.'+s.slice(5,7)+'.'+s.slice(0,4) : '';
const escapeHTML = s => String(s??'').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const discount = o => Number(o.old_price)>Number(o.price)&&Number(o.price)>0 ? Math.round((1-Number(o.price)/Number(o.old_price))*100):0;
const valid = o => o && typeof o.name==='string' && typeof o.market==='string' && typeof o.city==='string' && typeof o.source_url==='string' && /^https:\/\//.test(o.source_url) && o.valid_from<=today() && o.valid_until>=today() && Number.isFinite(Number(o.price)) && Number(o.price)>=0;
// Frei nutzbare Symbolbilder: keine urheberrechtlich geschützten Händlerfotos.
const productSymbol = offer => {
  if (offer.emoji) return offer.emoji;
  const name = String(offer.name || '').toLocaleLowerCase('de');
  const groups = [
    [/milch|joghurt|quark|sahne|käse|mozzarella|butter|skyr/, '🥛'],
    [/kaffee|espresso|cappuccino/, '☕'],
    [/brot|brötchen|toast|baguette|croissant/, '🥖'],
    [/pizza/, '🍕'], [/nudel|pasta|spaghetti/, '🍝'],
    [/schokolade|praline|kakao|nutella/, '🍫'],
    [/banane/, '🍌'], [/apfel|äpfel/, '🍎'],
    [/tomate/, '🍅'], [/kartoffel/, '🥔'],
    [/obst|gemüse|salat/, '🥬'], [/ei(er|\b)/, '🥚'],
    [/fleisch|hähnchen|wurst|schinken/, '🥩'],
    [/fisch|lachs|thunfisch/, '🐟'],
    [/saft|limonade|cola|wasser|getränk/, '🧃'],
    [/keks|gebäck|kuchen/, '🍪'], [/eiscreme|speiseeis/, '🍦'],
    [/reis|müsli|haferflocken/, '🌾'],
    [/schuh|sneaker|boot|stiefel/, '👟'],
    [/jacke|pullover|hose|shirt|bekleidung|kleid/, '👕'],
    [/spielzeug|spiel/, '🧸'], [/haarreif|kosmetik|schminke/, '💄'],
    [/werkzeug|bohrer|schraube/, '🛠️'],
    [/topf|pfanne|küche/, '🍳'],
    [/pflanze|blume|garten/, '🌿'],
    [/lampe|leuchte|licht/, '💡'],
    [/handy|smartphone|tablet|computer/, '📱']
  ];
  return (groups.find(([pattern]) => pattern.test(name)) || [null, '🛍️'])[1];
};
function uniqueFilter(element,field){const current=$(element).value; const options=[...new Set(allOffers.map(o=>o[field]).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'de'));$(element).innerHTML='<option value="all">Alle '+(field==='market'?'Märkte':'Kategorien')+'</option>'+options.map(v=>`<option value="${escapeHTML(v)}">${escapeHTML(v)}</option>`).join('');$(element).value=options.includes(current)?current:'all'}
function draw(){let q=$('search').value.trim().toLocaleLowerCase('de'),region=$('region').value,market=$('market').value,category=$('category').value;let filtered=allOffers.filter(o=>(!q||[o.name,o.market,o.category,o.quantity].join(' ').toLocaleLowerCase('de').includes(q))&&(region==='all'||o.city===region)&&(market==='all'||o.market===market)&&(category==='all'||o.category===category));let sort=$('sort').value; filtered.sort((a,b)=>sort==='discount'?discount(b)-discount(a):sort==='price'?Number(a.price)-Number(b.price):sort==='ending'?a.valid_until.localeCompare(b.valid_until):a.name.localeCompare(b.name,'de')); $('count').textContent=filtered.length;$('result-label').textContent=filtered.length===1?'1 Angebot gefunden':`${filtered.length} Angebote gefunden`;$('clear-search').hidden=!q;$('empty').hidden=filtered.length!==0;$('cards').innerHTML=filtered.map(o=>{let pct=discount(o);let href=String(o.source_url||'');let safeLink=/^https:\/\//.test(href)?`<a class="source-link" href="${escapeHTML(href)}" target="_blank" rel="noopener noreferrer">Quelle ansehen ↗</a>`:'';return `<article class="offer"><div class="offer-visual" style="--tint:${/^#[0-9a-f]{6}$/i.test(o.tint||'')?o.tint:'#eef4e9'}"><span class="offer-emoji">${escapeHTML(productSymbol(o))}</span>${pct?`<span class="discount">−${pct}%</span>`:''}${o.demo?'<span class="demo-chip">DEMO</span>':''}</div><div class="offer-body"><div class="market-name">${escapeHTML(o.market)} · ${escapeHTML(o.city)}</div><h3>${escapeHTML(o.name)}</h3><div class="quantity">${escapeHTML(o.quantity||'')}</div><div class="prices"><span class="price">${euro(o.price)}</span>${Number(o.old_price)>Number(o.price)?`<span class="oldprice">${euro(o.old_price)}</span>`:''}</div><div class="offer-foot"><strong>Gültig:</strong> ${o.demo?'nur Beispiel':dateDE(o.valid_from)+' – '+dateDE(o.valid_until)}${o.branch?`<br><strong>Filiale:</strong> ${escapeHTML(o.branch)}`:''}${o.reference_price?`<br><strong>Grundpreis:</strong> ${escapeHTML(o.reference_price)}`:''}${safeLink}</div></div></article>`}).join('');$('empty-text').textContent=allOffers.length?'Probiere einen anderen Suchbegriff oder ändere deine Filter.':'Es wurden noch keine gültigen Angebote eingespielt.';}
async function loadOffers(){let rows=[];let connected=false;try{if(cfg.supabaseUrl&&cfg.supabaseAnonKey){const url=cfg.supabaseUrl.replace(/\/$/,'')+'/rest/v1/offers?select=*&order=valid_until.asc&limit=2000';let res=await fetch(url,{headers:{apikey:cfg.supabaseAnonKey,Authorization:'Bearer '+cfg.supabaseAnonKey}});if(!res.ok)throw Error('Supabase '+res.status);rows=await res.json();connected=true;}else{const res=await fetch('./data/offers.json',{cache:'no-store'});if(!res.ok)throw Error('JSON '+res.status);rows=await res.json();connected=true;}}catch(err){$('notice').hidden=false;$('notice').textContent='Die Angebotsdaten konnten nicht geladen werden. Bitte Datenquelle und Verbindung prüfen.';console.error(err)} allOffers=(Array.isArray(rows)?rows:[]).filter(valid); if(!allOffers.length&&cfg.showDemoOnEmpty){allOffers=demo;isDemo=true;$('notice').hidden=false;$('notice').innerHTML='<strong>Vorschau mit Beispieldaten:</strong> Diese Produkte und Preise sind frei erfunden und ausdrücklich <strong>keine aktuellen echten Angebote</strong>. Sobald gültige Daten eingebunden sind, verschwinden diese Beispiele automatisch.';}$('update-status').textContent=isDemo?'● Demo-Modus':connected?'● Gültigkeit heute geprüft':'● Datenquelle nicht erreichbar';if(connected&&!isDemo){try{const meta=await (await fetch('./data/status.json',{cache:'no-store'})).json();if(meta.last_success_utc){const d=new Date(meta.last_success_utc); const age=Date.now()-d.getTime();$('update-status').textContent='● Letzter Import: '+d.toLocaleString('de-DE',{timeZone:'Europe/Berlin',dateStyle:'short',timeStyle:'short'});if(age>48*3600*1000){$('notice').hidden=false;$('notice').textContent='Die letzte erfolgreiche Aktualisierung liegt über 48 Stunden zurück. Bitte die Angebote bei den Händlern prüfen.';}}else{$('update-status').textContent='● Noch kein Live-Import';}}catch(e){console.warn('Status nicht verfügbar',e)}}$('summary').textContent=isDemo?'So könnte deine regionale Angebotssuche aussehen.':'Angebote mit aktuell gültigem Zeitraum.';uniqueFilter('market','market');uniqueFilter('category','category');draw();}
$('search').addEventListener('input',draw);$('search-button').addEventListener('click',()=>{$('angebote').scrollIntoView({behavior:'smooth'});draw()});document.querySelectorAll('[data-query]').forEach(b=>b.addEventListener('click',()=>{$('search').value=b.dataset.query;draw();$('angebote').scrollIntoView({behavior:'smooth'})}));['region','market','category','sort'].forEach(id=>$(id).addEventListener('change',draw));$('reset').addEventListener('click',()=>{$('search').value='';['region','market','category','sort'].forEach(id=>$(id).selectedIndex=0);draw()});$('clear-search').addEventListener('click',()=>{$('search').value='';draw()});$('show-all').addEventListener('click',()=>{$('search').value='';['region','market','category'].forEach(id=>$(id).selectedIndex=0);draw()});loadOffers();
