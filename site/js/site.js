(function(){
  /* entrances */
  var els=[].slice.call(document.querySelectorAll('[data-rise],[data-photo]'));
  function show(e){e.classList.add('in')}
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){show(e.target);io.unobserve(e.target)}})},{rootMargin:'0px 0px -8% 0px'});
    els.forEach(function(e){io.observe(e)});
  } else els.forEach(show);
  setTimeout(function(){els.forEach(show)},2500);

  /* open-now status from real hours, Boston time */
  var H={0:null,1:[9,17],2:[9,17],3:[9,17],4:[9,17],5:[9,17],6:[9,15]};
  var names=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  function fmt(h){return (h>12?h-12:h)+(h>=12?' pm':' am')}
  function tick(){
    try{
      var p=new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',weekday:'short',hour:'numeric',minute:'numeric',hour12:false}).formatToParts(new Date());
      var g=function(t){return (p.find(function(x){return x.type===t})||{}).value};
      var d=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].indexOf(g('weekday')),h=+g('hour')%24,m=+g('minute'),t=h+m/60;
      var key=d===0?'0':d===6?'6':'1';
      document.querySelectorAll('#hours [data-d],#foot-hours [data-d]').forEach(function(e){e.classList.toggle('today',e.getAttribute('data-d')===key)});
      document.querySelectorAll('[data-day]').forEach(function(e){var on=e.getAttribute('data-day')===String(d);e.classList.toggle('today',on);if(on)e.setAttribute('aria-current','date');else e.removeAttribute('aria-current')});
      var now=document.getElementById('now'),next=document.getElementById('next'),dot=document.getElementById('dot');
      var today=H[d],st=document.getElementById('open-status');
      if(st){st.textContent=(today&&t>=today[0]&&t<today[1])?'Open now, until '+fmt(today[1])+' today':'Closed now'}
      if(!now)return;
      if(today&&t>=today[0]&&t<today[1]){
        var left=today[1]-t;
        now.textContent='Open now';dot.classList.add('open');
        next.textContent=left<1?'Closing at '+fmt(today[1])+' — call ahead for walk-ins':'Until '+fmt(today[1])+' today. Walk-ins welcome.';
      } else {
        dot.classList.remove('open');
        var k=0,dd=d,start;
        if(today&&t<today[0]){start=today[0]}
        else{do{dd=(dd+1)%7;k++}while(!H[dd]);start=H[dd][0]}
        now.textContent='Closed now';
        next.textContent='Opens '+(k===0?'today':k===1?'tomorrow':names[dd])+' at '+fmt(start)+'.';
      }
    }catch(e){}
  }
  tick();setInterval(tick,60000);

  /* dentist index with preview */
  var bios=['Dr. Edriss, the owner and primary dentist, leads family care from check-ups and cleanings to fillings and crowns.',
    'Known for precision and kindness, Dr. Baig helps patients regain confidence with crowns, root canals and cosmetic work.',
    'Dr. Bano brings warmth and patience to every child\'s visit, so first trips to the dentist build trust instead of fear.',
    'With over a decade in cosmetic dentistry, Dr. Sidhu focuses on natural-looking smile makeovers, veneers and Invisalign.',
    'Dr. Sokoloff focuses on gentle, preventive care and keeping every patient comfortable from cleaning to restoration.'];
  var btns=[].slice.call(document.querySelectorAll('#index button')),imgs=[].slice.call(document.querySelectorAll('.frame img')),bio=document.getElementById('bio');
  function pick(i){btns.forEach(function(b,j){b.classList.toggle('on',j===i)});imgs.forEach(function(m,j){m.classList.toggle('on',j===i)});bio.textContent=bios[i]}
  btns.forEach(function(b,i){b.addEventListener('mouseenter',function(){pick(i)});b.addEventListener('focus',function(){pick(i)});b.addEventListener('click',function(){pick(i)})});

  /* first-visit accordion */
  var st=[].slice.call(document.querySelectorAll('.stage-p'));
  st.forEach(function(s,i){s.querySelector('button').addEventListener('click',function(){st.forEach(function(x,j){x.classList.toggle('open',j===i);x.querySelector('button').setAttribute('aria-expanded',j===i)})})});

  /* phone menu */
  var mb=document.querySelector('.menu-btn'),mn=document.getElementById('mnav');
  if(mb&&mn){
    function setMenu(open){mn.hidden=!open;mb.setAttribute('aria-expanded',open);mb.textContent=open?'Close':'Menu'}
    mb.addEventListener('click',function(){setMenu(mn.hidden);if(!mn.hidden){var f=mn.querySelector('a');f&&f.focus()}});
    mn.addEventListener('click',function(e){if(e.target.closest('a'))setMenu(false)});
    document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!mn.hidden){setMenu(false);mb.focus()}});
    window.matchMedia('(min-width:1101px)').addEventListener('change',function(m){if(m.matches)setMenu(false)});
  }

  /* online booking: Simplifeye self-scheduler (HIPAA-compliant, hosted by Simplifeye).
     Loaded only when a visitor clicks a booking button: Simplifeye's script also loads
     the practice's Google Analytics, so visitors who only browse get no cookies. */
  var SF_KEY='IrHKYGy15IWvHMTRuLTQFkmMl23qGrJ',sfLoading=false,sfPending=false;
  function schedulerReady(){return !!document.querySelector('iframe[id^="self-scheduling-widget-iframe"]')}
  function openScheduler(){
    window.postMessage(JSON.stringify({source:'simplifeye',type:'open-self-scheduling-widget',target:'selfSchedulingWidget',startingUrl:location.href}),'*');
  }
  var live=document.createElement('div');live.className='sr';live.setAttribute('role','status');live.setAttribute('aria-live','polite');document.body.appendChild(live);
  function say(t){live.textContent='';setTimeout(function(){live.textContent=t},50)}
  function loadScheduler(){
    if(sfLoading)return;sfLoading=true;
    window._SELF_SCHEDULING_WIDGET_CONF=window._SELF_SCHEDULING_WIDGET_CONF||{};
    window._SELF_SCHEDULING_WIDGET_CONF.key=SF_KEY;
    var sw=document.createElement('script');sw.async=true;sw.charset='UTF-8';sw.setAttribute('crossorigin','*');
    sw.src='https://embed.simplifeye.co/self-scheduler/'+SF_KEY+'/embed';
    document.head.appendChild(sw);
  }
  /* give the scheduler's frames accessible names once they appear */
  new MutationObserver(function(){
    [].forEach.call(document.querySelectorAll('iframe[id^="self-scheduling-widget"]:not([title])'),function(f){
      f.setAttribute('title',/button/.test(f.id)?'Schedule appointment button':'Online appointment scheduler');
    });
  }).observe(document.body,{childList:true,subtree:true});
  document.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('[data-book]');
    if(!a||e.defaultPrevented||e.button!==0||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;
    e.preventDefault();
    if(schedulerReady()){openScheduler();return}
    if(sfPending)return;sfPending=true;
    document.documentElement.style.cursor='progress';
    var label=a.innerHTML,isBtn=a.classList.contains('btn');
    if(isBtn)a.textContent='Opening scheduler…';
    a.setAttribute('aria-busy','true');say('Opening the online scheduler…');
    loadScheduler();
    var t0=Date.now();
    (function wait(){
      if(schedulerReady()){setTimeout(function(){openScheduler();done()},400);return}
      if(Date.now()-t0>8000){done();location.href=a.getAttribute('href')||'tel:+16173254100';return}
      setTimeout(wait,150);
    })();
    function done(){sfPending=false;document.documentElement.style.cursor='';if(isBtn)a.innerHTML=label;a.removeAttribute('aria-busy')}
  });
})();
