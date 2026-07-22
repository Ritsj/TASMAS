# Mutant: Undergångens Arvtagare — rules & setting reference

Not fed to the LLM (this project's summarize loop only picks up `*.txt` files
in a `prompts/{promptType}/` folder). This is a human-readable reference for
tuning `1_summary.txt` / `2_events_items.txt`, distilled from the rulebook
(`Mutant_Undergångens_arvtagare_Regelbok_v2.pdf`). It's a terminology map, not
a reproduction of the rules text.

## Karaktär (rollpersonen)

**Klasser**: IMM (icke-muterad människa, +2 alla ge, enda med talanger) ·
MM/MD (mutant, muterad människa/djur, 1–4 mutationer) ·
PSI/MMD (psi-mutant, 1–5 psi-mutationer, drabbas av resonans) ·
RBT (robot, optioner, naturligt pansar, beteendespärr mot att skada människor).

**Grundegenskaper (ge)**: Styrka (STY), Fysik (FYS), Storlek (STO), Smidighet
(SMI), Intelligens (INT), Vilja (VIL), Personlighet (PER).

**Sekundära egenskaper**: Kroppspoäng (**KP** = fys+sto), Traumatröskel
(**TT** = KP/2), Initiativbonus (IB), Skadebonus (SB), Reaktionsvärde (REA),
Status, Rykte, Bärförmåga, Förflyttning.

**Färdigheter (fv, %-värde, t100)**: naturliga (gratis grundchans) vs.
tränade (ingen grundchans, kräver köp/lärare). Skiljs från förmågor.

**Förmågor** = mutationer/psi-mutationer/optioner/talanger, köpta med
Skapelsepoäng (sp) vid rollpersonsskapande. Var och en har Kostnad,
Aktivering, Räckvidd, Effekt, Varaktighet.

**Resonans**: mental risk/kostnad vid misslyckad psi-mutationsaktivering —
2t6 + tidigare misslyckanden − vil mot en tabell (migrän → hjärnblödning).
Fungerar som en riskresurs, inte en förbrukningsbar poängpool.

**Erfarenhetspoäng (erf)**: delas ut av spelledaren per session (Framgång,
Längd, Komplexitet, Risk, Rollspelande), spenderas på att höja fv eller ge.

Förkortningar i tal: rp (rollperson), sl (spelledare), slp (spelledarperson),
sr (stridsrunda), fv, ge, sp, erf.

## Strid & skada

**Grundmekanik**: 1t100 ≤ fv = lyckat slag. Motståndsslag: bäst differens
(fv − slag) vinner.

**Stridsrunda (sr)** ≈ 5 sek. **Initiativvärde (iv)** = 1t10 + IB + vapenmod;
extra handlingar kostar −5 iv och kumulativt −25% fv (max 4). Handlingar:
Oberoende / Långa / Offensiva / Defensiva (Undvika/Parera, −25% fv per
ytterligare försök samma sr). Träffområden (1t6): ben/ben/bål/arm/arm/huvud.

**Skada**:
- Under TT → **kp-skada** (läker 0,5×fys kp/vecka, ger omtöckning).
- Över TT → **kritisk skada**: kroppsdel utslagen, kräver vård inom fys×1
  dygn annars permanent men; förblöder 1 kp/min. Huvud/bål-kritisk är
  livshotande utan vård inom 24–48h.
- Över 2×TT → **dödlig skada**: kroppsdel/liv förloras utan omedelbar hjälp.
- 0 kp → handlingsoförmögen; skada > kp+fys → död.

**Strålning / "zonröta"/"zonsmitta"**: fyra grader (mycket svag → dödlig),
periodiska fys-slag, misslyckande sänker fys (permanent tills chansat
tillbaka efter att ha lämnat zonen). Signaturmekanik för genren —
strålningsexponering och "strålningssjuk" är session-relevanta händelser.

**Andra skadekällor**: eld/frätande ämnen, fall, gifter (tox), sjukdomar
(vir), infektion från obehandlade sår.

**Vapenkategorier**: närstrids-, kast-, svartkruts-, skjut-, hagel-,
hemmabyggen (hb)-, gyrojet-, gauss-, energivapen (laser/maser/neutron/
plasma — genomborrar all känd rustning).

**Rustningar**: primitiva (abs 1–5) → kevlar/impact (abs 4–14) →
energirustningar/reflecskydd (abs 14–30, strålskydd, inget rörelsehinder).
Sköldar: abs dras från skada vid parad.

## Teknologi & ekonomi

**Fynd**: förkatastroftida föremål, hittas i zoner, handlas via byteshandel
snarare än krediter. **Pålitlighet (pål)**: tillförlitlighetsvärde;
misslyckat teknologislag → tillfälligt avbrott; två i rad → ur funktion
tills reparerat (Reparera-färdighet + reservdelar).

**Krediter (kr)**: valutan. Kejsarskatt 20% redan avdraget i inkomsttabeller.

**Rykte**: talang/förmåga, höjs kumulativt genom uppmärksammade dåd.
Chans att bli igenkänd = Rykte × 5%. Modifierar Reaktionsvärde (REA).

## Geografi & fraktioner

**Pyrisamfundet**: kejsardömet, grundat av Otto Skarprättare för ~200 år
sedan, nu styrt av kejsar Thorulf Skarprättare från **Hindenburg**
(huvudstad, Gryningspalatset, aristokratkvarteret Skanshaga).

**Pirit**: gränsstad, informellt styrd av gangsterfamiljerna Cappuccino,
Stiletto, Krutov; guvernör Valfrid Krööger.

**Nordholmia**: bolagsstad (Kolkompaniet, Etanolium, Pappersbolaget m.fl.)
under Wolfram Bonner; guvernör Yulia Wrede.

**Aristokratsläkter**: Skarprättare (kejsarätten), Krööger (handel),
Vattimo (fornfynd/kunskap), Wrede (lag/flotta), Schöld (militär).

**Fjärran hamnar**: Gotland (örepublik, presidör Konrad Suumak) ·
Ulvriket (militärdiktatur, Preben Töfting) · Göborg (fiskarstadsstat,
furste Ejnar Brandelius) · Åland (jordbrukskollektiv, "Ålrådet") ·
Ume (gängstad: Ozzbazz och Bazokaz) · Sursvall (mutantslavstad,
borgmästare Grums Fender).

**Zoner**: farliga obeboeliga områden (t.ex. Musközonen, Uddezonen),
utforskas av zonfarare/exploratorer. **Fribyggare** = oregistrerade
inlandsbosättningar (t.ex. Trohult). **Nybyggare** = ny pyrisk kolonisering
(t.ex. Svedala, Gullspång).

**Bestiarium (urval)**: kutbock/knasa/ulk (boskap), fåle/pansár (rid-/
stridsdjur), dråparträd (köttätande, sprider klonfrön "lil"), zonmara
(telepatisk luftburen zonfara), rubbitar (fientligt underjordsfolk).

**Bazaren** (exempeläventyr i Hindenburg): föreståndare Nicolas fon Rijn,
krogen Bunkern (ägare Lupus Vrock, stridsgropen HinHålet), värdshuset
Thermopolium (Änkan Tenerius), rivaliserande gäng Nimrodbrigaden och
Lejonorden.

---
Source digests compiled by parallel research agents from the full
176-page text extraction of the rulebook, 2026-07-22.
