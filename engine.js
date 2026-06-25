// engine.js — JS port of picatrix_engine.py (Schlyter ephemeris + Lilly dignities
// + 28 mansions + Ch4 electional checks). Tested in node against Python reference.
const DEG = Math.PI/180;
const SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
const norm=x=>((x%360)+360)%360;

function dayNumber(date){ // date: JS Date (uses UTC)
  const Y=date.getUTCFullYear(),M=date.getUTCMonth()+1,D=date.getUTCDate();
  const ut=date.getUTCHours()+date.getUTCMinutes()/60+date.getUTCSeconds()/3600;
  const d=367*Y - Math.floor(7*(Y+Math.floor((M+9)/12))/4) + Math.floor(275*M/9) + D - 730530;
  return d + ut/24;
}
function kepler(M,e){ M=norm(M)*DEG; let E=M+e*Math.sin(M)*(1+e*Math.cos(M));
  for(let i=0;i<60;i++){const dE=(E-e*Math.sin(E)-M)/(1-e*Math.cos(E));E-=dE;if(Math.abs(dE)<1e-11)break;} return E;}
function sun(d){
  const w=282.9404+4.70935e-5*d, e=0.016709-1.151e-9*d, Ms=356.0470+0.9856002585*d;
  const E=kepler(Ms,e), xv=Math.cos(E)-e, yv=Math.sqrt(1-e*e)*Math.sin(E);
  const v=Math.atan2(yv,xv)/DEG, r=Math.hypot(xv,yv), lon=norm(v+w);
  return {lon, xs:r*Math.cos(lon*DEG), ys:r*Math.sin(lon*DEG), Ms, w};
}
const PLAN={
 Mercury:[d=>48.3313+3.24587e-5*d,d=>7.0047+5.00e-8*d,d=>29.1241+1.01444e-5*d,d=>0.387098,d=>0.205635+5.59e-10*d,d=>168.6562+4.0923344368*d],
 Venus:[d=>76.6799+2.46590e-5*d,d=>3.3946+2.75e-8*d,d=>54.8910+1.38374e-5*d,d=>0.723330,d=>0.006773-1.302e-9*d,d=>48.0052+1.6021302244*d],
 Mars:[d=>49.5574+2.11081e-5*d,d=>1.8497-1.78e-8*d,d=>286.5016+2.92961e-5*d,d=>1.523688,d=>0.093405+2.516e-9*d,d=>18.6021+0.5240207766*d],
 Jupiter:[d=>100.4542+2.76854e-5*d,d=>1.3030-1.557e-7*d,d=>273.8777+1.64505e-5*d,d=>5.20256,d=>0.048498+4.469e-9*d,d=>19.8950+0.0830853001*d],
 Saturn:[d=>113.6634+2.38980e-5*d,d=>2.4886-1.081e-7*d,d=>339.3939+2.97661e-5*d,d=>9.55475,d=>0.055546-9.499e-9*d,d=>316.9670+0.0334442282*d],
 Uranus:[d=>74.0005+1.3978e-5*d,d=>0.7733+1.9e-8*d,d=>96.6612+3.0565e-5*d,d=>19.18171-1.55e-8*d,d=>0.047318+7.45e-9*d,d=>142.5905+0.011725806*d],
 Neptune:[d=>131.7806+3.0173e-5*d,d=>1.7700-2.55e-7*d,d=>272.8461-6.027e-6*d,d=>30.05826+3.313e-8*d,d=>0.008606+2.15e-9*d,d=>260.2471+0.005995147*d],
};
function planet(name,d){
  const [fN,fi,fw,fa,fe,fM]=PLAN[name];
  const N=fN(d),i=fi(d),w=fw(d),a=fa(d),e=fe(d),M=fM(d);
  const E=kepler(M,e), xv=a*(Math.cos(E)-e), yv=a*Math.sqrt(1-e*e)*Math.sin(E);
  const v=Math.atan2(yv,xv)/DEG, r=Math.hypot(xv,yv);
  const vw=(v+w)*DEG, Nr=N*DEG, ir=i*DEG;
  const xh=r*(Math.cos(Nr)*Math.cos(vw)-Math.sin(Nr)*Math.sin(vw)*Math.cos(ir));
  const yh=r*(Math.sin(Nr)*Math.cos(vw)+Math.cos(Nr)*Math.sin(vw)*Math.cos(ir));
  const s=sun(d);
  return norm(Math.atan2(yh+s.ys, xh+s.xs)/DEG);
}
function moon(d){
  const N=125.1228-0.0529538083*d, i=5.1454, w=318.0634+0.1643573223*d;
  const a=60.2666, e=0.054900, M=115.3654+13.0649929509*d;
  const E=kepler(M,e), xv=a*(Math.cos(E)-e), yv=a*Math.sqrt(1-e*e)*Math.sin(E);
  const v=Math.atan2(yv,xv)/DEG, r=Math.hypot(xv,yv);
  const vw=(v+w)*DEG, Nr=N*DEG, ir=i*DEG;
  const xh=r*(Math.cos(Nr)*Math.cos(vw)-Math.sin(Nr)*Math.sin(vw)*Math.cos(ir));
  const yh=r*(Math.sin(Nr)*Math.cos(vw)+Math.cos(Nr)*Math.sin(vw)*Math.cos(ir));
  let lon=norm(Math.atan2(yh,xh)/DEG);
  const s=sun(d), Ls=norm(s.Ms+s.w), Lm=norm(N+w+M), Mm=norm(M), Ms=norm(s.Ms);
  const Dm=norm(Lm-Ls), F=norm(Lm-N), sn=x=>Math.sin(x*DEG);
  const dlon=-1.274*sn(Mm-2*Dm)+0.658*sn(2*Dm)-0.186*sn(Ms)-0.059*sn(2*Mm-2*Dm)
    -0.057*sn(Mm-2*Dm+Ms)+0.053*sn(Mm+2*Dm)+0.046*sn(2*Dm-Ms)+0.041*sn(Mm-Ms)
    -0.035*sn(Dm)-0.031*sn(Mm+Ms)-0.015*sn(2*F-2*Dm)+0.011*sn(Mm-4*Dm);
  return norm(lon+dlon);
}
function geoLon(body,d){ if(body==='Sun')return sun(d).lon; if(body==='Moon')return moon(d); return planet(body,d); }
function signOf(lon){ lon=norm(lon); return [SIGNS[Math.floor(lon/30)], lon%30]; }
function fmtLon(lon){ const [s,deg]=signOf(lon); let dd=Math.floor(deg), mm=Math.round((deg-dd)*60);
  if(mm===60){dd++;mm=0;} return `${dd}°${String(mm).padStart(2,'0')}' ${s}`; }

