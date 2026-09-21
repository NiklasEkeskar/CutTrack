# Statuslogg CutTrack

## Vad "klart" betyder
Ett moment bockas av först när allt tre stämmer:
1. koden finns och körs utan fel
2. jag har testat den med riktig data
3. jag kan förklara den muntligt utan att läsa innantill

## Checklista, G-versionen
| Moment | Var i CutTrack | Klart |
| --- | --- | --- |
| Variabler och datatyper | DailyLog-, User- och CutProfile-attributen | [x] |
| Valfria värden (None) | waist i DailyLog, calorie_goal i CutProfile | [x] |
| If-satser | log_today, add_log, CutProfile-validering, check_goals, create_profile, load_profile, import_logs_csv | [x] |
| Loop | samtliga average-metoder, training_days, make_filename, plot_weight, ask_number, create_profile, run_menu | [x] |
| 3 till 5 egna funktioner | make_filename, save_profile, load_profile, export_logs_csv, plot_weight (fler byggda utöver kravet) | [x] |
| Felhantering med try/except | log_today, load_profile (tre feltyper var för sig), import_logs_csv, save_profile | [x] |
| Datahantering JSON eller CSV | save_profile/load_profile (JSON), export_logs_csv/import_logs_csv (CSV) | [x] |
| Minst en klass | User, DailyLog | [x] |
| Barnklass med arv | CutProfile(User), med super() | [x] |
| Standardbibliotek | json, csv, datetime, os | [x] |
| Externt bibliotek | matplotlib | [x] |
| API eller extern fil | CSV-inläsning (import_logs_csv). Open Food Facts bortprioriterat, se Beslut | [x] |
| Programmet körs utan kritiska fel | hela notebooken uppifrån och ner, bekräftat med Run All | [x] |
| Datafil skapad och sparad | cuttrack_loggar.csv | [x] |
| Notebook med markdown-celler som förklarar | .ipynb, 69 celler | [x] |
| README komplett | mål, metod, resultat, analys, certifikat, reflektion, länk, installation | [x] |
| GitHub-repo med länk i README | repo, publikt | [x] |
| Minst 5 commits | repo, 37 commits, verifierat direkt mot GitHub | [x] |
| Jag kan förklara varje del muntligt | DailyLog, User, CutProfile, filhantering klart. Meny och check_goals nyligen byggda, öva mer | [ ] |
| Zip med alla tre filerna inlämnad | lärarplattformen | [ ] |

Hela G-listan är i praktiken klar, inklusive README. Det som återstår är att committa de sista filerna (se Öppna frågor), muntlig träning, och zip-inlämning.

## Checklista, VG-utbyggnaden
Flera VG-moment är redan uppfyllda som en del av G-arbetet, se Beslut.

| Moment | Var i CutTrack | Klart |
| --- | --- | --- |
| Specifik felhantering per feltyp | load_profile (tre skilda except), import_logs_csv | [x] |
| Extra funktionalitet utöver minimikraven | meny med sex val, CSV-import, kaloriförslag på begäran | [x] |
| 10+ commits | repo, 37 commits | [x] |
| Kod uppdelad i egna filer | models.py, analysis.py, se teknisk_plan.md avsnitt Filstruktur | [x] |
| Konsekvent PEP 8-namngivning | hela koden, radlängd kontrollerad, namngivning ren | [x] |
| Diagram för protein och steg | plot_protein, plot_steps, samma mönster som plot_weight | [x] |
| Val av analysperiod, 7, 14 eller 30 dagar | ask_period(), check_goals(days), plot-funktionerna | [x] |
| Djupare reflektion i README | README, koppling mellan Reflektion och Analys om regelbaserat kontra ML | [x] |

### VG, alla fem delar klara
Diagram för protein och steg, PEP 8-kontroll, djupare reflektion, val av analysperiod, och nu även modulindelningen. Se teknisk_plan.md för detaljer om filstrukturen och de tekniska rättningar modulindelningen och analysperioden krävde (veckotakt normaliserad oavsett fönsterstorlek, träningsmål skalat till perioden).

## Kvar att göra
1. Committa de sista filerna, se Öppna frågor
2. Öva muntlig förklaring, se Muntlig träning, särskilt filstrukturen och kernel-omstarten
3. Öva på att göra en liten ändring i koden live, inte bara förklara den
4. Zip-fil enligt kursplanens namnformat: projekt_python_fornamn_efternamn.zip

Alla fem VG-delar klara. Inga fler tekniska beslut kvar, bara övning och paketering.

## Senaste uppdateringar
(fylls på löpande, senaste överst)

