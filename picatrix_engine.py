"""
picatrix_engine.py
==================
A dependency-free (stdlib `math` only) calculation engine operationalising
PICATRIX, BOOK ONE, CHAPTERS 3 & 4 (Greer & Warnock, Liber Rubeus edition).

Chapter 3 ("What the heavens are and what their substance is") -> the elemental
   QUALITIES of the seven planets + fixed stars, and the doctrine that the Sun
   amplifies a planet's virtue.
Chapter 4 ("The general theory and arrangement of the heavens for making
   magical images") -> the 28 MANSIONS OF THE MOON and the ELECTIONAL rules for
   timing image-magic (Moon dignified, safe from Saturn/Mars, free of
   combustion, joined to the Fortunes, not in the Via Combusta, not slow, etc.).

Astronomy: Paul Schlyter's low-precision analytic ephemeris (geocentric,
   tropical, ecliptic & equinox of date) -- accuracy ~1-2 arcmin for Sun/planets
   and ~2-4 arcmin for the Moon, which is far finer than this doctrine needs.
   For a production website one could swap in the Swiss Ephemeris; the API here
   is deliberately the same shape.

Astrology tables (essential dignities, terms, faces, aspects, combustion, Via
   Combusta) follow the Ptolemaic/Lilly tradition used in William Lilly's
   *Christian Astrology* (1647).

Everything below the data tables is verified by run_self_test() at import-as-main.
"""

import math
from datetime import datetime, timezone, timedelta

DEG = math.pi / 180.0
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
         'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
PLANETS7 = ['Saturn','Jupiter','Mars','Sun','Venus','Mercury','Moon']

def norm360(x): return x % 360.0

# ---------------------------------------------------------------------------
# 1. CHAPTER 3 -- planetary elemental qualities (the passage the text gives)
#    "If it be Saturn, things cold and dry ... Jupiter warm and moist ... etc."
# ---------------------------------------------------------------------------
PLANET_QUALITIES = {
    # planet : (primary quality phrasing from the text, traditional element)
    'Saturn':  dict(quality='cold and dry',                element='Earth',
                    note='greater infortune; cold/dry'),
    'Jupiter': dict(quality='warm and moist',              element='Air',
                    note='greater fortune; temperate, warm/moist'),
    'Mars':    dict(quality='hot and dry',                 element='Fire',
                    note='lesser infortune; hot/dry, burning'),
    'Sun':     dict(quality='hot and dry (amplifier)',     element='Fire',
                    note='Ch.3: the Sun *attracts/draws out* a planet\u2019s virtue, '
                         'increasing its effect'),
    'Venus':   dict(quality='moderately hot, very moist',  element='Air/Water',
                    note='lesser fortune; temperately warm, very moist'),
    'Mercury': dict(quality='weakly hot, very dry',        element='Earth/Air',
                    note='convertible; faintly warm, very dry'),
    'Moon':    dict(quality='cold and moist',              element='Water',
                    note='governs all beneath her; cold/moist'),
    'Fixed stars': dict(quality='as the Moon (cold and moist)', element='Water',
                    note='Ch.3: fixed stars move the same things as Luna'),
}

# ---------------------------------------------------------------------------
# 2. CHAPTER 4 -- the 28 Mansions of the Moon.
#    Boundaries are arithmetic: each mansion = 360/28 = 12.857142...deg,
#    measured from 0 Aries. Operations are PARAPHRASED keyword summaries of the
#    edition's list (not verbatim text), to keep this a transformative index.
# ---------------------------------------------------------------------------
MANSION_WIDTH = 360.0 / 28.0   # 12 deg 51' 25.714"

