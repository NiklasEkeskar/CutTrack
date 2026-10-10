# CutTrack, kravspecifikation

Det här dokumentet beskriver vad CutTrack ska kunna och vilka krav koden ska uppfylla. `produktvision.md` beskriver varför, `teknisk_plan.md` beskriver hur. Statuskolumnen visar vad som är byggt och styr roadmapen i `statuslogg.md`.

Status senast kontrollerad mot koden: 2026-10-10.

## Användare

Primär användare är en person som deffar och vill följa sin viktnedgång utan att tappa muskelmassa. Personen behöver inte kunna programmera. Flera personer ska kunna använda programmet på samma dator, var och en med egen profil och egna loggar.

## Användningsfall

1. Skapa en profil.
2. Logga dagens data.
3. Se analys för en period (7, 14 eller 30 dagar).
4. Se diagram över utvecklingen.
5. Få ett kaloriförslag.
6. Läsa in loggar från och exportera loggar till CSV.
7. Spara och fortsätta nästa dag.

## Funktionella krav

Status är Klart, Delvis eller Ej byggt.

### Profil

| ID | Krav | Status |
| --- | --- | --- |
| F1 | Användaren kan skapa en profil med längd, ålder, kön, aktivitetsnivå, startvikt, målvikt och önskad takt i procent per vecka. | Klart |
| F2 | Orimliga profilvärden avvisas: målvikten ska vara lägre än startvikten och takten ligga mellan 0 och 1,0 procent per vecka. | Klart, men `nan` (not a number) godtas som vikt och takt, se statuslogg.md, Luckor |
| F3 | Profilen sparas som en JSON-fil per användare och laddas vid nästa start. | Klart |
| F4 | Filnamnet byggs säkert från användarnamnet, bara a till z och siffror. | Klart |
| F23 | Användaren kan ställa in eget proteinmål (gram per kilo), stegmål och träningsmål när profilen skapas. | Delvis. Fälten finns i profilen och JSON-filen, men menyn frågar inte efter dem. Standardvärdena gäller. |

### Loggning

| ID | Krav | Status |
| --- | --- | --- |
| F5 | Daglig logg med datum, vikt, kalorier, protein, steg, träning (ja eller nej) och midjemått (valfritt). | Klart |
| F6 | En ny logg för ett datum som redan finns ersätter den gamla, och användaren får veta det. | Klart |
| F7 | Orimliga värden avvisas: vikten ska vara över 0 och högst 300 kg, kalorierna mellan 0 och 10 000. | Klart, men `nan` (not a number) godtas som vikt och kalorier, se statuslogg.md, Luckor |
| F8 | Loggar kan exporteras till och läsas in från CSV. Exporten får ett eget filnamn per användare, `<namn>_loggar.csv`. En rad med ogiltiga värden hoppas över och resten läses in. | Klart |

### Beräkningar

| ID | Krav | Status |
| --- | --- | --- |
| F9 | Kaloriförslag: basalomsättning enligt Mifflin-St Jeor på aktuell vikt, gånger aktivitetsfaktor, minus underskott från önskad takt (7700 kcal per kilo). | Klart |
| F10 | Kalorigolv: förslaget går aldrig under det högsta av basalomsättningen och 1 500 kcal (män) respektive 1 200 kcal (kvinnor). Slår golvet i säger programmet vad som hände och vilken takt användaren faktiskt får. | Klart |
| F11 | Proteinmålet är målvikt gånger gram per kilo, standard 1,9. | Klart |

### Analys och råd

