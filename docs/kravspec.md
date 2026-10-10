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
| F2 | Orimliga profilvärden avvisas: målvikten ska vara lägre än startvikten och takten ligga mellan 0 och 1,0 procent per vecka. Namn, längd, ålder, kön, aktivitetsnivå, startvikt och målen för protein, steg och träning ska vara av rätt sort och inom rimliga gränser (se statuslogg.md, Beslut). | Klart för målvikt och takt. Resten byggt och provkört 2026-10-10, inte genomgånget: `nan` och värden av fel sort avvisas, längd 100 till 250 cm, ålder 18 till 100 år, namn 1 till 50 tecken. |
| F3 | Profilen sparas som en JSON-fil per användare och laddas vid nästa start. | Delvis. Klart och genomgånget i sin ursprungliga form. Sparningen skrevs om 2026-10-10 (N3), byggd och provkörd men inte genomgången: `save_profile` skriver först till `<namn>.tmp.json` och byter namn med `os.replace` när allt är skrivet, så ett fel mitt i skrivningen lämnar den gamla profilen orörd. Profilen sparas dessutom efter varje ny logg i menyn, inte bara vid val 6. Se N3 och statuslogg.md, Beslut. |
| F4 | Filnamnet byggs säkert från användarnamnet, bara a till z och siffror. | Klart. Två namn kan ge samma filnamn (Åke och Äke blir `ke.json`). Sedan 2026-10-10 laddas en profil bara när namnet i filen är samma som det som skrevs, med valfria versaler och mellanslag (byggt, inte genomgånget). |
| F23 | Användaren kan ställa in eget proteinmål (gram per kilo), stegmål och träningsmål när profilen skapas. | Delvis. Fälten finns i profilen och JSON-filen, men menyn frågar inte efter dem. Standardvärdena gäller. |

### Loggning

| ID | Krav | Status |
| --- | --- | --- |
| F5 | Daglig logg med datum, vikt, kalorier, protein, steg, träning (ja eller nej) och midjemått (valfritt). | Klart |
| F6 | En ny logg för ett datum som redan finns ersätter den gamla, och användaren får veta det. | Klart |
| F7 | Orimliga värden avvisas: vikten ska vara över 0 och högst 300 kg, kalorierna mellan 0 och 10 000, proteinet mellan 0 och 1 000 gram, stegen ett heltal mellan 0 och 100 000, midjemåttet mellan 30 och 250 cm, och träningen ska vara ja eller nej. | Klart för vikt och kalorier. Resten byggt och provkört 2026-10-10, inte genomgånget: `nan` och `inf` avvisas, protein, steg, midjemått och träning kontrolleras. |
| F8 | Loggar kan exporteras till och läsas in från CSV. Exporten får ett eget filnamn per användare, `<namn>_loggar.csv`. En rad med ogiltiga värden hoppas över och resten läses in. | Delvis. Klart och genomgånget 2026-10-08 i sin ursprungliga form. Inläsningen är skriven om 2026-10-10 (N3), byggd och provkörd men inte genomgången. Går det fel på hela filen läses ingenting in och ett meddelande säger vad som är fel: filen är inte UTF-8, går inte att tolka som CSV, är tom eller saknar rubrikrad, har semikolon mellan kolumnerna eller saknar kolumner. En BOM hoppas över. En rad med fler eller färre celler än rubrikraden, ett värde som inte är ett tal eller en träningscell som inte är `True` eller `False` (valfria versaler) hoppas över med ett svenskt meddelande, och en rad där alla celler är tomma hoppas över utan meddelande. Se N3 och statuslogg.md, Beslut. |

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
| F21 | Textmeny med val för att logga, visa analys, visa diagram, visa kaloriförslag, läsa in CSV samt spara och avsluta. | Delvis. Klart och genomgånget, startas med `python main.py`. Menyn ändrades 2026-10-10 (N3), byggd och provkörd men inte genomgången: profilen sparas efter varje ny logg, menyn stannar med ett meddelande när profilfilen finns men inte går att läsa, och val 6 avslutar bara när sparningen lyckades. |
| F22 | Ansvarsfriskrivningen visas i README, vid start och i samband med kaloriberäkningen. Kaloriförslaget presenteras som en startpunkt som ska justeras efter ett par veckors utfall. | Klart, men byggt och inte genomgånget. Sedan 2026-10-10 visar `show_suggestion_note` i `main.py` en rad om att förslaget är en startpunkt och friskrivningen direkt efter kaloriförslaget, både när profilen skapas och i menyval 4. Friskrivningen står i listan `DISCLAIMER_LINES` och används av både välkomsttexten och noten. |