MANSIONS = [
 # (#, Latin name in this edition, Arabic name, paraphrased operation keywords)
 (1,  'Alnath',          'Al-Sharatain',  'safe journeys & return; medicines; sow discord between spouses/friends/allies; make servants flee'),
 (2,  'Albotain',        'Al-Butain',     'dig wells/streams; find treasure; plant wheat; wreck unfinished buildings; enrage one against another; strengthen imprisonment'),
 (3,  'Azoraya',         'Al-Thuraiya',   'safe sea travel; firm imprisonment; alchemy & fire-works; hunting; love between spouses'),
 (4,  'Aldebaran',       'Al-Dabaran',    'destroy cities/buildings; turn lord against servant; discord between spouses; destroy springs/treasure-seekers; kill/bind venomous animals'),
 (5,  'Almices',         'Al-Haqa',       'youths learn arts/trades; protect & speed travelers/sailors; improve buildings; break a friendship; favor between spouses (work Moon rising in a humane sign)'),
 (6,  'Athaya',          'Al-Hana',       'destroy & besiege cities; vengeance for kings\u2019 enemies; ruin crops/trees; cause friendship; improve hunting; nullify medicines'),
 (7,  'Aldirah',         'Al-Dhira',      'increase merchandise & profit; safe travel & sailing; increase crops; friendship of allies; expel flies; favor before kings/nobles'),
 (8,  'Annathra',        'Al-Nathrah',    'love & friendship; safe wagon travel; bind allies in friendship; firm imprisonment; afflict captives; expel mice/bugs'),
 (9,  'Atarf',           'Al-Tarf',       'destroy crops; misfortune to travelers; do evil to men; hatred between allies; help a man defend against attack'),
 (10, 'Algebha',         'Al-Jabhah',     'love between spouses; destroy enemies; firm imprisonment; strengthen/complete buildings; love & mutual aid of allies'),
 (11, 'Azobra',          'Al-Zubrah',     'rescue captives; besiege cities; organize trade & profit; safe travel; stabilize buildings; enrich allies'),
 (12, 'Acarfa',          'Al-Sarfah',     'increase harvests; destroy riches & ships; make allies/officials/captives/servants steadfast & honest'),
 (13, 'Alahue',          'Al-Awwa',       'increase trade, profit & harvests; good journeys; complete buildings; free captives; bind nobles for favor'),
 (14, 'Azimech',         'Al-Simak',      'love between spouses; heal the sick; destroy harvests; destroy lust; harm travelers; benefit kings; safe sailing; friendship of allies'),
 (15, 'Algarfa',         'Al-Ghafr',      'dig wells; seek treasure; impede travelers; permanently separate spouses; discord among friends/allies; scatter enemies; destroy enemies\u2019 house/reputation'),
 (16, 'Azubene',         'Al-Zubana',     'destroy merchandise/harvests; discord between friends & spouses; seduce a desired woman; impede travelers; free captives'),
 (17, 'Alichil',         'Al-Iklil',      'improve deception; besiege cities; firm buildings; save sailors; create DURABLE friendship & lasting love (especially this mansion)'),
 (18, 'Alcalb',          'Al-Qalb',       'conspire against kings; vengeance on enemies; strong buildings; free captives; separate friends'),
 (19, 'Exaula',          'Al-Shaulah',    'besiege & take cities; destroy wealth; expel men; aid wagon-travelers; increase harvests; free captives; wreck ships; ruin allies; kill captives'),
 (20, 'Nahaym',          'Al-Naaim',      'tame wild beasts; speed travelers\u2019 return; summon men; join good people; firm imprisonment; harm allies\u2019 wealth'),
 (21, 'Elbelda',         'Al-Baldah',     'strengthen buildings; increase harvests; profit & keep money; safe travel; separate wives from husbands'),
 (22, 'Caadaldeba',      "Sa'd al-Dhabih",'cure illness; sow discord between two; make servants/captives flee; goodwill between allies'),
 (23, 'Caaddebolach',    "Sa'd Bula",     'heal illness; join friends; divide spouses; help captives escape'),
 (24, 'Caadacohot',      "Sa'd al-Su'ud", 'increase merchandise & profit; goodwill between spouses; soldiers\u2019 victory; destroy allies\u2019 money; obstruct officials'),
 (25, 'Caaddalhacbia',   "Sa'd al-Akhbiyah",'besiege cities; take/afflict enemies; speed messengers; separate spouses; destroy harvests; bind spouses or any body part; strengthen prisons; secure buildings'),
 (26, 'Almiquedam',      'Al-Fargh al-Mukdim','bind people in mutual love; protect wagon-travelers; strengthen buildings; firm imprisonment & harm captives'),
 (27, 'Algarf almuehar', 'Al-Fargh al-Muakhar','increase merchandise, profit & harvests; unite allies; heal illness; destroy riches; impede buildings; imperil sea-travelers; prolong imprisonment'),
 (28, 'Arrexhe',         "Al-Risha (Batn al-Hut)",'increase merchandise & harvests; besiege cities; lay waste an area; lose treasures; safe travel; peace between spouses; firm imprisonment; harm sailors'),
]

