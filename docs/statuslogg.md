# Statuslogg CutTrack

## Vad "klart" betyder
Ett moment bockas av först när allt tre stämmer:
1. koden finns och körs utan fel
2. jag har testat den med riktig data
3. jag kan förklara den muntligt utan att läsa innantill

## Checklista, G-versionen
| Moment | Var i CutTrack | Klart |
| --- | --- | --- |
| Variabler och datatyper | DailyLog-attributen, CutProfile-attributen | [x] |
| Valfria värden (None) | waist i DailyLog, calorie_goal i CutProfile | [x] |
| If-satser | log_today (waist-hantering), add_log (dubblettkontroll), CutProfile (könsval i BMR), byggda och testade. check_goals och run_menu ej byggda än | [x] |
| Loop | add_log, get_logs, average_weight, weight_change, training_days, current_weight, byggda och testade. while i run_menu ej byggt än | [x] |
| 3 till 5 egna funktioner | load_profile, save_profile, export_logs_csv, calculate_trend, plot_weight | [ ] |
| Felhantering med try/except | log_today (DailyLog-validering), byggd och testad. filinläsning ej byggd än | [x] |
| Datahantering JSON eller CSV | save_profile, export_logs_csv | [ ] |
| Minst en klass | User, DailyLog | [x] |
| Barnklass med arv | CutProfile(User), med super() | [x] |
| Standardbibliotek | json, csv, datetime, statistics | [ ] |
| Externt bibliotek | matplotlib | [ ] |
| API eller extern fil | Open Food Facts, alternativt CSV-inläsning | [ ] |
| Programmet körs utan kritiska fel | hela notebooken uppifrån och ner | [ ] |
| Datafil skapad och sparad | cuttrack_loggar.csv | [ ] |
| Notebook med markdown-celler som förklarar | .ipynb | [ ] |
| README komplett | mål, metod, resultat, analys, certifikat, reflektion, länk, installation | [ ] |
| GitHub-repo med länk i README | repo | [ ] |
| Minst 15 commits | repo | [ ] |
| Jag kan förklara varje del muntligt | hela projektet | [ ] |
| Zip med alla tre filerna inlämnad | lärarplattformen | [ ] |

## Checklista, VG-utbyggnaden
Påbörjas först när hela G-listan ovan är avbockad.

| Moment | Var i CutTrack | Klart |
| --- | --- | --- |
| Kod uppdelad i egna filer | models.py, analysis.py | [ ] |
| Konsekvent PEP 8-namngivning | hela koden | [ ] |
| Diagram för protein och steg | plot-funktionerna | [ ] |
| Specifik felhantering per feltyp | API-anrop och filhantering | [ ] |
| Val av analysperiod, 7, 14 eller 30 dagar | run_menu | [ ] |
| Djupare reflektion i README | README | [ ] |

## Senaste uppdateringar
(fylls på löpande, senaste överst)

- 2026-09-16: CutProfile byggd som barnklass till User med `super().__init__()`. Innehåller current_weight (senaste loggade vikten, faller tillbaka på start_weight), calculate_bmr (Mifflin-St Jeor, räknas på aktuell vikt), calculate_tdee och protein_goal (räknas på målvikten). Validerar i `__init__` att målvikten är lägre än startvikten och att takten ligger mellan 0 och 1,0 procent per vecka. BMR verifierad mot handräknat facit för både man och kvinna. Testad i VS Code. suggest_calorie_goal och check_goals ej byggda än.
- 2026-09-16: Beslut om att träning loggas som bool (`trained`) i stället för minuter, samt ny metod training_days(days) på User. Notebooken, produktvision.md och teknisk_plan.md uppdaterade.
- 2026-09-15: Dubblettmappar av projektet upptäckta och rensade, alla docs samlade i docs-mappen, repot gjort publikt.
- 2026-09-15: DailyLog, User-stubben och log_today testade och körda med egen inmatning i VS Code, och committade till repot.
- 2026-09-15: DailyLog-klassen skriven, med validering av vikt (0 till 300 kg) och kalorier (0 till 10 000 kcal) i `__init__`. `add_log` ersätter befintlig logg vid samma datum istället för att skapa en dubblett. `log_today` skriven, frågar efter dagens värden med input() och fångar ValueError från datumformat, orimlig vikt/kalorier och textinmatning där tal förväntas.
- User färdigbyggd med get_logs, average_weight, weight_change och training_days. get_logs filtrerar på kalenderdagar och anropas av de andra tre, så urvalsregeln finns på ett ställe.

## Beslut
- Bygg G-versionen klar, testad och förklarbar först. Bygg därefter mot VG om tiden räcker, enligt VG-utbyggnaden i teknisk_plan.md.
- Commit-mål höjt till minst 15 tydliga commits.
- Träning loggas som ja eller nej (bool), inte som antal minuter. Frekvens är det som bevarar muskelmassa under en deff, och går att bedöma mot en tydlig regel.
- BMR räknas på aktuell vikt, inte startvikt, eftersom förbrukningen sjunker under deffen.
- Proteinmålet räknas på målvikten och ligger därmed fast genom hela deffen.
- Välkomsttext, riktlinjer och motiverande utskrifter byggs i samband med check_goals och menyn. Texten ska bygga på personens egna siffror, inte generell peppning, och strukturen görs med tomrader och rubriker i stället för centrering.

## Att verifiera mot källa innan koden skrivs
Alla ska anges i README:s metodavsnitt. Kan komma som muntlig fråga.
- [ ] Mifflin-St Jeor, formel och aktivitetsfaktorer
- [ ] 7700 kcal per kilo kroppsfett, ursprung och kritiken mot regeln
- [ ] Takt 0,5 till 1,0 procent per vecka, Garthe m.fl. 2011
- [ ] Protein per kilo, Helms m.fl. 2014 och nyare metaanalys
- [x] Kalorigolv beslutat: högsta av fast gräns (1200 kvinnor / 1500 män) och personens BMR. Källa: amerikanska obesitasriktlinjerna 2013. Läs källan själv före redovisning.

## Muntlig träning, sittande
- [x] Skillnaden mellan `class CutProfile(User)` (ger metoderna) och `super().__init__()` (sätter attributen). Repeteras vid nästa arvsmoment.
- [ ] get_logs, förklara med egna ord utan att titta i koden
- [ ] add_log, förklara varför dubbletter ersätts
- [ ] Varför None och inte 0 för waist, och varför training_days returnerar 0 men average_weight None

## Öppna frågor
Inga öppna just nu.