| ID | Krav | Status |
| --- | --- | --- |
| F12 | Analys för vald period (7, 14 eller 30 dagar) av viktens takt i procent per vecka, protein, träningsfrekvens och steg. | Klart |
| F13 | Vikttakten bedöms mot användarens eget mål (undre gräns) och ett fast säkerhetstak på 1,0 procent per vecka (övre gräns). Ökande vikt flaggas alltid. | Klart. Takten räknas enligt F24. |
| F14 | Programmet väntar med bedömningen: en period för att visa ett snitt, två perioder för att bedöma takten. Under väntetiden visas hur många dagar som återstår. | Delvis. Byggt och provkört 2026-10-10, inte genomgånget. Dagräkningen (`days_since_start`) utgår från det tidigaste av profilens startdatum och den tidigaste loggen och slutar vid senaste loggade dagen, båda dagarna medräknade. Loggar som är äldre än profilen, till exempel exempelfilen i en ny profil, ger därför inte längre ett negativt antal dagar. Datumen görs om till datum och jämförs inte som text. Ett ogiltigt datum kommer sedan 2026-10-10 inte längre in i en logg eller ett startdatum (D1, byggt men inte genomgånget), så `ValueError` i `days_since_start` kan bara uppstå om någon ändrat ett datum direkt i koden. Bockas av när punkten är genomgången, se statuslogg.md, Steg 1. |
| F15 | Protein, steg och träning analyseras direkt, redan under väntetiden, eftersom de bara kräver ett snitt. | Ej byggt. `check_goals` skriver väntetexten och avbryter, så inget område analyseras förrän perioden är full. |
| F16 | Sjudagarssnittet av vikten visas under dag 7 till 13. | Ej byggt. Väntetexten säger att snittet kan visas, men inget snitt skrivs ut. |
| F17 | Statusöversikt för alla områden plus en sak att fokusera på, i ordningen vikt, protein, träning, steg. | Klart, men slutraden "Allt ligger inom mål just nu" skrivs även när vikten inte kunde bedömas. Se statuslogg, Luckor och steg 1. |
| F18 | Midjemått jämförs mot vikt: vikt ner och midja ner pekar mot fettförlust, vikt ner och midja oförändrad är en varningssignal. | Ej byggt. Midjemåttet sparas men ingen kod läser det. |
| F24 | Takten räknas på snitt, inte på enskilda vägningar: snittet för senaste perioden jämförs med snittet för perioden före. Oförändrad vikt har en egen text. | Klart. Byggt och provkört 2026-10-10, genomgånget samma dag. Takten är skillnaden mellan snittet för senaste perioden och snittet för perioden före, delad på periodens längd och gånger sju (kilo per vecka), och procenttalet räknas på det senaste snittet. `get_logs` och `average_weight` har fått `offset_days` för att hämta perioden före. Skillnader under 0,05 kg per vecka får texten "oförändrad" i stället för "minskar med -0.0 procent per vecka", och saknas vägningar i någon av perioderna skrivs "för lite data". Två perioder krävs för alla periodlängder, så en 30 dagars period bedöms först efter 60 dagar. Begränsningar: bara en vägning per period krävs, och luckor i loggningen gör takten mindre exakt. Allt som beror på hur takten räknas ligger i `tests/test_readme_example.py`. |

### Diagram

| ID | Krav | Status |
| --- | --- | --- |
| F19 | Diagram över viktutvecklingen med rullande sjudagarssnitt och målvikt. | Klart |
| F20 | Diagram för protein och steg med rullande sjudagarssnitt och mållinje. | Delvis. Funktionerna finns i `analysis.py` men nås inte från menyn. |

### Gränssnitt och information

| ID | Krav | Status |
| --- | --- | --- |
| F21 | Textmeny med val för att logga, visa analys, visa diagram, visa kaloriförslag, läsa in CSV samt spara och avsluta. | Klart, startas med `python main.py` |
| F22 | Ansvarsfriskrivningen visas i README, vid start och i samband med kaloriberäkningen. Kaloriförslaget presenteras som en startpunkt som ska justeras efter ett par veckors utfall. | Delvis. Friskrivningen visas i README och vid start, inte vid kaloriförslaget, och ingen text säger att förslaget ska justeras. |

