# CutTrack, kravspecifikation

Det här dokumentet beskriver vad CutTrack ska kunna och vilka krav koden ska uppfylla. `produktvision.md` beskriver varför, `teknisk_plan.md` beskriver hur. Statuskolumnen visar vad som är byggt och styr roadmapen i `statuslogg.md`.

Status senast kontrollerad mot koden: 2026-10-09.

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
| F13 | Vikttakten bedöms mot användarens eget mål (undre gräns) och ett fast säkerhetstak på 1,0 procent per vecka (övre gräns). Ökande vikt flaggas alltid. | Klart, men takten räknas på ett sätt som ska bytas, se F24 |
| F14 | Programmet väntar med bedömningen: en period för att visa ett snitt, två perioder för att bedöma takten. Under väntetiden visas hur många dagar som återstår. | Klart, men dagräkningen blir fel när loggar är äldre än profilens startdatum: `days_since_start` ger då ett negativt antal dagar. Se statuslogg.md, Steg 1. |
| F15 | Protein, steg och träning analyseras direkt, redan under väntetiden, eftersom de bara kräver ett snitt. | Ej byggt. `check_goals` skriver väntetexten och avbryter, så inget område analyseras förrän perioden är full. |
| F16 | Sjudagarssnittet av vikten visas under dag 7 till 13. | Ej byggt. Väntetexten säger att snittet kan visas, men inget snitt skrivs ut. |
| F17 | Statusöversikt för alla områden plus en sak att fokusera på, i ordningen vikt, protein, träning, steg. | Klart |
| F18 | Midjemått jämförs mot vikt: vikt ner och midja ner pekar mot fettförlust, vikt ner och midja oförändrad är en varningssignal. | Ej byggt. Midjemåttet sparas men ingen kod läser det. |
| F24 | Takten räknas på snitt, inte på enskilda vägningar: snittet för senaste perioden jämförs med snittet för perioden före. | Ej byggt. Takten räknas från första och sista vägningen i perioden och delas med periodens längd i stället för med antalet dagar mellan vägningarna, vilket ger ungefär 14 procent för låg takt på sjudagarsperioden. En enskild vägning kan flytta resultatet med flera tiondels procentenheter. Oförändrad vikt ger texten "minskar med -0.0 procent per vecka". Dagens takträkning är låst av tester i `tests/test_readme_example.py`, som ska ändras först när metoden byts. |

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
| D1 | Datum skrivs ÅÅÅÅ-MM-DD, så att de sorteras rätt som text och läses av `datetime`. | Delvis. `log_today` kontrollerar datumet med `strptime`, som godtar `2026-10-8`, men sparar texten som den skrevs. `current_weight`, `days_since_start` och `weight_change` jämför datum som text, så ett datum utan nolla ger fel resultat utan felmeddelande. `DailyLog` validerar inte datumet alls, så ett ogiltigt datum i en CSV-fil läses in och kraschar först i `get_logs`. Se statuslogg.md, Luckor. |
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
| N1 | All text som visas för användaren är på svenska. Klasser, funktioner och variabler namnges på engelska enligt PEP 8. Commit-meddelanden skrivs på engelska. | Delvis. Programmets egna texter är på svenska, men tre sorters meddelanden innehåller Pythons eller operativsystemets engelska text: felet efter "Loggen sparades inte" (`could not convert string to float: 'abc'`), felet när en CSV-rad med ogiltiga värden hoppas över och felet när sparning, export eller inläsning av en fil misslyckas (`[Errno 13] Permission denied`). Upptäckt 2026-10-09 när menyn testades. Se statuslogg.md, Luckor. |
| N2 | Ren och underhållbar kod framför smart kod. Befintliga mönster följs innan nya införs. Kommentarer förklarar varför, inte vad. | Klart |
| N3 | Dålig inmatning, en skadad fil eller en trasig CSV-rad får aldrig krascha programmet. Fel fångas specifikt (`ValueError`, `KeyError`, `JSONDecodeError`, `OSError`) och användaren får ett begripligt meddelande. | Delvis. Upptäckt när testerna skrevs 2026-10-08: fem fall ger fortfarande ett Python-fel i stället för ett meddelande. En CSV-rad med för få kolumner (`TypeError`), en CSV-fil som inte är UTF-8 (`UnicodeDecodeError`), ett ogiltigt datum i en CSV-fil (läses in, kraschar sedan i `get_logs`), en profilfil med fel struktur eller fel typer (`TypeError`) och en profilfil som inte går att läsa som fil (`OSError`). Se statuslogg.md, Luckor. |
| N4 | Körberoenden är standardbiblioteket plus matplotlib. Utvecklingsberoenden (pytest, bara för att köra testerna) räknas separat. Ett nytt externt bibliotek kräver att det underhålls, fungerar med aktuell Python och att det går att motivera varför det behövs. | Klart. pytest 9.1.1 kontrollerat mot PyPI 2026-10-08, och matplotlib 3.11.2 och pytest 9.1.1 kontrollerade igen 2026-10-09, se teknisk_plan.md, Bibliotek. Hur beroendena installeras står i N9. |
| N5 | Programmet går att starta utan Jupyter, med ett kommando. | Klart. Byggt och provkört 2026-10-09, genomgånget samma dag: `python main.py` startar menyn, skyddet `if __name__ == "__main__":` gör att menyn inte startar när `main.py` importeras, och tre tester i `tests/test_main.py` kör Python som eget program: två startar `python main.py` och ett provar att `import main` inte startar menyn. |
| N6 | Reglerna (validering, kalenderdagsfönstret, kaloriförslag och golv, vikttakt, väntetid) och filhanteringen (filnamn, profilfiler, CSV-inläsning med trasiga rader) täcks av automatiska tester. | Klart. Byggt och provkört 2026-10-08, genomgånget 2026-10-09: 140 tester med pytest i `tests/` täcker reglerna i `models.py` och allt i `analysis.py` utom diagrammen. Diagrammen är inte testade. Menyn har egna tester, se N8. |
| N7 | Dokumentationen hålls i synk med koden, och kod finns på ett ställe. | Delvis. Klasser och funktioner finns bara i `models.py`, `analysis.py` och `main.py`, och notebooken importerar dem. Notebookens förklaringstexter är inte genomgångna mot koden sedan kursfasen. Texterna om menyn och hur programmet startas skrevs om 2026-10-09 när koden flyttade till `main.py`. |
| N8 | Menyn (frågor, profilskapande, loggning, menyval och avslut) och startpunkten `python main.py` täcks av automatiska tester som matar in svaren utan tangentbord. | Klart. Byggt och provkört 2026-10-09, genomgånget samma dag: 91 tester i `tests/test_main.py`, och 120 avsiktliga fel i `main.py` upptäcks av dem. Analysen och diagrammet ersätts av stubbar i testerna, så deras utskrifter testas inte härifrån. Brister i menyn som inte är rättade än är inte låsta med tester (statuslogg.md, Luckor). |
| N9 | Programmets beroenden installeras med ett kommando, och körberoenden (matplotlib) och utvecklingsberoenden (pytest) ligger i skilda filer med lägsta och högsta version. Den lägsta versionen är provad. | Klart. Byggt och provkört 2026-10-09, genomgånget samma dag: `requirements.txt` har `matplotlib>=3.11,<4` och `requirements-dev.txt` tar med den och lägger till `pytest>=9.1,<10`. Installerat i nya virtuella miljöer på Python 3.11, 3.12, 3.13 och 3.14 med de senaste versionerna, och på 3.11 och 3.14 med de lägsta som filerna tillåter (matplotlib 3.11.0, pytest 9.1.0). Med bara `requirements.txt` saknas pytest och `python main.py` kör igenom en inskriven session. Med `requirements-dev.txt` går alla 231 tester igenom, och de tre diagramfunktionerna ritar utan varningar. Python 3.10 är inte provat och går inte att använda, eftersom matplotlib 3.11 kräver 3.11. |
| N10 | Projektet har en öppen licens i filen `LICENSE`, och README förklarar vad den innebär. | Delvis. Byggt 2026-10-09, inte genomgånget: MIT med `Copyright (c) 2026 Niklas Ekeskär`, texten jämförd byte för byte med GitHubs mall och med SPDX:s MIT-text. README har ett avsnitt Licens. Licensen gäller bara det som ägaren har rättigheter i, och upphovsrätten i rent AI-genererad kod är oklar (statuslogg.md, Beslut). Ansvarsbegränsningen i licensen ersätter inte hälsofriskrivningen, se F22. Att GitHub känner igen licensen bekräftas efter push. |

## Utanför omfattning

- Medicinsk rådgivning eller diagnos.
- Kroppsfettsprocent eller andra mätningar av kroppssammansättning.
- En AI- eller maskininlärningsmodell. Den kräver betydligt fler observationer än ett enskilt projekt har, se roadmapen.
- Konton, inloggning och molnlagring.
- Andra lägen än deff (viktbalans, muskelbygge). Arkitekturen är förberedd för dem men de är inte byggda.

## Vad klart betyder

Ett krav är klart först när koden körs utan fel, är testad med realistisk data (och när det finns tester, av testerna) och går att förklara för en annan utvecklare utan att läsa innantill.