- 2026-09-18: Modulindelning genomförd, sista VG-delen. Koden delad i models.py (DailyLog, User, CutProfile) och analysis.py (make_filename, save_profile, load_profile, export_logs_csv, import_logs_csv, plot_weight, plot_protein, plot_steps), båda testade fristående med samma testbatteri som innan, identiskt resultat. Notebooken importerar från dem och behåller menyn och alla tester. Introcellen förklarar filstrukturen och att kerneln måste startas om efter ändringar i .py-filerna. teknisk_plan.md och produktvision.md uppdaterade, produktvision.md:s roadmap skärpt med konkreta exempel (dagar-till-mål, platådetektion, korrelation, coach-roll) efter en egen problem- och utvecklingsanalys. Beslut: inget av roadmap-förslagen byggs nu, VG:s krav på extra funktionalitet är redan uppfyllt och mer kod ökar bara vad som måste kunna förklaras live utan att flytta betyget.
- 2026-09-18: Kommentarer tillagda i koden på de ställen som faktiskt saknade dem, inte en genomgång av allt. get_logs (de två stegen), add_log (dubblettkontrollen) och suggest_calorie_goal (hela golv-logiken) hade noll kommentarer innan, trots att de är tre av de mest diskuterade delarna. Även run_menu (varför choice jämförs som text) och en kort hänvisning i plot_protein/plot_steps till att de följer plot_weight-mönstret. import_logs_csv hade redan sin kommentar sedan tidigare.
- 2026-09-18: Reflektion i README utökad med koppling till Analys, om skillnaden mellan CutTracks regelbaserade logik och en framtida maskininlärningsmodell, vad som skulle återanvändas (klasser, validering, filhantering) och vad som skulle behöva läggas till (dataförberedelse, träning, utvärdering).
- 2026-09-18: PEP 8 kontrollerat på riktigt, inte antaget. Namngivning (klasser PascalCase, funktioner snake_case) helt ren, 0 avvikelser av 32 funktioner/metoder och 3 klasser. Radlängd: 5 rader av 1101 över 99 tecken, radbrutna och verifierade.
- 2026-09-18: plot_protein och plot_steps byggda, samma mönster som plot_weight (dictionary-sortering, rullande sjudagarssnitt). Testat med 20 dagars data och med för få loggar.
- 2026-09-18: Källor till kaloriberäkningarna sökta fram och lästa på riktigt, inte bara sammanfattningar. Ny sektion "Källor, kaloriberäkningarna" i README med direktlänkar till PubMed/PMC för alla sex källor. Två viktiga nyanser upptäckta och dokumenterade: Garthe 2011 rekommenderar specifikt 0,7 procent per vecka, vårt säkerhetstak på 1,0 är en marginal, inte studiens resultat. Helms 2014 rekommenderar protein per kilo fettfri massa, inte kroppsvikt, vårt tal 1,9 g/kg kroppsvikt kommer i stället från Morton m.fl. 2018.
- 2026-09-18: Gick igenom en egen problem- och riskanalys av projektet (filstruktur, testfiler, dubbletter i kod, obekräftade påståenden). Två buggar bekräftade och rättade i notebooken: introcellen hade dubblerade rader om plot_weight och menyfunktionerna, och CSV-testcellen skrev över cuttrack_loggar.csv med tre testrader istället för Resultat-avsnittets tjugo dagar. export_logs_csv(demo_user, ...) tillagd sist i Resultat-avsnittet så filen på disk efter Run All nu innehåller rätt data. Commit-antalet i teknisk_plan.md ("20+") verifierat direkt mot GitHub: 37 commits, stämmer.
- 2026-09-18: Vikten visas nu i både procent och kg i check_goals (till exempel "cirka 0,6 kg"), samt ett kg-exempel direkt i create_profile när takten matas in, räknat på startvikten. Testat mot den faktiska demo-datan innan det gick in i koden.
- 2026-09-18: Upptäckte att inget arbete committats sedan "Add menu, welcome text and profile creation", trots att notebook (resultatsektion med midjemått) och samtliga docs-filer ändrats sedan dess. Rutin för framöver: kör `git status` innan `git add` för att se exakt vilka filer som faktiskt är ändrade, i stället för att gissa filnamn.
- 2026-09-18: README.md färdigställt i sin helhet, alla nio avsnitt enligt kravspec.md: Mål, Metod, Resultat, Analys, Certifikat, Reflektion, GitHub-länk, Installation, AI-användning. Reflektion skriven av mig själv efter frågor om vad som gick bra, vad som var svårast (get_logs, kalenderdagsfiltreringen som fyra andra metoder bygger på) och vad jag skulle gjort annorlunda (bestämma fil- och mappstruktur tidigare, efter en kväll som gick åt till att reda ut dubbla mappar).
- 2026-09-18: Certifikatavsnittet klart. AI-900 och AI-102 kontrollerade och visade sig vara pensionerade av Microsoft den 30 juni 2026. README pekar istället på AI-901 (Azure AI Fundamentals) och AI-103 (Azure AI Apps and Agents Developer), verifierat direkt mot Microsoft Learn, inte bara branschbloggar.
- 2026-09-17: Demo-data för resultatavsnittet byggd med riktiga kroppsmått (189 cm, 39 år, man, startvikt 101,5 kg, målvikt 98 kg), 20 dagar simulerad men realistisk data (protein 190-230g, steg 8000-12000, träning 4-6 ggr/vecka), samt midjemått en gång i veckan (90,0 till 88,2 cm). Testat genom check_goals vid flera tidpunkter, gav naturlig variation: för snabb takt dag 14-17, för långsam dag 18-19, rätt takt dag 20 med steg som fokusområde istället. Kaloriförslag 2409 kcal, jämfört med faktiskt intag 2300 kcal i datan. Diagram genererat och kontrollerat.
- 2026-09-17: kravspec.md omskriven helt utifrån den faktiska kursplanen (tidigare byggd på en ofullständig sammanfattning). Nytt: krav på att dokumentera AI-användning i README, branschanalys preciserad till yrkesroller och trender, fullständig VG-matris, betygskriterier, checklista inför inlämning.
- 2026-09-17: README-avsnitt skrivna och bekräftade: AI-användning (hur Claude använts genom projektet, att koden till stor del är AI-skriven men förstådd och testad), Analys (kopplar CutTracks datahantering till AI-branschen, med SCB-siffror: AI-användning i svenska företag 25,2 till 35,0 procent 2024-2025, Sverige mot EU-snittet 20 procent, klyftan mellan stora och små företag 71,9 mot 30,8 procent).
- 2026-09-17: plot_weight byggd, matplotlib. Sorterar loggar med en dictionary och sorted() istället för bubbelsortering. Rullande sjudagarssnitt, ett värde per dag. Testat med för få loggar, loggar i oordning, och 20 dagars data.
- 2026-09-17: CSV-hantering byggd, export_logs_csv och import_logs_csv. try/except inne i importloopen så en trasig rad inte stoppar resten. Testat med normalfall och en fil med två trasiga rader.
- 2026-09-17: Menyn byggd: show_welcome (riktlinjer utan siffror som kan krocka med aktivitetsnivå), ask_number, create_profile, run_menu. Testat med simulerad inmatning i tre scenarier: ny profil, laddad profil, samtliga felvägar.
- 2026-09-16: JSON-filhantering byggd: make_filename (teckenlista istället för isalnum, för att utesluta å/ä/ö), save_profile, load_profile med tre skilda feltyper. Testat med normalfall och tre feltyper.
- 2026-09-16: check_goals byggd, med days_since_start och waiting_message. Vikttrenden bedöms mot personens eget mål som undre gräns och ett fast säkerhetstak på 1,0 procent som övre gräns.
- 2026-09-16: suggest_calorie_goal byggd, golv som högsta av BMR och fast gräns.
- 2026-09-16: CutProfile byggd som barnklass med super().
- 2026-09-15: DailyLog, User, log_today byggda och testade. Dubblettmappar rensade, repot gjort publikt.