## Datakrav

| ID | Krav | Status |
| --- | --- | --- |
| D1 | Datum skrivs ÅÅÅÅ-MM-DD, så att de sorteras rätt som text och läses av `datetime`. | Delvis. Byggt och provkört 2026-10-10, inte genomgånget. `normalize_date` i `models.py` kontrollerar att datumet finns och skriver om det med nollor (`2026-10-8` blir `2026-10-08`). `DailyLog` och `User` (startdatumet) anropar den, så kontrollen gäller för menyn, CSV-inläsning och profilfiler, och `log_today` anropar den först så att ett fel datum stoppar före de andra frågorna. Ett datum som inte finns eller inte är text ger ett svenskt `ValueError`: menyn säger att loggen inte sparades, `import_logs_csv` hoppar över raden och `load_profile` säger att filen innehåller ogiltiga värden. Eftersom alla datum nu har nollor ger `current_weight` och `weight_change` rätt svar även när datumet skrevs utan nolla. Kvar: ett datum i framtiden eller med fel år godtas (kontrollen gäller bara att datumet finns och har formatet), och ett datum med mellanslag före eller efter avvisas. Se statuslogg.md, Luckor och Steg 1. |
| D2 | Ett saknat värde är `None`, aldrig 0, och kontrolleras med `is not None`. | Klart |
| D3 | Snitt och trender räknas på kalenderdagar bakåt från det senast loggade datumet, inte på antal loggar. | Klart |
| D4 | Personlig data lämnar inte datorn. Profilfiler (`*.json`) och användarens egna CSV-exporter ignoreras av git. Exempeldata ligger i en egen incheckad fil, `data/exempel_loggar.csv`. | Klart. Menyn startas från terminalen med `python main.py` och notebooken kör den inte, så det programmet skriver ut (namn, vikter, kalorier) hamnar inte i notebookens utdata. Provas menyn i en notebookcell ändå ska cellens utdata rensas före commit, det står i notebooken under Kör programmet. Exempelfilen är den enda CSV-filen som checkas in, och exporten får ett eget filnamn per användare (`<namn>_loggar.csv`) som `.gitignore` ignorerar. |

## Säkerhets- och hälsokrav

| ID | Krav | Status |
| --- | --- | --- |
| H1 | Säkerhetstaket på 1,0 procent per vecka och kalorigolvet går inte att ställa in bort. | Klart |
| H2 | Programmet ger allmänna riktvärden och är inte medicinsk rådgivning. | Klart, se även F22 |
| H3 | Förenklingar och begränsningar (till exempel 7700-regeln och att kroppsfett inte mäts) redovisas öppet i README. | Klart |
| H4 | Programmet justerar aldrig ett förslag tyst. När en gräns slår i ska användaren få veta vad som hände och varför. | Klart |

## Icke-funktionella krav

