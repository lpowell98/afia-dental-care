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
      var now=document.getElementById('now');if(!now){return}var _n,next=document.getElementById('next'),dot=document.getElementById('dot');
      var today=H[d];
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
      var key=d===0?'0':d===6?'6':'1';
      document.querySelectorAll('#hours [data-d],#foot-hours [data-d]').forEach(function(e){e.classList.toggle('today',e.getAttribute('data-d')===key)});
    }catch(e){}
  }
  tick();setInterval(tick,60000);

  /* dentist index with preview */
  var bios=['Known for precision and kindness, Dr. Baig helps patients regain confidence with crowns, root canals and cosmetic work.',
    'Dr. Bano brings warmth and patience to every child\'s visit, so first trips to the dentist build trust instead of fear.',
    'With over a decade in cosmetic dentistry, Dr. Sidhu focuses on natural-looking smile makeovers, veneers and Invisalign.',
    'Dr. Sokoloff focuses on gentle, preventive care and keeping every patient comfortable from cleaning to restoration.'];
  var btns=[].slice.call(document.querySelectorAll('#index button')),imgs=[].slice.call(document.querySelectorAll('.frame img')),bio=document.getElementById('bio');
  function pick(i){btns.forEach(function(b,j){b.classList.toggle('on',j===i)});imgs.forEach(function(m,j){m.classList.toggle('on',j===i)});bio.textContent=bios[i]}
  btns.forEach(function(b,i){b.addEventListener('mouseenter',function(){pick(i)});b.addEventListener('focus',function(){pick(i)});b.addEventListener('click',function(){pick(i)})});

  /* first-visit accordion */
  var st=[].slice.call(document.querySelectorAll('.stage-p'));
  st.forEach(function(s,i){s.querySelector('button').addEventListener('click',function(){st.forEach(function(x,j){x.classList.toggle('open',j===i);x.querySelector('button').setAttribute('aria-expanded',j===i)})})});

  /* online booking: Simplifeye self-scheduler (HIPAA-compliant, hosted by Simplifeye).
     Loaded only when a visitor clicks a booking button: Simplifeye's script also loads
     the practice's Google Analytics, so visitors who only browse get no cookies. */
  var SF_KEY='IrHKYGy15IWvHMTRuLTQFkmMl23qGrJ',sfLoading=false,sfPending=false;
  function schedulerReady(){return !!document.querySelector('iframe[id^="self-scheduling-widget-iframe"]')}
  function openScheduler(){
    window.postMessage(JSON.stringify({source:'simplifeye',type:'open-self-scheduling-widget',target:'selfSchedulingWidget',startingUrl:location.href}),'*');
  }
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
    if(!a)return;
    e.preventDefault();
    if(schedulerReady()){openScheduler();return}
    if(sfPending)return;sfPending=true;
    document.documentElement.style.cursor='progress';
    loadScheduler();
    var t0=Date.now();
    (function wait(){
      if(schedulerReady()){setTimeout(function(){openScheduler();done()},400);return}
      if(Date.now()-t0>8000){done();location.href=a.getAttribute('href')||'tel:+16173254100';return}
      setTimeout(wait,150);
    })();
    function done(){sfPending=false;document.documentElement.style.cursor=''}
  });
})();