## Beslut
- Bygg G-versionen klar, testad och förklarbar först. G är nu i praktiken klart kodmässigt.
- Open Food Facts byggs inte. Kravet på extern data uppfylls via CSV-inläsning (import_logs_csv) istället. Sparar tid inför inlämning, och slipper API-felhantering som inte går att testa lika grundligt som filhantering.
- VG-moment som redan är uppfyllda av G-arbetet räknas som klara: specifik felhantering per feltyp, extra funktionalitet utöver kraven, 10+ commits. Modulindelning (models.py/analysis.py) prioriteras bort om tiden är knapp, eftersom den kräver att importstrukturen också kan förklaras och ändras live.
- Träning loggas som ja eller nej (bool), inte som antal minuter.
- BMR räknas på aktuell vikt, inte startvikt.
- Proteinmålet räknas på målvikten.
- Vikttrendens undre gräns är personens eget mål, övre gränsen är ett fast säkerhetstak på 1,0 procent.
- Resultatavsnittet i README bygger på simulerad men realistisk data konstruerad utifrån min egen rutin, inte en logg förd dag för dag i realtid. Det anges öppet i README.
- AI-användningen dokumenteras öppet i README enligt kursplanens krav: idén och besluten är mina, koden är till stor del AI-skriven men genomgången, testad och förstådd.

