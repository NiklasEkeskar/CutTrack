# Statuslogg CutTrack

## Vad "klart" betyder
Ett moment bockas av först när allt tre stämmer:
1. koden finns och körs utan fel
2. jag har testat den med riktig data
3. jag kan förklara den muntligt utan att läsa innantill

## Checklista, G-versionen
| Moment | Var i CutTrack | Klart |
| --- | --- | --- |
| Variabler och datatyper | DailyLog-attributen, profilen | [ ] |
| Valfria värden (None) | waist i DailyLog | [ ] |
| If-satser | check_goals, run_menu, filinläsning | [ ] |
| Loop | for över loggar, while i run_menu | [ ] |
| 3 till 5 egna funktioner | load_profile, save_profile, export_logs_csv, calculate_trend, plot_weight | [ ] |
| Felhantering med try/except | filinläsning, DailyLog-validering | [ ] |
| Datahantering JSON eller CSV | save_profile, export_logs_csv | [ ] |
| Minst en klass | User, DailyLog | [ ] |
| Barnklass med arv | CutProfile(User) | [ ] |
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

## Beslut
- Bygg G-versionen klar, testad och förklarbar först. Bygg därefter mot VG om tiden räcker, enligt VG-utbyggnaden i teknisk_plan.md.
- Commit-mål höjt till minst 15 tydliga commits.

## Att verifiera mot källa innan koden skrivs
Alla ska anges i README:s metodavsnitt. Kan komma som muntlig fråga.
- [ ] Mifflin-St Jeor, formel och aktivitetsfaktorer
- [ ] 7700 kcal per kilo kroppsfett, ursprung och kritiken mot regeln
- [ ] Takt 0,5 till 1,0 procent per vecka, Garthe m.fl. 2011
- [ ] Protein per kilo, Helms m.fl. 2014 och nyare metaanalys
- [x] Kalorigolv beslutat: högsta av fast gräns (1200 kvinnor / 1500 män) och personens BMR. Källa: amerikanska obesitasriktlinjerna 2013. Läs källan själv före redovisning.

## Öppna frågor
- [ ] Gör repot publikt före inlämning (ligger privat nu, läraren kommer inte åt länken)
