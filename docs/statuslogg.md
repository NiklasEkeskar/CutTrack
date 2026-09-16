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
| If-satser | log_today, add_log, CutProfile-validering, check_goals (prioritering och gränser) | [x] |
| Loop | add_log, get_logs, average_weight, average_protein, average_steps, weight_change, training_days, current_weight, days_since_start | [x] |
| 3 till 5 egna funktioner | load_profile, save_profile, export_logs_csv, plot_weight | [ ] |
| Felhantering med try/except | log_today (DailyLog- och CutProfile-validering), byggd och testad. filinläsning ej byggd än | [x] |
| Datahantering JSON eller CSV | save_profile, export_logs_csv | [ ] |
| Minst en klass | User, DailyLog | [x] |
| Barnklass med arv | CutProfile(User), med super() | [x] |
| Standardbibliotek | datetime använt. json, csv, statistics ej använda än | [ ] |
| Externt bibliotek | matplotlib | [ ] |
| API eller extern fil | Open Food Facts, alternativt CSV-inläsning | [ ] |
| Programmet körs utan kritiska fel | hela notebooken uppifrån och ner | [ ] |
| Datafil skapad och sparad | cuttrack_loggar.csv | [ ] |
| Notebook med markdown-celler som förklarar | .ipynb | [x] |
| README komplett | mål, metod, resultat, analys, certifikat, reflektion, länk, installation | [ ] |
| GitHub-repo med länk i README | repo | [ ] |
| Minst 15 commits | repo, 23 commits nu | [x] |
| Jag kan förklara varje del muntligt | DailyLog, User, CutProfile klart. suggest_calorie_goal och check_goals nyligen byggda, öva mer | [ ] |
| Zip med alla tre filerna inlämnad | lärarplattformen | [ ] |

## Checklista, VG-utbyggnaden
Påbörjas först när hela G-listan ovan är avbockad. Läraren har sagt att projektet inte behöver vara mer avancerat än kraven anger, så VG är lågt prioriterat med den tid som återstår.

| Moment | Var i CutTrack | Klart |
| --- | --- | --- |
| Kod uppdelad i egna filer | models.py, analysis.py | [ ] |
| Konsekvent PEP 8-namngivning | hela koden | [ ] |
| Diagram för protein och steg | plot-funktionerna | [ ] |
| Specifik felhantering per feltyp | API-anrop och filhantering | [ ] |
| Val av analysperiod, 7, 14 eller 30 dagar | run_menu | [ ] |
| Djupare reflektion i README | README | [ ] |

## Kvar i G-versionen
1. Filnamnshantering, bygga säkert filnamn från användarnamnet, teckenvis i en loop
2. save_profile och load_profile, JSON
3. export_logs_csv, CSV, detta är datafilen som lämnas in
4. plot_weight, matplotlib
5. run_menu, CLI-loop med while, inklusive välkomsttext, riktlinjer och ansvarsfriskrivning
6. README
7. Open Food Facts, tilläggsfunktion, kan hoppas över eftersom CSV-inläsning täcker API-kravet

## Senaste uppdateringar
(fylls på löpande, senaste överst)