## Att verifiera mot källa innan koden skrivs
Alla angivna i README under "Källor, kaloriberäkningarna", med direktlänkar till PubMed/PMC. Läs själva artiklarna, inte bara sammanfattningen nedan, innan redovisning.
- [x] Mifflin-St Jeor 1990, formeln stämmer exakt mot koden. https://pubmed.ncbi.nlm.nih.gov/2305711/
- [x] 7700 kcal per kilo kroppsfett, Wishnofsky 1958 (ursprung) och Hall m.fl. 2011 (kritiken, dynamisk modell). https://pubmed.ncbi.nlm.nih.gov/13594881/ och https://pubmed.ncbi.nlm.nih.gov/21872751/
- [x] Takt, Garthe m.fl. 2011. Viktigt att kunna: studien rekommenderar specifikt 0,7 procent som bäst för att bevara fettfri massa, inte "upp till 1,0". Vårt säkerhetstak på 1,0 är en marginal, inte en direkt återgivning av resultatet. https://pubmed.ncbi.nlm.nih.gov/21558571/
- [x] Protein. Viktig nyans: Helms m.fl. 2014 rekommenderar 2,3-3,1 g per kilo FETTFRI MASSA för tävlande, inte kroppsvikt. CutTrack loggar ingen kroppsfettsprocent och räknar därför på målvikt istället, med 1,9 g/kg hämtat ur Morton m.fl. 2018 (metaanalys, nytta planar ut runt 1,6-2,2 g/kg kroppsvikt för icke-tävlande). Detta måste kunna förklaras exakt så om det kommer upp, annars låter det som att Helms-talet bara skrivits av fel. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4033492/ och https://pmc.ncbi.nlm.nih.gov/articles/PMC5867436/
- [x] Kalorigolv: högsta av fast gräns (1200 kvinnor / 1500 män) och personens BMR. Källa: amerikanska obesitasriktlinjerna 2013.
- [x] SCB-siffror till analysavsnittet: AI-användning i företag 2025, kontrollerade direkt mot scb.se

## Muntlig träning, sittande
- [x] Skillnaden mellan `class CutProfile(User)` (ger metoderna) och `super().__init__()` (sätter attributen)
- [x] Varför golvet är det högsta av basalomsättning och fast gräns
- [ ] Filstrukturen: vad som ligger i models.py, analysis.py respektive notebooken, och varför kerneln måste startas om efter en ändring i en .py-fil
- [ ] Varför weight_change normaliseras till en veckotakt (raw_change / days * 7) när analysperioden är valbar
- [ ] get_logs, förklara med egna ord utan att titta i koden
- [ ] add_log, förklara varför dubbletter ersätts
- [ ] check_goals, förklara varför vikten har två olika sorters gränser
- [ ] waiting_message, förklara varför den räknar från senaste loggade dagen och inte dagens riktiga datum
- [ ] load_profile, förklara varför tre skilda except-block istället för ett gemensamt
- [ ] import_logs_csv, förklara varför try/except ligger inne i loopen och inte runt hela
- [ ] make_filename, förklara varför användarinmatning inte får styra filnamnet direkt
- [ ] run_menu, förklara varför input/print hålls separat från klasserna
- [ ] Öva på en liten live-ändring: till exempel byta ett gränsvärde och köra om

## Examination, viktigt att hålla isär
- Teoretisk examination: onlinequiz 28 september (grupp 1), 40 frågor, minst 10 rätt. Testar kursens allmänna innehåll, inget med CutTrack att göra.
- Praktisk examination: CutTrack, inlämning före redovisning, max 10 minuters muntlig redovisning av både kod och README-analys.
- AI-användning ska dokumenteras och förklaras i README, se avsnittet i README och Beslut ovan.
- Kommentarer i koden rekommenderas av läraren, kvar att göra.

## Öppna frågor
- [x] Committa notebooken med resultatsektionen
- [x] Committa docs/kravspec.md
- [x] Committa docs/teknisk_plan.md
- [x] Committa docs/statuslogg.md
- [x] Committa README.md och resultat_diagram.png i projektroten
- [x] Committa bugfixar i notebooken (dubbletter i introcellen, CSV-testrader som skrev över den riktiga datan)
- [x] Committa kg-visning i check_goals och create_profile
- [x] Committa README:s Källor-sektion och statuslogg.md:s ikryssade källverifiering
- [x] Committa plot_protein/plot_steps, bekräftat
- [x] Committa PEP 8-radbrytningarna, bekräftat
- [x] Committa reflektionstillägget i README, bekräftat
- [x] Committa dagens kodkommentarer, bekräftat
- [ ] Committa analysperiod-ändringarna i cuttrack.ipynb (check_goals, waiting_message, ask_period, run_menu)