## Datakrav

| ID | Krav | Status |
| --- | --- | --- |
| D1 | Datum skrivs ÅÅÅÅ-MM-DD, så att de sorteras rätt som text och läses av `datetime`. | Delvis. Byggt och provkört 2026-10-10, inte genomgånget. `normalize_date` i `models.py` kontrollerar att datumet finns och skriver om det med nollor (`2026-10-8` blir `2026-10-08`). `DailyLog` och `User` (startdatumet) anropar den, så kontrollen gäller för menyn, CSV-inläsning och profilfiler, och `log_today` anropar den först så att ett fel datum stoppar före de andra frågorna. Ett datum som inte finns eller inte är text ger ett svenskt `ValueError`: menyn säger att loggen inte sparades, `import_logs_csv` hoppar över raden och `load_profile` säger att filen innehåller ogiltiga värden. Eftersom alla datum nu har nollor ger `current_weight` och `weight_change` rätt svar även när datumet skrevs utan nolla. Kvar: ett datum i framtiden eller med fel år godtas (kontrollen gäller bara att datumet finns och har formatet), och ett datum med mellanslag före eller efter avvisas i menyn och i profilfiler (CSV-inläsningen tar bort mellanslagen sedan 2026-10-10). Se statuslogg.md, Luckor och Steg 1. |
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
| N1 | All text som visas för användaren är på svenska. Klasser, funktioner och variabler namnges på engelska enligt PEP 8. Commit-meddelanden skrivs på engelska. | Klart, men byggt och inte genomgånget. Två sorters meddelanden innehöll Pythons eller operativsystemets engelska text: felet efter "Loggen sparades inte" (`could not convert string to float: 'abc'`) och felet när sparning, export eller inläsning av en fil misslyckas (`[Errno 13] Permission denied`). Upptäckt 2026-10-09 när menyn testades. Rättat 2026-10-10: `to_number` i `main.py` skriver till exempel "Vikt måste vara ett tal, men du skrev 'abc'.", och `describe_os_error` i `analysis.py` ger svensk text för de åtta vanligaste filfelen. Ett ovanligt filfel visas fortfarande med operativsystemets text. Felet när en CSV-rad hoppas över är på svenska sedan 2026-10-10 (N3, byggt men inte genomgånget): `parse_number` och `parse_trained` skriver meddelandet själva och nämner kolumnen och vad som stod i cellen. Datumfelet är på svenska sedan 2026-10-10 (D1, byggt men inte genomgånget): `normalize_date` skriver meddelandet själv, i stället för Pythons `time data '...' does not match format '%Y-%m-%d'`. Se statuslogg.md, Luckor. |
| N2 | Ren och underhållbar kod framför smart kod. Befintliga mönster följs innan nya införs. Kommentarer förklarar varför, inte vad. | Klart |
| N3 | Dålig inmatning, en skadad fil eller en trasig CSV-rad får aldrig krascha programmet. Fel fångas specifikt (`ValueError`, `KeyError`, `TypeError`, `JSONDecodeError`, `UnicodeDecodeError`, `csv.Error`, `OSError`) och användaren får ett begripligt meddelande. | Delvis. Upptäckt när testerna skrevs 2026-10-08: fem fall gav ett Python-fel i stället för ett meddelande. Alla fem är rättade 2026-10-10 (byggda och provkörda men inte genomgångna): ett ogiltigt datum i en CSV-fil eller profilfil (D1), en CSV-rad med för få kolumner (`TypeError`), en CSV-fil som inte är UTF-8 (`UnicodeDecodeError`), en profilfil med fel struktur eller fel typer (`TypeError`) och en profilfil som inte går att läsa som fil (`OSError`). CSV-inläsningen fångar dessutom `csv.Error`, och tre fel i den är rättade: `TRUE` och `ja` lästes som ett nej utan meddelande, en BOM eller semikolon gav noll inlästa rader med ett meddelande per rad, och en decimalkomma i sista kolumnen lästes som ett avkortat tal utan meddelande. En profilfil som inte är UTF-8 gav ett meddelande om ogiltiga värden med Pythons engelska text om teckenkodningen, och har nu ett eget meddelande. Profilfilerna rättades tillsammans med skyddet mot dataförlust, eftersom ett meddelande i stället för en krasch annars hade gjort att just den filen skrevs över av en ny tom profil vid menyval 6 (provat 2026-10-10: en profilfil på 772 byte blev 328 byte utan loggar). Nu stannar menyn med ett meddelande och ändrar inte filen. `save_profile` skriver via en temporär fil, så en krasch mitt i skrivningen (provad 2026-10-10: en profil på 781 byte blev en trasig fil på 502 byte) nu lämnar den gamla profilen orörd. Menyn sparar efter varje ny logg, och menyval 6 avslutar bara om sparningen lyckades. Fält med fel typ i profilfilen, till exempel längd eller steg som text eller `"name": 5` som kraschade vid nästa sparning, avvisas sedan 2026-10-10 av klasserna med ett meddelande (F2, F7, byggt men inte genomgånget). Se statuslogg.md, Luckor och Beslut. |
| N4 | Körberoenden är standardbiblioteket plus matplotlib. Utvecklingsberoenden (pytest, bara för att köra testerna) räknas separat. Ett nytt externt bibliotek kräver att det underhålls, fungerar med aktuell Python och att det går att motivera varför det behövs. | Klart. pytest 9.1.1 kontrollerat mot PyPI 2026-10-08, och matplotlib 3.11.2 och pytest 9.1.1 kontrollerade igen 2026-10-09, se teknisk_plan.md, Bibliotek. Hur beroendena installeras står i N9. |
| N5 | Programmet går att starta utan Jupyter, med ett kommando. | Klart. Byggt och provkört 2026-10-09, genomgånget samma dag: `python main.py` startar menyn, skyddet `if __name__ == "__main__":` gör att menyn inte startar när `main.py` importeras, och tre tester i `tests/test_main.py` kör Python som eget program: två startar `python main.py` och ett provar att `import main` inte startar menyn. |
| N6 | Reglerna (validering, kalenderdagsfönstret, kaloriförslag och golv, vikttakt, väntetid) och filhanteringen (filnamn, profilfiler, CSV-inläsning med trasiga rader) täcks av automatiska tester. | Klart. Byggt och provkört 2026-10-08, genomgånget 2026-10-09: 140 tester med pytest i `tests/` täcker reglerna i `models.py` och allt i `analysis.py` utom diagrammen. Diagrammen är inte testade. Menyn har egna tester, se N8. F24 lade 2026-10-10 till 19 tester (7 i `test_models.py` och 12 i `test_readme_example.py`) och tog bort tre som låste den gamla takträkningen, så sviten blev 247 tester. De nya testerna är genomgångna 2026-10-10. Rättningen av `days_since_start` lade samma dag till 10 tester (8 i `test_models.py`, 1 i `test_readme_example.py` och 1 i `test_main.py`), så sviten var 257 tester. Datumkontrollen (D1) lade samma dag till 59 tester (44 i `test_models.py`, 9 i `test_main.py` och 6 i `test_analysis.py`) och ändrade ett i `test_models.py`, så sviten var 316 tester. Den tåligare CSV-inläsningen (N3) lade samma dag till 44 tester i `test_analysis.py`, ersatte ett och ändrade ett, så sviten var 359 tester. Att inte tappa loggar (N3) lade samma dag till 40 tester (19 i `test_analysis.py` och 21 i `test_main.py`) och ändrade två (ett i vardera filen), så sviten var 399 tester. Kontrollen av inmatningen (F2, F7, N1) lade samma dag till 443 tester (237 i `test_models.py`, 79 i `test_analysis.py` och 127 i `test_main.py`) och ändrade ett i `test_analysis.py`, så sviten var 841 tester. Kontrollen av namnet i profilfilen lade samma dag till 16 tester (14 i `test_analysis.py` och 2 i `test_main.py`), så sviten var 857 tester. Texten vid kaloriförslaget (F22) lade samma dag till 5 tester i `test_main.py`, så sviten är nu 862 tester. De 10, de 59, de 44, de 40, de 443, de 16 och de 5 nya testerna är byggda och provkörda men inte genomgångna. |
| N7 | Dokumentationen hålls i synk med koden, och kod finns på ett ställe. | Delvis. Klasser och funktioner finns bara i `models.py`, `analysis.py` och `main.py`, och notebooken importerar dem. Notebookens förklaringstexter är inte genomgångna mot koden sedan kursfasen. Texterna om menyn och hur programmet startas skrevs om 2026-10-09 när koden flyttade till `main.py`. F24 ändrade 2026-10-10 fyra förklaringsceller (metoderna i `User`, `get_logs`, `check_goals` och rubriken över utskrifterna vid olika tidpunkter) och de sparade utskrifterna i två celler, men resten är inte genomgånget. Rättningen av `days_since_start` ändrade samma dag förklaringscellen om `days_since_start` och `waiting_message`. Datumkontrollen (D1) ändrade samma dag sex förklaringsceller (inledningen, `DailyLog`, `get_logs`, `days_since_start`, `log_today` och testcellen för egen inmatning), valideringscellen under CutProfile (ny kod och ny utskrift) och den sparade utskriften i cellen som kör `log_today`. Den tåligare CSV-inläsningen (N3) ändrade samma dag förklaringscellen om `import_logs_csv`, beskrivningen av testcellerna och testcellen med trasiga rader (ny sparad utskrift och ett andra fall med två filer som är fel som helhet). Att inte tappa loggar (N3) ändrade samma dag sju förklaringsceller (inledningen, `log_today`, `save_profile`, `load_profile`, beskrivningen av testcellen för filhanteringen, `run_menu` och Kör programmet), importcellen och två testceller: den som kör `log_today` (ny kod och ny utskrift) och den med felen i `load_profile` (fler fall och ny utskrift). |
| N8 | Menyn (frågor, profilskapande, loggning, menyval och avslut) och startpunkten `python main.py` täcks av automatiska tester som matar in svaren utan tangentbord. | Klart. Byggt och provkört 2026-10-09, genomgånget samma dag: 91 tester i `tests/test_main.py`, och 120 avsiktliga fel i `main.py` upptäcks av dem. Analysen och diagrammet ersätts av stubbar i testerna, så deras utskrifter testas inte härifrån. Brister i menyn som inte är rättade än är inte låsta med tester (statuslogg.md, Luckor). Ett 92:a test lades till 2026-10-10: en ny användare läser in exempelfilen och får en riktig analys, utan stubbar. Det är byggt och provkört men inte genomgånget. Datumkontrollen (D1) lade samma dag till 9 tester: datumet sparas med nollor, samma dag med och utan nolla blir en logg, ett datum som inte finns ger ett svenskt meddelande, och datumet kontrolleras före de andra frågorna. De är byggda och provkörda men inte genomgångna, så `tests/test_main.py` hade 101 tester. Att inte tappa loggar (N3) lade samma dag till 21 tester: `log_today` ger `True` eller `False`, profilen sparas efter varje ny logg men inte efter en rad som avvisats eller direkt efter CSV-inläsningen (nästa nya logg sparar det inlästa med), menyn varnar när den automatiska sparningen misslyckas, val 6 avslutar inte när sparningen misslyckas, menyn stannar vid fyra sorters profilfiler som inte går att läsa och vid en mapp med filens namn, och `python main.py` lämnar en trasig profilfil orörd. Ett test för Ctrl+C-meddelandet ändrades. Det ger 122 tester i `tests/test_main.py`, byggda och provkörda men inte genomgångna. Kontrollen av inmatningen lade samma dag till 127 tester: decimalkomma, `nan` och `inf`, gränser i `ask_number`, längd och ålder som frågas om direkt, `ask_name`, ja och nej på träningsfrågan, tomt midjemått och svenska meddelanden. Det ger 249 tester, byggda och provkörda men inte genomgångna. Kontrollen av namnet i profilfilen lade till 2: menyn stannar när filen hör till ett annat namn, och laddar profilen när bara versalerna skiljer. Det ger 251 tester. Texten vid kaloriförslaget (F22) lade till 5, så det är 256. |
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