- 2026-09-16: calculate_trend struken ur teknisk_plan.md. average_weight och weight_change på User gör redan det jobbet via get_logs, en separat funktion hade gjort samma sak två gånger. De fyra egna funktionerna är nu load_profile, save_profile, export_logs_csv, plot_weight.
- 2026-09-16: check_goals byggd på CutProfile, med days_since_start och waiting_message. Prioritetsordning vikt, protein, träningsfrekvens, steg, en enda focus_area lyfts fram. Vikttrenden bedöms mot personens eget target_rate_percent som undre gräns och ett fast säkerhetstak på 1,0 procent som övre gräns, i stället för ett gemensamt fast intervall. training_goal_days tillagt på CutProfile, standard 3. average_protein och average_steps tillagda på User. Testat med sju scenarier plus två edge-fall (lågt personligt mål som nås snabbare men säkert, högt personligt mål som ändå överskrider säkerhetstaket), alla rätt.
- 2026-09-16: suggest_calorie_goal byggd på CutProfile. Golv som det högsta av basalomsättning och fast gräns (1500 män, 1200 kvinnor). Programmet justerar aldrig tyst, skriver alltid ut vad som hände och att vägen till snabbare takt går via mer aktivitet, inte mindre mat. Testat med tre fall, golv som inte slår i, golv som slår i, och fallet där inget underskott alls går att skapa genom maten.
- 2026-09-16: CutProfile byggd som barnklass till User med super().__init__(). current_weight, calculate_bmr (Mifflin-St Jeor, räknas på aktuell vikt), calculate_tdee, protein_goal (räknas på målvikten). Validerar målvikt och takt i __init__. Testad i VS Code.
- 2026-09-16: Beslut om att träning loggas som bool (trained) i stället för minuter, ny metod training_days(days) på User.
- 2026-09-15: Dubblettmappar av projektet upptäckta och rensade, alla docs samlade i docs-mappen, repot gjort publikt.
- 2026-09-15: DailyLog, User (add_log, get_logs, average_weight, weight_change, training_days) och log_today byggda, testade och committade.

## Beslut
- Bygg G-versionen klar, testad och förklarbar först. VG lågt prioriterat, enligt lärarens besked att projektet inte behöver vara mer avancerat än kraven anger.
- Commit-mål höjt till minst 15 tydliga commits, uppnått.
- Träning loggas som ja eller nej (bool), inte som antal minuter.
- BMR räknas på aktuell vikt, inte startvikt.
- Proteinmålet räknas på målvikten och ligger fast genom hela deffen.
- Vikttrendens undre gräns är personens eget mål, övre gränsen är ett fast säkerhetstak på 1,0 procent, oavsett eget mål.
- calculate_trend byggs inte som egen funktion, average_weight och weight_change täcker det.
- Välkomsttext, riktlinjer och motiverande utskrifter byggs i run_menu och check_goals. Bygger på personens egna siffror, inte generell peppning. Struktur med tomrader och rubriker, inte centrering.
- Övningar där jag ändrar i koden på begäran, inte bara förklarar den, körs efter att G-versionen är klar, med den färdiga koden. Inget separat övningsprojekt.

## Muntlig träning, sittande
- [x] Skillnaden mellan class CutProfile(User) (ger metoderna) och super().__init__() (sätter attributen)
- [x] Varför golvet är det högsta av basalomsättning och fast gräns, inte bara ett fast tal
- [ ] get_logs, förklara med egna ord utan att titta i koden
- [ ] add_log, förklara varför dubbletter ersätts
- [ ] check_goals, förklara varför vikten har två olika sorters gränser
- [ ] waiting_message, förklara varför den räknar från senaste loggade dagen och inte dagens riktiga datum
- [ ] Varför None och inte 0 för waist, och varför training_days returnerar 0 men average_weight None

## Examination, viktigt att hålla isär
- Teoretisk examination: onlinequiz 28 september (grupp 1), 40 frågor, minst 10 rätt. Testar kursens allmänna innehåll, inget med CutTrack att göra.
- Praktisk examination: CutTrack, inlämning före redovisning, sedan redovisning där koden ska förklaras och mindre ändringar göras live.
- Kommentarer i koden rekommenderas av läraren, läggs till som eget steg innan inlämning.

## Att verifiera mot källa innan koden skrivs
Alla ska anges i README:s metodavsnitt. Kan komma som muntlig fråga.
- [ ] Mifflin-St Jeor, formel och aktivitetsfaktorer
- [ ] 7700 kcal per kilo kroppsfett, ursprung och kritiken mot regeln
- [ ] Takt 0,5 till 1,0 procent per vecka, Garthe m.fl. 2011
- [ ] Protein per kilo, Helms m.fl. 2014 och nyare metaanalys
- [x] Kalorigolv beslutat: högsta av fast gräns (1200 kvinnor / 1500 män) och personens BMR. Källa: amerikanska obesitasriktlinjerna 2013. Läs källan själv före redovisning.

## Öppna frågor
Inga öppna just nu.