const BODIES=['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune'];
function allPositions(date){
  const d=dayNumber(date), out={};
  for(const b of BODIES){
    const lon=geoLon(b,d), step=(b==='Moon')?0.05:1.0;
    const lon2=geoLon(b,d+step);
    const speed=(((lon2-lon+540)%360)-180)/step;
    const [sign,deg]=signOf(lon);
    out[b]={lon,sign,degInSign:deg,speed,retro:speed<0};
  }
  return out;
}
const MANSION_WIDTH=360/28;
function mansionBounds(n){return [(n-1)*MANSION_WIDTH, n*MANSION_WIDTH];}
function mansionIndexForLon(lon){ lon=norm(lon); let i=Math.floor(lon/MANSION_WIDTH); return i>27?27:i; }

// Lilly dignities
const DOMICILE={Aries:'Mars',Taurus:'Venus',Gemini:'Mercury',Cancer:'Moon',Leo:'Sun',Virgo:'Mercury',Libra:'Venus',Scorpio:'Mars',Sagittarius:'Jupiter',Capricorn:'Saturn',Aquarius:'Saturn',Pisces:'Jupiter'};
const DETRIMENT={Aries:'Venus',Taurus:'Mars',Gemini:'Jupiter',Cancer:'Saturn',Leo:'Saturn',Virgo:'Jupiter',Libra:'Mars',Scorpio:'Venus',Sagittarius:'Mercury',Capricorn:'Moon',Aquarius:'Sun',Pisces:'Mercury'};
const EXALT={Aries:['Sun',19],Taurus:['Moon',3],Cancer:['Jupiter',15],Virgo:['Mercury',15],Libra:['Saturn',21],Capricorn:['Mars',28],Pisces:['Venus',27]};
const FALL={Libra:'Sun',Scorpio:'Moon',Capricorn:'Jupiter',Pisces:'Mercury',Aries:'Saturn',Cancer:'Mars',Virgo:'Venus'};
const TRIP={Fire:['Sun','Jupiter'],Earth:['Venus','Moon'],Air:['Saturn','Mercury'],Water:['Mars','Mars']};
const SIGN_ELEMENT={Aries:'Fire',Leo:'Fire',Sagittarius:'Fire',Taurus:'Earth',Virgo:'Earth',Capricorn:'Earth',Gemini:'Air',Libra:'Air',Aquarius:'Air',Cancer:'Water',Scorpio:'Water',Pisces:'Water'};
const TERMS={Aries:[['Jupiter',6],['Venus',12],['Mercury',20],['Mars',25],['Saturn',30]],Taurus:[['Venus',8],['Mercury',14],['Jupiter',22],['Saturn',27],['Mars',30]],Gemini:[['Mercury',6],['Jupiter',12],['Venus',17],['Mars',24],['Saturn',30]],Cancer:[['Mars',7],['Venus',13],['Mercury',19],['Jupiter',26],['Saturn',30]],Leo:[['Jupiter',6],['Venus',11],['Saturn',18],['Mercury',24],['Mars',30]],Virgo:[['Mercury',7],['Venus',17],['Jupiter',21],['Mars',28],['Saturn',30]],Libra:[['Saturn',6],['Mercury',14],['Jupiter',21],['Venus',28],['Mars',30]],Scorpio:[['Mars',7],['Venus',11],['Mercury',19],['Jupiter',24],['Saturn',30]],Sagittarius:[['Jupiter',12],['Venus',17],['Mercury',21],['Saturn',26],['Mars',30]],Capricorn:[['Venus',7],['Mercury',14],['Jupiter',22],['Mars',26],['Saturn',30]],Aquarius:[['Saturn',7],['Mercury',13],['Venus',20],['Jupiter',25],['Mars',30]],Pisces:[['Venus',12],['Jupiter',16],['Mercury',19],['Mars',28],['Saturn',30]]};
const FACES={Aries:['Mars','Sun','Venus'],Taurus:['Mercury','Moon','Saturn'],Gemini:['Jupiter','Mars','Sun'],Cancer:['Venus','Mercury','Moon'],Leo:['Saturn','Jupiter','Mars'],Virgo:['Sun','Venus','Mercury'],Libra:['Moon','Saturn','Jupiter'],Scorpio:['Mars','Sun','Venus'],Sagittarius:['Mercury','Moon','Saturn'],Capricorn:['Jupiter','Mars','Sun'],Aquarius:['Venus','Mercury','Moon'],Pisces:['Saturn','Jupiter','Mars']};
function termRuler(s,deg){for(const [p,u] of TERMS[s])if(deg<u)return p;return TERMS[s][4][0];}
function faceRuler(s,deg){return FACES[s][Math.min(Math.floor(deg/10),2)];}
function essentialDignities(pl,lon,isDay){
  const [s,deg]=signOf(lon); let held=[],debs=[],score=0;
  if(DOMICILE[s]===pl){held.push('domicile');score+=5;}
  if(EXALT[s]&&EXALT[s][0]===pl){held.push('exaltation');score+=4;}
  const tr=TRIP[SIGN_ELEMENT[s]]; if((isDay?tr[0]:tr[1])===pl){held.push('triplicity');score+=3;}
  if(termRuler(s,deg)===pl){held.push('term');score+=2;}
  if(faceRuler(s,deg)===pl){held.push('face');score+=1;}
  if(DETRIMENT[s]===pl){debs.push('detriment');score-=5;}
  if(FALL[s]===pl){debs.push('fall');score-=4;}
  return {score,held,debs};
}
const HUMANE=new Set(['Gemini','Virgo','Libra','Sagittarius','Aquarius']);
const SHORT_ASC=new Set(['Capricorn','Aquarius','Pisces','Aries','Taurus','Gemini']);
const DIURNAL=new Set(['Aries','Gemini','Leo','Libra','Sagittarius','Aquarius']);
const FORTUNES=new Set(['Jupiter','Venus']); const INFORTUNES=new Set(['Saturn','Mars']);
const VIA=[188,213], UNDER_RAYS=12, MOON_SLOW=12;
const ASPECTS={0:'conjunction',60:'sextile',90:'square',120:'trine',180:'opposition'};
function angSep(a,b){let s=Math.abs(a-b)%360;return Math.min(s,360-s);}
function moonAspects(pos,d){
  const res=[], ml=pos.Moon.lon, ml2=geoLon('Moon',d+0.05);
  for(const o of ['Saturn','Mars','Jupiter','Venus','Sun']){
    const ol=pos[o].lon, ol2=geoLon(o,d+0.05), sep=angSep(ml,ol);
    for(const ang of [0,60,90,120,180]){
      if(Math.abs(sep-ang)<=8){
        const sep2=angSep(ml2,ol2), applying=Math.abs(sep2-ang)<Math.abs(sep-ang);
        res.push({other:o,aspect:ASPECTS[ang],orb:Math.abs(sep-ang),applying});
      }
    }
  }
  return res;
}
function jd(date){let Y=date.getUTCFullYear(),M=date.getUTCMonth()+1;
  const D=date.getUTCDate()+(date.getUTCHours()+date.getUTCMinutes()/60+date.getUTCSeconds()/3600)/24;
  if(M<=2){Y--;M+=12;} const A=Math.floor(Y/100),B=2-A+Math.floor(A/4);
  return Math.floor(365.25*(Y+4716))+Math.floor(30.6001*(M+1))+D+B-1524.5;}