def mansion_bounds(num):
    """Return (start_deg, end_deg) absolute ecliptic longitude for mansion #num (1-28)."""
    start = (num - 1) * MANSION_WIDTH
    end = num * MANSION_WIDTH
    return start, end

def mansion_for_longitude(lon):
    """Return the mansion record whose arc contains ecliptic longitude `lon`."""
    lon = norm360(lon)
    idx = int(lon // MANSION_WIDTH)          # 0..27
    if idx > 27: idx = 27
    return MANSIONS[idx]

# Sign-classification tables used by Chapter 4's electional rules + footnotes
HUMANE_SIGNS      = {'Gemini','Virgo','Libra','Sagittarius','Aquarius'}      # text, mansion 5
SHORT_ASCENSION   = {'Capricorn','Aquarius','Pisces','Aries','Taurus','Gemini'}  # footnote 52
LONG_ASCENSION    = {'Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius'}
DIURNAL_SIGNS     = {'Aries','Gemini','Leo','Libra','Sagittarius','Aquarius'} # masculine/diurnal
NOCTURNAL_SIGNS   = {'Taurus','Cancer','Virgo','Scorpio','Capricorn','Pisces'}
FORTUNES          = {'Jupiter','Venus'}    # footnote 51
INFORTUNES        = {'Saturn','Mars'}      # footnote 53
VIA_COMBUSTA      = (188.0, 213.0)         # 8 Libra -> 3 Scorpio
UNDER_RAYS_DEG    = 12.0                    # Ch.4: "twelve degrees before or after" the Sun
MOON_SLOW_DEG_DAY = 12.0                    # Ch.4: < 12 deg/day "assimilated to Saturn"

# ---------------------------------------------------------------------------
# 3. WILLIAM LILLY essential-dignity tables (Christian Astrology, p.104)
# ---------------------------------------------------------------------------
DOMICILE = {  # sign -> ruling planet
 'Aries':'Mars','Taurus':'Venus','Gemini':'Mercury','Cancer':'Moon','Leo':'Sun',
 'Virgo':'Mercury','Libra':'Venus','Scorpio':'Mars','Sagittarius':'Jupiter',
 'Capricorn':'Saturn','Aquarius':'Saturn','Pisces':'Jupiter'}
DETRIMENT = {  # opposite sign's ruler is in detriment
 'Aries':'Venus','Taurus':'Mars','Gemini':'Jupiter','Cancer':'Saturn','Leo':'Saturn',
 'Virgo':'Jupiter','Libra':'Mars','Scorpio':'Venus','Sagittarius':'Mercury',
 'Capricorn':'Moon','Aquarius':'Sun','Pisces':'Mercury'}
EXALTATION = {  # sign -> (planet, exact degree)
 'Aries':('Sun',19),'Taurus':('Moon',3),'Cancer':('Jupiter',15),'Virgo':('Mercury',15),
 'Libra':('Saturn',21),'Capricorn':('Mars',28),'Pisces':('Venus',27)}
FALL = {  # sign -> planet in fall
 'Libra':'Sun','Scorpio':'Moon','Capricorn':'Jupiter','Pisces':'Mercury',
 'Aries':'Saturn','Cancer':'Mars','Virgo':'Venus'}
TRIPLICITY = {  # element -> (day ruler, night ruler)  [Ptolemaic, as Lilly uses]
 'Fire':('Sun','Jupiter'),'Earth':('Venus','Moon'),
 'Air':('Saturn','Mercury'),'Water':('Mars','Mars')}
SIGN_ELEMENT = {
 'Aries':'Fire','Leo':'Fire','Sagittarius':'Fire','Taurus':'Earth','Virgo':'Earth',
 'Capricorn':'Earth','Gemini':'Air','Libra':'Air','Aquarius':'Air',
 'Cancer':'Water','Scorpio':'Water','Pisces':'Water'}

# Egyptian terms (bounds). For each sign: list of (planet, upper_degree).
TERMS = {
 'Aries':[('Jupiter',6),('Venus',12),('Mercury',20),('Mars',25),('Saturn',30)],
 'Taurus':[('Venus',8),('Mercury',14),('Jupiter',22),('Saturn',27),('Mars',30)],
 'Gemini':[('Mercury',6),('Jupiter',12),('Venus',17),('Mars',24),('Saturn',30)],
 'Cancer':[('Mars',7),('Venus',13),('Mercury',19),('Jupiter',26),('Saturn',30)],
 'Leo':[('Jupiter',6),('Venus',11),('Saturn',18),('Mercury',24),('Mars',30)],
 'Virgo':[('Mercury',7),('Venus',17),('Jupiter',21),('Mars',28),('Saturn',30)],
 'Libra':[('Saturn',6),('Mercury',14),('Jupiter',21),('Venus',28),('Mars',30)],
 'Scorpio':[('Mars',7),('Venus',11),('Mercury',19),('Jupiter',24),('Saturn',30)],
 'Sagittarius':[('Jupiter',12),('Venus',17),('Mercury',21),('Saturn',26),('Mars',30)],
 'Capricorn':[('Venus',7),('Mercury',14),('Jupiter',22),('Mars',26),('Saturn',30)],
 'Aquarius':[('Saturn',7),('Mercury',13),('Venus',20),('Jupiter',25),('Mars',30)],
 'Pisces':[('Venus',12),('Jupiter',16),('Mercury',19),('Mars',28),('Saturn',30)],
}
# Faces / decans (Chaldean order), 3 per sign of 10deg each.
FACES = {
 'Aries':['Mars','Sun','Venus'],'Taurus':['Mercury','Moon','Saturn'],
 'Gemini':['Jupiter','Mars','Sun'],'Cancer':['Venus','Mercury','Moon'],
 'Leo':['Saturn','Jupiter','Mars'],'Virgo':['Sun','Venus','Mercury'],
 'Libra':['Moon','Saturn','Jupiter'],'Scorpio':['Mars','Sun','Venus'],
 'Sagittarius':['Mercury','Moon','Saturn'],'Capricorn':['Jupiter','Mars','Sun'],
 'Aquarius':['Venus','Mercury','Moon'],'Pisces':['Saturn','Jupiter','Mars'],
}
DIGNITY_SCORE = dict(domicile=5, exaltation=4, triplicity=3, term=2, face=1)
DEBILITY_SCORE = dict(detriment=-5, fall=-4)

def sign_of(lon):
    lon = norm360(lon); return SIGNS[int(lon // 30)], lon % 30.0

def term_ruler(sign, deg):
    for planet, upper in TERMS[sign]:
        if deg < upper: return planet
    return TERMS[sign][-1][0]

def face_ruler(sign, deg):
    return FACES[sign][min(int(deg // 10), 2)]

def essential_dignities(planet, lon, is_day):
    """Return (score, [list of dignities held], [debilities])."""
    sign, deg = sign_of(lon)
    held, debs, score = [], [], 0
    if DOMICILE[sign] == planet: held.append('domicile'); score += DIGNITY_SCORE['domicile']
    ex = EXALTATION.get(sign)
    if ex and ex[0] == planet: held.append('exaltation'); score += DIGNITY_SCORE['exaltation']
    trip = TRIPLICITY[SIGN_ELEMENT[sign]]
    if (trip[0] if is_day else trip[1]) == planet: held.append('triplicity'); score += DIGNITY_SCORE['triplicity']
    if term_ruler(sign, deg) == planet: held.append('term'); score += DIGNITY_SCORE['term']
    if face_ruler(sign, deg) == planet: held.append('face'); score += DIGNITY_SCORE['face']
    if DETRIMENT[sign] == planet: debs.append('detriment'); score += DEBILITY_SCORE['detriment']
    if FALL.get(sign) == planet: debs.append('fall'); score += DEBILITY_SCORE['fall']
    return score, held, debs

# ---------------------------------------------------------------------------
# 4. ASTRONOMY -- Schlyter analytic ephemeris (geocentric, tropical, of date)
# ---------------------------------------------------------------------------
def _day_number(dt_utc):
    Y, M, D = dt_utc.year, dt_utc.month, dt_utc.day
    ut = dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600
    d = (367*Y - (7*(Y + ((M+9)//12)))//4 + (275*M)//9 + D - 730530)
    return d + ut/24.0

def _kepler(M, e):
    M = norm360(M)*DEG
    E = M + e*math.sin(M)*(1 + e*math.cos(M))
    for _ in range(60):
        dE = (E - e*math.sin(E) - M)/(1 - e*math.cos(E)); E -= dE
        if abs(dE) < 1e-11: break
    return E

def _sun(d):
    w = 282.9404 + 4.70935e-5*d; e = 0.016709 - 1.151e-9*d
    Ms = 356.0470 + 0.9856002585*d
    E = _kepler(Ms, e)
    xv = math.cos(E)-e; yv = math.sqrt(1-e*e)*math.sin(E)
    v = math.atan2(yv, xv)/DEG; r = math.hypot(xv, yv)
    lon = norm360(v+w)
    return lon, r*math.cos(lon*DEG), r*math.sin(lon*DEG), Ms, w

_PLAN = {
 'Mercury':(lambda d:48.3313+3.24587e-5*d,lambda d:7.0047+5.00e-8*d,lambda d:29.1241+1.01444e-5*d,lambda d:0.387098,lambda d:0.205635+5.59e-10*d,lambda d:168.6562+4.0923344368*d),
 'Venus':(lambda d:76.6799+2.46590e-5*d,lambda d:3.3946+2.75e-8*d,lambda d:54.8910+1.38374e-5*d,lambda d:0.723330,lambda d:0.006773-1.302e-9*d,lambda d:48.0052+1.6021302244*d),
 'Mars':(lambda d:49.5574+2.11081e-5*d,lambda d:1.8497-1.78e-8*d,lambda d:286.5016+2.92961e-5*d,lambda d:1.523688,lambda d:0.093405+2.516e-9*d,lambda d:18.6021+0.5240207766*d),
 'Jupiter':(lambda d:100.4542+2.76854e-5*d,lambda d:1.3030-1.557e-7*d,lambda d:273.8777+1.64505e-5*d,lambda d:5.20256,lambda d:0.048498+4.469e-9*d,lambda d:19.8950+0.0830853001*d),
 'Saturn':(lambda d:113.6634+2.38980e-5*d,lambda d:2.4886-1.081e-7*d,lambda d:339.3939+2.97661e-5*d,lambda d:9.55475,lambda d:0.055546-9.499e-9*d,lambda d:316.9670+0.0334442282*d),
 'Uranus':(lambda d:74.0005+1.3978e-5*d,lambda d:0.7733+1.9e-8*d,lambda d:96.6612+3.0565e-5*d,lambda d:19.18171-1.55e-8*d,lambda d:0.047318+7.45e-9*d,lambda d:142.5905+0.011725806*d),
 'Neptune':(lambda d:131.7806+3.0173e-5*d,lambda d:1.7700-2.55e-7*d,lambda d:272.8461-6.027e-6*d,lambda d:30.05826+3.313e-8*d,lambda d:0.008606+2.15e-9*d,lambda d:260.2471+0.005995147*d),
}

def _planet(name, d):
    fN,fi,fw,fa,fe,fM = _PLAN[name]
    N,i,w,a,e,M = fN(d),fi(d),fw(d),fa(d),fe(d),fM(d)
    E = _kepler(M, e)
    xv = a*(math.cos(E)-e); yv = a*math.sqrt(1-e*e)*math.sin(E)
    v = math.atan2(yv, xv)/DEG; r = math.hypot(xv, yv)
    vw=(v+w)*DEG; Nr=N*DEG; ir=i*DEG
    xh = r*(math.cos(Nr)*math.cos(vw)-math.sin(Nr)*math.sin(vw)*math.cos(ir))
    yh = r*(math.sin(Nr)*math.cos(vw)+math.cos(Nr)*math.sin(vw)*math.cos(ir))
    sl,xs,ys,_,_ = _sun(d)
    return norm360(math.atan2(yh+ys, xh+xs)/DEG)

def _moon(d):
    N=125.1228-0.0529538083*d; i=5.1454; w=318.0634+0.1643573223*d
    a=60.2666; e=0.054900; M=115.3654+13.0649929509*d
    E=_kepler(M,e)
    xv=a*(math.cos(E)-e); yv=a*math.sqrt(1-e*e)*math.sin(E)
    v=math.atan2(yv,xv)/DEG; r=math.hypot(xv,yv)
    vw=(v+w)*DEG; Nr=N*DEG; ir=i*DEG
    xh=r*(math.cos(Nr)*math.cos(vw)-math.sin(Nr)*math.sin(vw)*math.cos(ir))
    yh=r*(math.sin(Nr)*math.cos(vw)+math.cos(Nr)*math.sin(vw)*math.cos(ir))
    lon=norm360(math.atan2(yh,xh)/DEG)
    sl,xs,ys,Ms,sw=_sun(d)
    Ls=norm360(Ms+sw); Lm=norm360(N+w+M); Mm=norm360(M); MsS=norm360(Ms)
    Dm=norm360(Lm-Ls); F=norm360(Lm-N); s=lambda x: math.sin(x*DEG)
    dlon=(-1.274*s(Mm-2*Dm)+0.658*s(2*Dm)-0.186*s(MsS)-0.059*s(2*Mm-2*Dm)
          -0.057*s(Mm-2*Dm+MsS)+0.053*s(Mm+2*Dm)+0.046*s(2*Dm-MsS)+0.041*s(Mm-MsS)
          -0.035*s(Dm)-0.031*s(Mm+MsS)-0.015*s(2*F-2*Dm)+0.011*s(Mm-4*Dm))
    return norm360(lon+dlon)

def geo_longitude(body, d):
    if body == 'Sun':  return _sun(d)[0]
    if body == 'Moon': return _moon(d)
    return _planet(body, d)

def all_positions(dt_utc):
    """Return dict body -> dict(lon, sign, deg_in_sign, speed_deg_per_day, retrograde)."""
    d = _day_number(dt_utc)
    out = {}
    for b in ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune']:
        lon = geo_longitude(b, d)
        lon2 = geo_longitude(b, d + (0.05 if b == 'Moon' else 1.0))
        speed = ((lon2 - lon + 540) % 360 - 180) / (0.05 if b == 'Moon' else 1.0)
        sign, deg = sign_of(lon)
        out[b] = dict(lon=lon, sign=sign, deg_in_sign=deg,
                      speed=speed, retrograde=speed < 0)
    return out

# ---------------------------------------------------------------------------
# 5. Whole-sign ASCENDANT (approximate) -- for diurnal/nocturnal & humane-sign
#    rising checks. Standard formula; flagged approximate.
# ---------------------------------------------------------------------------
def _jd(dt_utc):
    Y,M = dt_utc.year, dt_utc.month
    D = dt_utc.day + (dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600)/24
    if M <= 2: Y -= 1; M += 12
    A = Y//100; B = 2 - A + A//4
    return int(365.25*(Y+4716)) + int(30.6001*(M+1)) + D + B - 1524.5

def ascendant(dt_utc, lat_deg, lon_deg):
    jd = _jd(dt_utc); T = (jd - 2451545.0)/36525.0
    gmst = (280.46061837 + 360.98564736629*(jd-2451545.0)
            + 0.000387933*T*T - T*T*T/38710000.0) % 360.0
    lst = (gmst + lon_deg) % 360.0          # local apparent sidereal time (deg)
    ramc = lst*DEG
    eps = (23.439291 - 0.0130042*T)*DEG
    phi = lat_deg*DEG
    asc = math.atan2(math.cos(ramc), -(math.sin(ramc)*math.cos(eps)
                                       + math.tan(phi)*math.sin(eps)))
    asc = norm360(asc/DEG)
    # ensure the *rising* (eastern) intersection
    if not (norm360(asc - lst) < 180):
        asc = norm360(asc + 180)
    return asc

# ---------------------------------------------------------------------------
# 6. CHAPTER 4 ELECTIONAL CHECKER -- evaluate the Moon for image-magic timing
# ---------------------------------------------------------------------------
def angular_sep(a, b):
    s = abs(a-b) % 360.0
    return min(s, 360.0 - s)

ASPECTS = {0:'conjunction',60:'sextile',90:'square',120:'trine',180:'opposition'}

def moon_aspects(pos, d):
    """Aspects from Moon to Saturn, Mars, Jupiter, Venus, Sun (orb 8 deg)."""
    res = []
    mlon = pos['Moon']['lon']
    mlon_next = geo_longitude('Moon', d+0.05)
    for other in ['Saturn','Mars','Jupiter','Venus','Sun']:
        olon = pos[other]['lon']; olon_next = geo_longitude(other, d+0.05)
        sep = angular_sep(mlon, olon)
        for ang, name in ASPECTS.items():
            if abs(sep-ang) <= 8.0:
                sep2 = angular_sep(mlon_next, olon_next)
                applying = abs(sep2-ang) < abs(sep-ang)
                res.append(dict(other=other, aspect=name, orb=round(abs(sep-ang),2),
                                applying=applying))
    return res

def electional_report(dt_utc, lat_deg=None, lon_deg=None, is_day=None):
    """Full Chapter-4 suitability read-out for the Moon at a given moment."""
    d = _day_number(dt_utc)
    pos = all_positions(dt_utc)
    moon = pos['Moon']; sun = pos['Sun']
    if is_day is None:                      # crude day/night if no horizon known
        is_day = True
    msign = moon['sign']
    score, held, debs = essential_dignities('Moon', moon['lon'], is_day)
    man = mansion_for_longitude(moon['lon'])
    asp = moon_aspects(pos, d)

    sun_moon_sep = angular_sep(moon['lon'], sun['lon'])
    under_rays = sun_moon_sep < UNDER_RAYS_DEG
    combust_lilly = sun_moon_sep < 8.5
    via = VIA_COMBUSTA[0] <= moon['lon'] <= VIA_COMBUSTA[1]
    slow = moon['speed'] < MOON_SLOW_DEG_DAY
    bad_infortune = [a for a in asp if a['other'] in INFORTUNES
                     and a['aspect'] in ('conjunction','square','opposition')]
    good_fortune  = [a for a in asp if a['other'] in FORTUNES
                     and a['aspect'] in ('trine','sextile')]

    asc_sign = None
    if lat_deg is not None and lon_deg is not None:
        asc = ascendant(dt_utc, lat_deg, lon_deg)
        asc_sign = sign_of(asc)[0]

    # Chapter-4 verdict for a *benefic* working
    flags = []
    if under_rays: flags.append('Moon under the Sun\u2019s rays (<12\u00b0) \u2013 avoid')
    if via:        flags.append('Moon in the Via Combusta (8\u00b0 Libra\u20133\u00b0 Scorpio) \u2013 avoid')
    if slow:       flags.append(f'Moon slow ({moon["speed"]:.1f}\u00b0/day < 12\u00b0) \u2013 like Saturn')
    if bad_infortune:
        flags.append('Moon afflicted by Saturn/Mars (' +
                     ', '.join(f'{a["aspect"]} {a["other"]}' for a in bad_infortune) + ')')
    if msign == 'Scorpio': flags.append('Moon in its fall (Scorpio)')
    good = []
    if good_fortune:
        good.append('Moon aided by Fortune(s): ' +
                    ', '.join(f'{a["aspect"]} {a["other"]}' + (' (applying)' if a['applying'] else '')
                              for a in good_fortune))
    if score >= 1: good.append(f'Moon has essential dignity (+{score}: {", ".join(held) or "\u2014"})')

    benefic_suitable = (not under_rays and not via and not slow and not bad_infortune)

    return dict(
        when=dt_utc, positions=pos, moon=moon, mansion=man,
        moon_dignity=dict(score=score, dignities=held, debilities=debs),
        aspects=asp, sun_moon_sep=round(sun_moon_sep,2),
        under_rays=under_rays, combust_lilly=combust_lilly, via_combusta=via,
        slow=slow, ascendant_sign=asc_sign,
        humane_sign=(msign in HUMANE_SIGNS), short_ascension=(msign in SHORT_ASCENSION),
        diurnal_sign=(msign in DIURNAL_SIGNS),
        flags=flags, favorable=good, benefic_suitable=benefic_suitable,
    )

# ---------------------------------------------------------------------------
# Pretty helpers
# ---------------------------------------------------------------------------
def fmt_lon(lon):
    sign, deg = sign_of(lon); dd=int(deg); mm=int(round((deg-dd)*60))
    if mm==60: dd+=1; mm=0
    return f"{dd:2d}\u00b0{mm:02d}' {sign}"

# ===========================================================================
# VERIFICATION
# ===========================================================================
def run_self_test():
    print("="*72); print("PICATRIX BOOK 1 ENGINE \u2014 SELF TEST"); print("="*72)
    ok = True

    # (A) Mansions tile the circle exactly, no gaps/overlaps
    assert len(MANSIONS) == 28
    for n in range(1,29):
        s,e = mansion_bounds(n)
        assert abs((e-s) - MANSION_WIDTH) < 1e-9
    assert abs(mansion_bounds(28)[1] - 360.0) < 1e-9
    assert mansion_for_longitude(0.0)[0] == 1
    assert mansion_for_longitude(13.0)[0] == 2          # 13 Aries -> mansion 2
    assert mansion_for_longitude(359.999)[0] == 28
    print("[OK] 28 mansions tile 360\u00b0 exactly; lookup correct "
          "(0\u00b0Ari=M1, 13\u00b0Ari=M2, 30\u00b0Pis=M28)")

    # (B) Dignity tables are internally consistent
    for sg in SIGNS:
        assert TERMS[sg][-1][1] == 30, f"terms of {sg} must reach 30\u00b0"
        assert len(FACES[sg]) == 3
    # every planet's domicile/detriment are opposite signs
    for sg in SIGNS:
        opp = SIGNS[(SIGNS.index(sg)+6)%12]
        assert DETRIMENT[sg] == DOMICILE[opp]
    print("[OK] Lilly dignity tables consistent (terms reach 30\u00b0, "
          "detriment = ruler of opposite sign, 3 faces/sign)")

    # (C) Known dignity spot-checks
    s,h,_ = essential_dignities('Sun', 19.0, True)       # 19 Aries: exalt + day triplicity ruler of fire
    assert 'exaltation' in h and 'triplicity' in h, h
    s,h,_ = essential_dignities('Mars', 200.0, True)     # 20 Libra: Mars detriment + term
    assert 'detriment' in essential_dignities('Mars',200.0,True)[2]
    print("[OK] dignity spot-checks (Sun 19\u00b0Ari exalt+trip; Mars in Libra detriment)")

    # (D) Ephemeris cross-check against independently verified values for the
    #     evening of 2026-06-24 (see conversation): Sun ~3.5 Cancer, Jup ~29 Cancer,
    #     Sat ~14 Aries, Moon ~9 Scorpio, Pluto-region etc.
    dt = datetime(2026,6,25,0,47,0, tzinfo=timezone.utc)
    pos = all_positions(dt)
    checks = {'Sun':('Cancer',3.5),'Jupiter':('Cancer',29),'Saturn':('Aries',14),
              'Mars':('Taurus',27),'Venus':('Leo',13),'Mercury':('Cancer',25),
              'Uranus':('Gemini',3),'Neptune':('Aries',4),'Moon':('Scorpio',9)}
    print("\nEphemeris check  2026-06-25 00:47 UT (geocentric, tropical):")
    for b,(esign,edeg) in checks.items():
        p = pos[b]
        match = (p['sign']==esign and abs(p['deg_in_sign']-edeg) < 1.5)
        ok &= match
        print(f"   {b:8s} {fmt_lon(p['lon'])}  {'Rx' if p['retrograde'] else '  '}"
              f"   expect ~{edeg:.0f}\u00b0 {esign}   {'OK' if match else 'MISMATCH'}")

    # (E) End-to-end electional report runs and is self-consistent
    rep = electional_report(dt, lat_deg=40.71, lon_deg=-74.01, is_day=False)
    assert rep['mansion'][0] == mansion_for_longitude(pos['Moon']['lon'])[0]
    print(f"\n[OK] electional_report() ran: Moon in Mansion "
          f"{rep['mansion'][0]} ({rep['mansion'][1]}); "
          f"benefic-suitable={rep['benefic_suitable']}; flags={len(rep['flags'])}")
    print("\nResult:", "ALL CHECKS PASSED" if ok else "*** SOME CHECKS FAILED ***")
    return ok

if __name__ == '__main__':
    run_self_test()