| ID | Krav | Status |
| --- | --- | --- |
| N1 | All text som visas för användaren är på svenska. Klasser, funktioner och variabler namnges på engelska enligt PEP 8. Commit-meddelanden skrivs på engelska. | Delvis. Programmets egna texter är på svenska, men tre sorters meddelanden innehåller Pythons eller operativsystemets engelska text: felet efter "Loggen sparades inte" (`could not convert string to float: 'abc'`), felet när en CSV-rad med ogiltiga värden hoppas över och felet när sparning, export eller inläsning av en fil misslyckas (`[Errno 13] Permission denied`). Upptäckt 2026-10-09 när menyn testades. Datumfelet är på svenska sedan 2026-10-10 (D1, byggt men inte genomgånget): `normalize_date` skriver meddelandet själv, i stället för Pythons `time data '...' does not match format '%Y-%m-%d'`. Se statuslogg.md, Luckor. |
| N2 | Ren och underhållbar kod framför smart kod. Befintliga mönster följs innan nya införs. Kommentarer förklarar varför, inte vad. | Klart |
| N3 | Dålig inmatning, en skadad fil eller en trasig CSV-rad får aldrig krascha programmet. Fel fångas specifikt (`ValueError`, `KeyError`, `JSONDecodeError`, `OSError`) och användaren får ett begripligt meddelande. | Delvis. Upptäckt när testerna skrevs 2026-10-08: fem fall gav ett Python-fel i stället för ett meddelande. Ett av dem, ett ogiltigt datum i en CSV-fil eller profilfil, är rättat 2026-10-10 (D1, byggt men inte genomgånget). Fyra kvar: en CSV-rad med för få kolumner (`TypeError`), en CSV-fil som inte är UTF-8 (`UnicodeDecodeError`), en profilfil med fel struktur eller fel typer (`TypeError`) och en profilfil som inte går att läsa som fil (`OSError`). Hit hör också att en profilfil som inte går att läsa ersätts av en ny tom profil vid menyval 6, vilket provades 2026-10-10 och tappar alla loggar i filen. Se statuslogg.md, Luckor. |
| N4 | Körberoenden är standardbiblioteket plus matplotlib. Utvecklingsberoenden (pytest, bara för att köra testerna) räknas separat. Ett nytt externt bibliotek kräver att det underhålls, fungerar med aktuell Python och att det går att motivera varför det behövs. | Klart. pytest 9.1.1 kontrollerat mot PyPI 2026-10-08, och matplotlib 3.11.2 och pytest 9.1.1 kontrollerade igen 2026-10-09, se teknisk_plan.md, Bibliotek. Hur beroendena installeras står i N9. |
| N5 | Programmet går att starta utan Jupyter, med ett kommando. | Klart. Byggt och provkört 2026-10-09, genomgånget samma dag: `python main.py` startar menyn, skyddet `if __name__ == "__main__":` gör att menyn inte startar när `main.py` importeras, och tre tester i `tests/test_main.py` kör Python som eget program: två startar `python main.py` och ett provar att `import main` inte startar menyn. |
| N6 | Reglerna (validering, kalenderdagsfönstret, kaloriförslag och golv, vikttakt, väntetid) och filhanteringen (filnamn, profilfiler, CSV-inläsning med trasiga rader) täcks av automatiska tester. | Klart. Byggt och provkört 2026-10-08, genomgånget 2026-10-09: 140 tester med pytest i `tests/` täcker reglerna i `models.py` och allt i `analysis.py` utom diagrammen. Diagrammen är inte testade. Menyn har egna tester, se N8. F24 lade 2026-10-10 till 19 tester (7 i `test_models.py` och 12 i `test_readme_example.py`) och tog bort tre som låste den gamla takträkningen, så sviten blev 247 tester. De nya testerna är genomgångna 2026-10-10. Rättningen av `days_since_start` lade samma dag till 10 tester (8 i `test_models.py`, 1 i `test_readme_example.py` och 1 i `test_main.py`), så sviten var 257 tester. Datumkontrollen (D1) lade samma dag till 59 tester (44 i `test_models.py`, 9 i `test_main.py` och 6 i `test_analysis.py`) och ändrade ett i `test_models.py`, så sviten är nu 316 tester. De 10 och de 59 nya testerna är byggda och provkörda men inte genomgångna. |
| N7 | Dokumentationen hålls i synk med koden, och kod finns på ett ställe. | Delvis. Klasser och funktioner finns bara i `models.py`, `analysis.py` och `main.py`, och notebooken importerar dem. Notebookens förklaringstexter är inte genomgångna mot koden sedan kursfasen. Texterna om menyn och hur programmet startas skrevs om 2026-10-09 när koden flyttade till `main.py`. F24 ändrade 2026-10-10 fyra förklaringsceller (metoderna i `User`, `get_logs`, `check_goals` och rubriken över utskrifterna vid olika tidpunkter) och de sparade utskrifterna i två celler, men resten är inte genomgånget. Rättningen av `days_since_start` ändrade samma dag förklaringscellen om `days_since_start` och `waiting_message`. Datumkontrollen (D1) ändrade samma dag sex förklaringsceller (inledningen, `DailyLog`, `get_logs`, `days_since_start`, `log_today` och testcellen för egen inmatning), valideringscellen under CutProfile (ny kod och ny utskrift) och den sparade utskriften i cellen som kör `log_today`. |
| N8 | Menyn (frågor, profilskapande, loggning, menyval och avslut) och startpunkten `python main.py` täcks av automatiska tester som matar in svaren utan tangentbord. | Klart. Byggt och provkört 2026-10-09, genomgånget samma dag: 91 tester i `tests/test_main.py`, och 120 avsiktliga fel i `main.py` upptäcks av dem. Analysen och diagrammet ersätts av stubbar i testerna, så deras utskrifter testas inte härifrån. Brister i menyn som inte är rättade än är inte låsta med tester (statuslogg.md, Luckor). Ett 92:a test lades till 2026-10-10: en ny användare läser in exempelfilen och får en riktig analys, utan stubbar. Det är byggt och provkört men inte genomgånget. Datumkontrollen (D1) lade samma dag till 9 tester: datumet sparas med nollor, samma dag med och utan nolla blir en logg, ett datum som inte finns ger ett svenskt meddelande, och datumet kontrolleras före de andra frågorna. De är byggda och provkörda men inte genomgångna, så `tests/test_main.py` har nu 101 tester. |
| N9 | Programmets beroenden installeras med ett kommando, och körberoenden (matplotlib) och utvecklingsberoenden (pytest) ligger i skilda filer med lägsta och högsta version. Den lägsta versionen är provad. | Klart. Byggt och provkört 2026-10-09, genomgånget samma dag: `requirements.txt` har `matplotlib>=3.11,<4` och `requirements-dev.txt` tar med den och lägger till `pytest>=9.1,<10`. Installerat i nya virtuella miljöer på Python 3.11, 3.12, 3.13 och 3.14 med de senaste versionerna, och på 3.11 och 3.14 med de lägsta som filerna tillåter (matplotlib 3.11.0, pytest 9.1.0). Med bara `requirements.txt` saknas pytest och `python main.py` kör igenom en inskriven session. Med `requirements-dev.txt` går alla 231 tester igenom, och de tre diagramfunktionerna ritar utan varningar. Python 3.10 är inte provat och går inte att använda, eftersom matplotlib 3.11 kräver 3.11. |
| N10 | Projektet har en öppen licens i filen `LICENSE`, och README förklarar vad den innebär. | Klart. Byggt 2026-10-09, genomgånget samma dag: MIT med `Copyright (c) 2026 Niklas Ekeskär`, texten jämförd byte för byte med GitHubs mall och med SPDX:s MIT-text. README har ett avsnitt Licens. Filen ligger på main på GitHub, och Community standards listar licensen. Licensen gäller bara det som ägaren har rättigheter i, och upphovsrätten i rent AI-genererad kod är oklar (statuslogg.md, Beslut). Ansvarsbegränsningen i licensen ersätter inte hälsofriskrivningen, se F22. |

## Utanför omfattning

- Medicinsk rådgivning eller diagnos.
- Kroppsfettsprocent eller andra mätningar av kroppssammansättning.
- En AI- eller maskininlärningsmodell. Den kräver betydligt fler observationer än ett enskilt projekt har, se roadmapen.
- Konton, inloggning och molnlagring.
- Andra lägen än deff (viktbalans, muskelbygge). Arkitekturen är förberedd för dem men de är inte byggda.

## Vad klart betyder

Ett krav är klart först när koden körs utan fel, är testad med realistisk data (och när det finns tester, av testerna) och går att förklara för en annan utvecklare utan att läsa innantill.