function ascendant(date,lat,lon){
  const J=jd(date), T=(J-2451545)/36525;
  let gmst=norm(280.46061837+360.98564736629*(J-2451545)+0.000387933*T*T-T*T*T/38710000);
  const lst=norm(gmst+lon), ramc=lst*DEG, eps=(23.439291-0.0130042*T)*DEG, phi=lat*DEG;
  let asc=norm(Math.atan2(Math.cos(ramc), -(Math.sin(ramc)*Math.cos(eps)+Math.tan(phi)*Math.sin(eps)))/DEG);
  if(!(norm(asc-lst)<180)) asc=norm(asc+180);
  return asc;
}
function electional(date,lat,lon,isDay){
  const d=dayNumber(date), pos=allPositions(date), mo=pos.Moon, su=pos.Sun;
  if(isDay===undefined||isDay===null) isDay=true;
  const dig=essentialDignities('Moon',mo.lon,isDay), mi=mansionIndexForLon(mo.lon);
  const asp=moonAspects(pos,d), sms=angSep(mo.lon,su.lon);
  const underRays=sms<UNDER_RAYS, combustLilly=sms<8.5;
  const via=mo.lon>=VIA[0]&&mo.lon<=VIA[1], slow=mo.speed<MOON_SLOW;
  const badInf=asp.filter(a=>INFORTUNES.has(a.other)&&['conjunction','square','opposition'].includes(a.aspect));
  const goodFor=asp.filter(a=>FORTUNES.has(a.other)&&['trine','sextile'].includes(a.aspect));
  let ascSign=null; if(lat!=null&&lon!=null) ascSign=signOf(ascendant(date,lat,lon))[0];
  const benefic_ok=(!underRays&&!via&&!slow&&badInf.length===0);
  return {date,pos,moon:mo,mansionIndex:mi,dignity:dig,aspects:asp,sunMoonSep:sms,
    underRays,combustLilly,via,slow,ascSign,humane:HUMANE.has(mo.sign),
    shortAsc:SHORT_ASC.has(mo.sign),diurnal:DIURNAL.has(mo.sign),
    badInfortune:badInf,goodFortune:goodFor,benefic_ok};
}

module.exports={allPositions,fmtLon,signOf,mansionIndexForLon,mansionBounds,MANSION_WIDTH,
  essentialDignities,electional,ascendant,geoLon,dayNumber,norm,SIGNS};
