# CutTrack, teknisk plan

## Språkregel för kod
Klasser, attribut, metoder, funktioner och variabler namnges på engelska enligt PEP 8. All text som visas för användaren skrivs på svenska. Markdown-celler i notebooken och README skrivs på svenska. Commit-meddelanden på engelska.

Ingen dekorativ utskrift. Inga emojis, inga `print("=" * 60)`. Koden följer vanliga Python-mönster (klasser, `__init__`, `self`, try/except, filhantering) och håller sig till ren, läsbar kod framför smart kod.

## Byggordning och status
Version 1 byggdes i den här ordningen: datamodellen först (DailyLog, User, CutProfile), sedan beräkningar och regler, därefter filhantering och diagram, och sist menyn. Menyn låg först i notebooken och flyttades 2026-10-09 till main.py. Profilens fält lades in från start, även de som bara används av kaloriberäkningen, eftersom en ändrad datamodell gör redan sparade JSON-filer oläsbara. Själva beräkningsfunktionerna skrevs efter att grundflödet fungerade.

Version 1 innehåller:
- tre klasser med arv: DailyLog, User och CutProfile(User)
- JSON för profiler och CSV för loggar, med specifik felhantering per feltyp
- analys över valbar period (7, 14 eller 30 dagar) med väntetid, eget mål och säkerhetstak
- diagram för vikt, protein och steg
- textmeny med sex val och kaloriförslag på begäran
- kod uppdelad i models.py, analysis.py och main.py, med PEP 8-namngivning

Vad som återstår, och var koden avviker från visionen, står i kravspec.md och statuslogg.md.

## Klasser
### User (basklass)
Attribut: name, height_cm, age, sex, activity_level, start_weight, created_date (kontrolleras och skrivs som ÅÅÅÅ-MM-DD med nollor av `normalize_date`), logs (lista med DailyLog).
Metoder: add_log, get_logs(days, offset_days=0), average_weight(days, offset_days=0), weight_change(days), training_days(days).

### CutProfile(User), barnklass
Extra attribut: goal_weight, calorie_goal, protein_goal_per_kg, step_goal, target_rate_percent, training_goal_days (standard 3).
Extra metoder: current_weight, calculate_bmr, calculate_tdee, protein_goal, suggest_calorie_goal, days_since_start, waiting_message, check_goals.

Validerar i `__init__` att målvikten är lägre än startvikten och att takten ligger mellan 0 och 1,0 procent per vecka. Samma mönster som DailyLog, felet kastas där objektet skapas.

`super().__init__(...)` anropar Users `__init__` så att alla ärvda attribut sätts, inklusive den tomma logglistan. Klassraden `class CutProfile(User)` ger tillgång till förälderns metoder, men attributen kommer inte med automatiskt när barnklassen har en egen `__init__`.

### DailyLog
Attribut: date (alltid ÅÅÅÅ-MM-DD med nollor), weight, calories, protein, steps, trained (bool), waist (valfritt).
Validerar i `__init__` att date är ett riktigt datum, genom `normalize_date` som också skriver om det med nollor, och att weight och calories är rimliga tal, annars ValueError som fångas med try/except där loggen skapas. Datumet kontrolleras först.

## Hantering av valfria värden
`waist` kan vara `None` när användaren inte mätt. `None` betyder avsaknad av värde, inte noll. Skillnaden spelar roll: 0 cm är ett mätfel, `None` är en utebliven mätning.

Två regler:
- kontrollera alltid med `if log.waist is not None:` och aldrig med `if log.waist:`, eftersom 0 och None båda räknas som falska i ett vanligt if-test
- när snitt räknas, hoppa över tomma värden i loopen och räkna antalet träffar, kontrollera att antalet är större än noll innan du dividerar

Konstruktionen är enkel men lätt att göra fel på, därför ska de två reglerna ovan följas överallt där `waist` används.

## Metoder som returnerar None respektive noll
`average_weight` och `weight_change` returnerar `None` när underlaget är för tunt, inga loggar alls respektive färre än två. Skälet är samma som för `waist`: 0 skulle betyda att vikten inte ändrades, vilket är ett annat påstående än att det saknas underlag.

`training_days` returnerar däremot 0 när det inte finns några loggar, eftersom noll träningsdagar är ett korrekt svar och inte ett saknat värde.

## Regler och beräkningar

### Kaloriförslag
Mifflin-St Jeor för basalomsättning:
- man: BMR = 10 × vikt(kg) + 6,25 × längd(cm) - 5 × ålder + 5
- kvinna: BMR = 10 × vikt(kg) + 6,25 × längd(cm) - 5 × ålder - 161

BMR räknas på aktuell vikt, inte på startvikten. `current_weight()` hämtar senaste loggade vikten och faller tillbaka på start_weight när det inte finns några loggar än. Skälet: under en deff sjunker vikten, och därmed sjunker förbrukningen. Räknas BMR på startvikten överskattas behovet mer och mer ju längre deffen pågår.

TDEE = BMR × aktivitetsfaktor:
- 1,2 stillasittande
- 1,375 lätt aktiv
- 1,55 måttligt aktiv
- 1,725 mycket aktiv
- 1,9 extremt aktiv

Underskott räknas från önskad takt via tumregeln 7700 kcal per kilo kroppsfett.

VIKTIGT att dokumentera i README: 7700-regeln (3500 kcal per pound) är omdiskuterad. Den går tillbaka till en artikel från 1958 och antar ett konstant energiunderskott, vilket inte stämmer. I takt med att vikten går ner sjunker förbrukningen, så samma underskott ger mindre effekt över tid. Forskning visar att regeln överskattar faktisk viktnedgång. Programmet använder den som startpunkt. Avsikten är att det också ska säga att siffran bör justeras efter verkligt utfall efter två veckor, men den texten är inte byggd än (kravspec.md F22). Valet av en enkel modell med kända begränsningar står under Begränsningar i README.

Programmet vägrar räkna fram orimliga underskott: en önskad takt över 1,0 procent per vecka avvisas med `ValueError` redan när profilen skapas.

### Golv för kaloriförslaget
Ett tak på takten räcker inte. Formeln kan fortfarande räkna fram ett för lågt intag för någon som är kort eller lättviktig, eftersom underskottet dras från ett redan lågt TDEE. Därför behövs ett golv.

Två golv, och det högsta av dem gäller:

1. Fast golv: 1200 kcal för kvinnor, 1500 kcal för män. Kommer från de amerikanska riktlinjerna för behandling av övervikt och fetma hos vuxna (Jensen m.fl. 2013, AHA/ACC/TOS, se README), som rekommenderar 1200 till 1500 kcal för kvinnor och 1500 till 1800 för män, vanligen justerat efter kroppsvikt. CutTrack använder undre kanten. Riktlinjerna gäller personer med övervikt eller fetma men används här som golv för alla användare.
2. Rörligt golv: personens egen BMR. Att föreslå ett intag under vad kroppen gör av med i vila är svårt att motivera. Fördelen är att det skalar med personen automatiskt, vilket ett fast tal inte gör.

Exempel: är BMR 1450 för en kvinna blir golvet 1450, inte 1200.

Beteende när golvet slår i: programmet ska INTE tyst justera upp siffran. Det ska säga vad som hände, varför, och att takten därför blir långsammare än den önskade. Tyst justering får användaren att tro att den snabba takten fortfarande gäller.

### Takt på viktnedgången
Bedöms som procent av kroppsvikt per vecka, inte i kilo, så att samma gränser fungerar för olika kroppsstorlekar.

Två olika gränser med olika syften, inte ett gemensamt fast intervall:
- undre gränsen är personens eget target_rate_percent, satt vid profilskapande. Går det långsammare än det egna målet, flaggas det.
- övre gränsen är ett fast säkerhetstak på 1,0 procent per vecka, oavsett vad personen själv satt som mål. Risken för muskelförlust vid för snabb nedgång är en säkerhetsfråga, inte en preferens, och ska inte gå att ställa in bort.

Konsekvens: sätter någon sitt mål till 0,3 procent och når exakt det, räknas det som rätt takt, inte som för långsamt. Sätter någon sitt mål till 1,0 och landar på 1,3, flaggas det ändå, trots att de själva bad om en snabb takt.

- vikten ökar: underskottet räcker inte, flaggas alltid
- vikten är oförändrad (skillnaden under 0,05 kg per vecka): underskottet räcker inte, flaggas alltid, med en egen text
- under eget mål men inom säkerhetstaket: långsammare än önskat, flaggas
- vid eller över eget mål och inom säkerhetstaket: rätt takt
- över 1,0 procent: över säkerhetsgränsen, flaggas alltid, oavsett eget mål

### Proteinmål
Räknas mot målvikten, inte nuvarande vikt, och ligger därmed fast genom hela deffen. Utgångspunkt 1,9 gram per kilo målvikt. Ligger i metoden `protein_goal()` på CutProfile.

Skälet till målvikten: proteinbehovet finns för att skydda den muskelmassa som ska vara kvar när deffen är slut. Räknades det på nuvarande vikt skulle målet sjunka i takt med att vikten går ner, alltså precis tvärtemot syftet.

### Träningsfrekvens
Loggas som `trained`, en bool per dag, inte som antal minuter. Under en deff är det frekvensen som håller muskelmassan uppe, inte passets längd. Ett långt pass med mycket vila ger inte mer stimulans än ett kort och fokuserat. Frekvens går dessutom att bedöma mot en tydlig regel, antal dagar per vecka, medan minuter kräver ett godtyckligt tröskelvärde som skulle behöva motiveras.

Kostnaden av valet: programmet kan inte se om träningsvolymen kryper nedåt när energin sjunker under deffen. Ett valfritt minutfält som inte bedöms kan läggas till senare om det behovet uppstår.

Räknas med `training_days(days)` på User, som loopar över loggarna i fönstret och räknar antalet där `trained` är True.

### Trend och tidsfönster
Sjudagarssnittet räknas på de sju senaste kalenderdagarna, inte de sju senaste loggarna. Skälet är att trend handlar om tid. Sju loggar utspridda över en månad är inte ett veckosnitt.

Avsikten var att kräva minst fyra loggar inom fönstret innan ett snitt används. Så är det inte byggt: `average_weight` kräver minst en logg, och takten bedöms när båda perioderna har minst en vägning.

**Hur takten räknas.** Takten är skillnaden mellan snittet för den senaste perioden och snittet för perioden före, `(average_weight(days) - average_weight(days, days)) / days * 7`, alltså kilo per vecka, och procenttalet räknas på det senaste snittet. Ett snitt över `days` kalenderdagar ligger mitt i sin period, så de två snitten hör till tidpunkter som ligger `days` dagar isär. Därför delas skillnaden med `days` och multipliceras med sju, och samma nedgång per vecka ger samma kilotal för 7, 14 och 30 dagars period. Perioden före hämtas med `get_logs(days, offset_days)`, som hoppar över de `offset_days` senaste dagarna med samma kalenderdagsregel som alla andra urval. En enskild vägning är en av många i ett snitt: i exemplet i README flyttar 200 gram mer eller mindre på sista vägningen takten från 1,66 till 1,63 respektive 1,69 procent per vecka. Skillnader under 0,05 kg per vecka, det som avrundas till 0.0 kg i utskriften, räknas som oförändrad vikt och får en egen text, så att programmet aldrig skriver "minskar med 0.0 kg" eller "-0.0 procent". Saknas vägningar i någon av perioderna skrivs att det är för lite data.

**Vad metoden ersatte, och dess gränser.** Före F24 (byggt 2026-10-10) räknade `check_goals` takten från `weight_change(days)`, sista minus första loggade vikt i fönstret, med `raw_change / days * 7`. Det hade två svagheter. Första: en enskild vägning flyttade resultatet märkbart, i exemplet gav 200 gram på sista vägningen 1,11 respektive 1,52 procent per vecka i stället för 1,31. Andra: divisionen skedde på periodens längd i stället för på antalet dagar mellan första och sista vägningen, så takten blev ungefär 14 procent för låg på sjudagarsperioden. `weight_change` finns kvar men används inte längre av `check_goals`. Den nya metoden har egna gränser. Den kräver bara en vägning per period, så en period med få vägningar ger ett snitt som är nästan lika osäkert som en enskild vägning, och luckor i loggningen gör att avståndet mellan snitten avviker från `days`. Två perioder krävs för alla periodlängder, eftersom takten jämför två hela perioder, så takten bedöms först efter 14, 28 eller 60 dagar (kravspec.md F24 och statuslogg.md, Beslut).

Kräver `datetime` från standardbiblioteket för att göra om datumsträngar till datumobjekt som kan jämföras.

Urvalet ligger i `get_logs(days, offset_days=0)`, som anropas av `average_weight`, `weight_change` och `training_days`. Regeln finns därmed på ett enda ställe och behöver bara ändras där.

### Väntetexter
Dag 1 till 6 och dag 7 till 13 visar programmet en kort förklaring av varför det inte ger råd än, plus hur många dagar som återstår. Två till tre meningar, inte mer.

Tiderna gäller sjudagarsperioden. Med vald period `days` krävs en period (`days` dagar) för att visa ett snitt och två perioder (2 × `days` dagar) för att bedöma takten, så med 14 dagars period börjar full analys på dag 28 och med 30 dagar på dag 60. Två perioder krävs för att takten jämför den senaste perioden med perioden före.

Byggd som en egen metod, waiting_message, på CutProfile, inte inbakat i check_goals. Räknar dagar via days_since_start, som räknar från starten till senast loggade dagen, inte till dagens riktiga datum, av samma skäl som get_logs: har du inte loggat på några dagar ska analysen ändå utgå från din senaste aktiva period. Starten är created_date, eller den tidigaste loggen om den ligger före created_date, och båda dagarna räknas med. Det andra fallet uppstår när äldre data läses in i en ny profil, till exempel exempelfilen, eftersom create_profile ger en ny profil dagens datum. Före rättningen (2026-10-10) räknades alltid från created_date, och antalet dagar blev då negativt och väntetexten fel. created_date ändras inte, så profilen sparas som den skapades. Datumen görs om med strptime och jämförs som datum, som i get_logs. Alla loggars datum läses, så ett ogiltigt datum skulle ge ValueError i days_since_start, även under väntetiden. Sedan datumkontrollen (2026-10-10) kommer ett ogiltigt datum inte in i en logg eller ett startdatum, så felet kan bara uppstå om någon ändrat ett datum direkt i koden (kravspec.md D1, statuslogg.md Steg 1).

check_goals anropar waiting_message först. Finns det text att visa, skrivs den och funktionen avbryter innan någon analys görs. Först när perioden är full (dag 14 för sjudagarsperioden) returnerar waiting_message None och full analys körs.

### Prioritering av råd
Statusöversikt över alla områden plus en sak att fokusera på. Ordning: vikt, protein, träningsfrekvens, steg.

Byggd i check_goals som en flagga (focus_area) som bara sätts av det första området som inte når sitt mål, genom `if focus_area is None:` i varje gren. Vikten kollas först i koden, så ett viktproblem vinner alltid över ett proteinproblem oavsett vilken ordning de faktiskt hittas i. Är focus_area fortfarande None efter alla fyra kontrollerna, skrivs en sammanfattning byggd på att inget slog till, inte en generell fras.

Avsikten, enligt produktvision.md, är att protein, träning och steg kräver bara ett snitt och därför ska analyseras direkt, till skillnad från vikten som kräver väntetiden i waiting_message. Så är det inte byggt idag: check_goals avbryter efter väntetexten, så inget område analyseras förrän perioden är full (kravspec.md F15).

## Funktioner (utöver klassmetoder)
Byggda:
- normalize_date(date_text): kontrollerar att texten är ett riktigt datum i formatet ÅÅÅÅ-MM-DD och returnerar det skrivet med nollor, annars ValueError med svensk text. Anropas av `DailyLog`, `User` och `log_today` (models.py)
- make_safe_name(name): bygger den säkra delen av ett filnamn från användarnamnet, teckenvis i en loop
- make_filename(name): lägger till .json, filnamnet för användarens profil
- make_csv_filename(name): lägger till _loggar.csv, filnamnet för användarens CSV-export
- save_profile(profile): sparar profil och loggar till JSON
- load_profile(name): läser profil och loggar från JSON, try/except för tre feltyper
- export_logs_csv(profile, filename=None): loggarna som CSV, utan filnamn används make_csv_filename(profile.name)
- import_logs_csv(profile, filename=None): läser loggar från CSV och hoppar över trasiga rader, utan filnamn läses samma standardnamn som exporten skriver
- plot_weight(profile, days): viktdiagram med matplotlib
- plot_protein(profile, days) och plot_steps(profile, days): samma mönster för protein och steg
- ask_number(question, is_integer): frågar tills svaret går att tolka som tal (main.py)
- ask_period(): frågar efter analysperiod, 7, 14 eller 30 dagar (main.py)
- create_profile(name): frågar efter uppgifterna som behövs och skapar en ny CutProfile (main.py)
- show_welcome(): välkomsttext, riktlinjer och ansvarsfriskrivning (main.py)
- run_menu(): CLI-loop med input(), separat från beräkningslogiken (main.py)
- log_today(user): frågar efter dagens värden och lägger till en DailyLog (main.py)
- main(): startpunkten. Kör run_menu() och fångar KeyboardInterrupt och EOFError (Ctrl+C, och Ctrl+D eller stängd inmatning) med ett kort meddelande i stället för en Python-felutskrift. Anropas av `if __name__ == "__main__":` längst ned i main.py (main.py)

Inte byggd:
- search_food(name), Open Food Facts API, se avsnittet Externt API nedan.

calculate_trend är struken ur listan. average_weight och weight_change på User gör redan det jobbet, rullande medelvikt över kalenderdagar, via get_logs. En separat calculate_trend hade gjort samma sak två gånger.

## Felhantering
- load_profile, tre skilda except-block: json.JSONDecodeError (trasig fil), KeyError (saknat fält), ValueError (ogiltiga värden)
- import_logs_csv, try/except inne i loopen så en trasig rad hoppas över utan att stoppa resten av importen
- normalize_date, ValueError med svensk text för ett datum som inte finns, text som inte följer ÅÅÅÅ-MM-DD och värden som inte är text (`strptime` ger TypeError för dem, och det görs om till samma ValueError). `DailyLog` och `User` anropar den, så felet kastas där objektet skapas
- log_today och create_profile, ValueError vid ogiltig inmatning eller orimliga värden, även ett ogiltigt datum
- main, KeyboardInterrupt och EOFError. Inget annat fångas, så ett riktigt fel syns som Python-fel och döljs inte av ett vänligt meddelande
- save_profile och export_logs_csv, OSError vid skrivproblem
- API-anrop (om Open Food Facts byggs), nätverksfel och timeout

Fyra fall fångas inte ännu och ger ett Python-fel i stället för ett meddelande: en CSV-rad med för få kolumner, en CSV-fil som inte är UTF-8, en profilfil med fel struktur eller fel typer och en profilfil som inte går att läsa som fil (kravspec.md N3, statuslogg.md Luckor och Steg 1). Det femte fallet, ett ogiltigt datum i en CSV-fil, rättades 2026-10-10: `DailyLog` avvisar datumet, så `import_logs_csv` hoppar över raden och `load_profile` säger att filen innehåller ogiltiga värden.

I menyn finns tre brister till som inte kraschar men tappar data: inget sparas före menyval 6, så Ctrl+C eller en stängd terminal tappar allt sedan start, menyval 6 avslutar även när `save_profile` eller `export_logs_csv` misslyckades, eftersom `run_menu` inte läser deras returvärde, och en profilfil som inte går att läsa ersätts av en ny tom profil vid menyval 6, eftersom `load_profile` ger `None` både för en saknad och för en skadad fil och `run_menu` då skapar en ny profil med samma filnamn (provat 2026-10-10, statuslogg.md, Luckor och Steg 1).

## Tester
pytest, installerat som utvecklingsberoende med `python -m pip install -r requirements-dev.txt`. Programmet kräver det inte för att köras. Testerna körs från rotmappen med `python -m pytest`. `pytest.ini` anger att `models`, `analysis` och `main` hittas från rotmappen (`pythonpath = .`) och att testerna ligger i `tests/`.

Fyra filer, och vad var och en täcker:
- `tests/test_models.py`: validering av värden (F2, F7) och datum (D1), loggfönstret i kalenderdagar och förskjutningen `offset_days` (D3, F24), snitt, viktförändring och träningsdagar, kaloriförslag och golv (F9, F10), väntetid och dagar sedan start (F14) och vilken gren `check_goals` väljer (F13, F17)
- `tests/test_analysis.py`: filnamn (F4, F8), profilfiler (F3), CSV-export och inläsning, inklusive trasiga rader (F8) och rader och profilfiler med ogiltiga datum (D1)
- `tests/test_readme_example.py`: låser det `check_goals` skriver ut i README-exemplet, kontrollerar att README visar samma rader, att exempelfilen ger samma analys i en profil som skapats efter loggarna (F14), och innehåller testerna av hur vikttakten räknas (F24)
- `tests/test_main.py`: textmenyn i `main.py` (F1, F2, F5, F6, F7, F21, F22, D1, D2, N5): frågorna och deras omfrågning vid fel svar, profilskapandet, loggningen, de sex menyvalen, `main()` och att `python main.py` startar och avslutas, samt en ny användare som läser in exempelfilen och får en riktig analys (F14)

Så är testerna skrivna:
- Varje test i `test_analysis.py` körs i en egen tom mapp, med en fixtur (`autouse=True`) som byter arbetsmapp till `tmp_path`. Funktionerna skriver filer i den aktuella mappen, och utan fixturen hade testerna skrivit profiler och CSV-filer i repot.
- Förväntade värden räknas ut för hand i kommentarerna och kopieras inte från programmets utskrift, så att testet kontrollerar koden i stället för att upprepa den. Undantaget är README-exemplet, som är programmets egen utskrift. Den är kontrollräknad utanför koden, och samma rader måste stå i README.
- Allt som beror på hur takten räknas (F24) ligger i `test_readme_example.py`. De övriga testerna kontrollerar vilken gren som väljs, med data som ligger långt från gränserna. Ett test i `test_models.py` fick ändå ny data när F24 byggdes, eftersom det antog fel: en enda sänkt dag i en annars platt vecka är brus för en metod som jämför snitt, och räknas med rätta som oförändrad vikt (statuslogg.md, Beslut).
- Ett test som låser dagens beteende (på engelska characterization test) beskriver vad koden gör, inte vad den borde göra. Det användes bara för F24: testerna låste den gamla takträkningen tills den byttes 2026-10-10, och ersattes då av tester av den nya. Övriga kända fel får sina tester först när de rättas (statuslogg.md, Luckor och Beslut). För menyn betyder det att `nan`, negativa steg, `ja` som träningssvar, decimalkomma och tomt namn inte finns i `test_main.py`.
- Menyn läser med `input()`, och `input()` läser från `sys.stdin`. `test_main.py` byter `sys.stdin` mot en `io.StringIO` med färdiga svar (hjälpfunktionen `type_answers`), så att testet bestämmer vad användaren skriver. När svaren tar slut kastar `input()` `EOFError`, som vid Ctrl+D, så ett test som frågar efter mer än det gett stoppas i stället för att hänga. Svaren syns inte i utskriften, så en fråga och nästa utskrift hamnar på samma rad och testerna kontrollerar med `text in output`, aldrig rad för rad.
- Analysen (`check_goals`) och diagrammet (`plot_weight`) ersätts med stubbar där menyn anropar dem (`monkeypatch.setattr`). Menyn ska bara skicka vidare rätt period, ingen figur får öppnas under en testkörning, och analysens regler testas på ett ställe, i `test_models.py` och `test_readme_example.py`. Undantaget är testet av exempelfilen, som kör den riktiga analysen för att visa att en ny användare får en analys och inte en väntetext. Det får sitt startdatum av `create_profile` (dagens datum), så det är beroende av datorns klocka. Testerna i `test_models.py` och `test_readme_example.py` sätter startdatumet själva och är det som bevisar rättningen oavsett datum.
- Tre tester kör Python som eget program med `subprocess.run`, eftersom `if __name__ == "__main__":` aldrig körs när ett test importerar filen. Två startar `python main.py` och provar att programmet startar och avslutas och att det inte ger någon Python-felutskrift när inmatningen stängs. Det tredje kör `import main` med tom inmatning och provar att menyn inte startar.

Inte täckt: diagramfunktionerna (`plot_weight`, `plot_protein`, `plot_steps`), vad analysen skriver ut när den anropas via menyn (utom att ett test kontrollerar att en ny användare med exempelfilen får en analys och inte väntetexten) och de fyra fallen under Felhantering.

Hur testerna kontrollerades 2026-10-08: koden ändrades avsiktligt på 177 ställen, en ändring i taget, och testerna kördes mot varje. 173 ändringar gav ett misslyckat test, de fyra som inte gjorde det står i statuslogg.md. Täckning enligt coverage.py: `analysis.py` utom diagrammen täcks helt och `models.py` till 98 procent. Kontrollen gjordes för hand en gång och finns inte som skript i repot.

Menytesterna kontrollerades 2026-10-09 på samma sätt, med `main.py` som mål. Första omgången gav 113 ändringar: 106 upptäcktes, fyra inte (en extra giltig analysperiod, aktivitetsvalet utan krav på heltal, och kalorier och protein lästes som heltal) och tre avbröt testkörningen. Testerna skärptes, och andra omgången gav 120 ändringar som alla upptäcktes. Täckning: `main.py` 99 procent, och raden som saknas är `main()` i skyddet, som bara körs av de två testerna som startar `python main.py` i en egen process. Flytten från notebooken kontrollerades dessutom genom att jämföra syntaxträd och källtext för de sex funktionerna med notebookens celler: de är identiska. Inte heller den här kontrollen finns som skript i repot.

Datumkontrollen kontrollerades 2026-10-10 på samma sätt, med `models.py`, `main.py` och `analysis.py` som mål: 19 avsiktliga ändringar, en i taget. 17 upptäcktes av testerna. De två som inte gjorde det ger samma resultat med avsikt: att `normalize_date` returnerar `strftime("%Y-%m-%d")` i stället för `isoformat()` (samma text för fyrsiffriga år, bara år före 1000 skiljer sig åt, och på Linux bara i Python 3.11 till 3.13), och att `log_today` kastar bort det omskrivna datumet (`DailyLog` skriver om det en gång till). Sviten, 316 tester, gick igenom på Python 3.11, 3.12, 3.13 och 3.14 med varningar behandlade som fel. Täckning: `models.py` 98 procent och `main.py` 99 procent, med samma luckor som före ändringen. Inte heller den här kontrollen finns som skript i repot.

## Datumformat och dubbletter

### Format
Datum skrivs alltid som ÅÅÅÅ-MM-DD med nollor, till exempel 2026-09-15. Sorteras rätt som text och läses direkt av datetime.strptime med formatsträngen "%Y-%m-%d". Funktionen `normalize_date` i models.py ser till att det stämmer. Den läser texten med `strptime`, som kastar ValueError för text som inte följer formatet och för ett datum som inte finns (2026-02-30), och skriver sedan om datumet med `isoformat()`. Ett värde som inte är text alls, till exempel `None` från en JSON-fil, ger TypeError i `strptime`, och det görs om till samma ValueError, så den som anropar fångar bara en feltyp.

`strptime` godtar månad och dag utan inledande nolla (`2026-10-8`). `normalize_date` skriver om ett sådant datum (`2026-10-08`) i stället för att avvisa det, eftersom det bara kan betyda en dag och det inte finns något att gissa (statuslogg.md, Beslut). `DailyLog.__init__` och `User.__init__` anropar funktionen, så ett objekt kan inte skapas med ett ogiltigt datum, oavsett om det kommer från menyn, en CSV-fil eller en JSON-fil. `log_today` anropar den också, först av allt, så att ett fel datum stoppar innan användaren har skrivit in resten. `isoformat()` valdes framför `strftime("%Y-%m-%d")`, eftersom `strftime` skriver år före 1000 olika på olika Python-versioner (år 26 blir `26` på Python 3.11 till 3.13 och `0026` på 3.14, provat på Linux 2026-10-10) medan `isoformat()` alltid ger fyra siffror.

Att formatet sorteras rätt som text används i `weight_change` och `current_weight`, som hittar tidigaste eller senaste logg genom att jämföra datumsträngarna direkt i en loop, utan att sortera listan. Det är säkert eftersom alla datum skrivs med nollor av `normalize_date`. `get_logs` och `days_since_start` räknar i stället med `datetime`.

Funktionen kontrollerar att datumet finns och har rätt format, inte att det är rimligt. Ett datum i framtiden eller med fel år godtas, och ett datum med mellanslag före eller efter avvisas (kravspec.md D1, statuslogg.md, Luckor).

### Dubbletter samma dag
Den nya loggen ersätter den gamla. Två poster för samma datum gör alla snitt fel eftersom dagen räknas dubbelt. Eftersom datumen skrivs med nollor räknas `2026-10-8` och `2026-10-08` som samma dag.

Innan en logg läggs till: loopa igenom befintliga loggar och kolla om datumet redan finns. Finns det, byt ut posten och tala om för användaren att dagens logg uppdaterades. Annars lägg till som ny. En for-loop och en if-sats.

### Filnamn från användarnamn
Bygg aldrig filnamnet direkt från det användaren skriver in. Gör om till små bokstäver och behåll bara bokstäver och siffror, ta bort resten. "Niklas E" blir niklase.json. Skriver någon in ett snedstreck försvinner det.

Bygg strängen med en loop, tecken för tecken, som bara tar med tillåtna tecken. Det är enklare att läsa och granska än ett reguljärt uttryck.

Samma säkra namn ligger bakom alla användarens filer: profilen blir niklase.json och CSV-exporten niklase_loggar.csv (make_safe_name, make_filename, make_csv_filename). Begränsning: två namn som blir lika efter rensningen, till exempel "Anna Berg" och "Anna-Berg", delar profilfil och exportfil.

## Datalagring
En JSON-fil per användare med profil och loggar (<namn>.json). Vid avslut exporteras loggarna även som CSV (<namn>_loggar.csv), som går att öppna i Excel. CSV-kolumnerna namnges på engelska så de matchar attributnamnen.

Profilen innehåller längd, ålder, kön och vikt, vilket är personuppgifter. Profilfiler (`*.json`) och egna CSV-filer ignoreras därför av git, och programmet skickar ingen data någonstans, allt ligger lokalt. Det enda undantaget i .gitignore är `data/exempel_loggar.csv`, simulerad exempeldata som notebookens exempelcell skriver. Undantaget står längst ned i filen, eftersom den sista matchande raden i .gitignore avgör. Filen checkas in med programmets egna radslut (CRLF) genom raden `data/exempel_loggar.csv -text` i .gitattributes. Utan den byter git radslut vid `git add` och visar filen som ändrad varje gång notebooken körs om (kravspec.md D4).

## Externt API: Open Food Facts
Gratis, ingen API-nyckel, base URL world.openfoodfacts.org. Slår upp protein och kalorier per 100 gram.

Fallgropar att hantera med try/except:
- API:t kan svara 200 OK men ha status 0 i svaret, vilket betyder att livsmedlet inte hittades. Det räcker inte att kolla statuskoden.
- nätverksfel och timeout, requests.exceptions
- saknade fält för vissa produkter, använd .get() med default

Tilläggsfunktion, inte byggd. Uppgifterna ovan kontrolleras mot aktuell dokumentation innan den byggs.

## Utvecklingsmiljö
macOS med VS Code och Python 3.14 i `.venv`. Terminalen är PowerShell (pwsh), så kommandon som ska klistras in skrivs så att de fungerar där: miljön aktiveras med `.venv/bin/Activate.ps1` och inte med `source`, och en körbar fil i en annan miljö anropas med `&` före sökvägen. Git-kommandona fungerar likadant, men ett commit-meddelande i citattecken får inte innehålla `$` eller backtick, eftersom PowerShell tolkar dem. Upptäckt 2026-10-09 när installationsprovet kördes.

## Bibliotek
Standard, faktiskt använda: json (spara/läsa profil), csv (export/import loggar), datetime (datum och kalenderdagar), os (kolla om fil finns).
Externt, faktiskt använt: matplotlib (diagram för vikt, protein och steg). Standardbiblioteket kan inte rita diagram. Version 3.11.2, släppt 2026-09-11, kräver Python 3.11 eller senare och har Python 3.11 till 3.14 bland klassificeringarna på PyPI (kontrollerat 2026-10-09). Underhållet är aktivt: 3.10.9 kom 2026-04-24, 3.11.0 2026-06-12, 3.11.1 2026-07-18 och 3.11.2 2026-09-11.
Externt, bara för utveckling: pytest (testerna). Version 9.1.1, släppt 2026-06-19, MIT-licens, kräver Python 3.10 eller senare och har Python 3.10 till 3.15 bland klassificeringarna på PyPI (kontrollerat 2026-10-09, fortfarande senaste versionen). Underhållet är aktivt: 9.0.3 kom 2026-04-07, 9.1.0 2026-06-13 och 9.1.1 2026-06-19. Behövs för `tmp_path`, `monkeypatch`, `capsys`, `pytest.raises` och `pytest.approx`, som testerna bygger på.
Beroendefiler i rotmappen: `requirements.txt` (körning) har en rad, `matplotlib>=3.11,<4`. `requirements-dev.txt` (testerna) tar med den filen med `-r requirements.txt` och lägger till `pytest>=9.1,<10`. Den lägsta versionen är första utgåvan i den serie som programmet byggts med, och den är provad (matplotlib 3.11.0 och pytest 9.1.0 på Python 3.11 och 3.14). Den högsta utesluter nästa huvudversion, som får ändra hur biblioteket fungerar. Exakta versioner (`==`) valdes bort eftersom filen då måste ändras vid varje utgåva. En låsfil med alla underberoenden (numpy, pillow med flera) är nästa steg om det visar sig behövas. Lägsta Python är 3.11, eftersom matplotlib 3.11 kräver det. Filerna har inga kommentarer och bara ASCII-tecken, eftersom pip läser dem med systemets teckenkodning: med pip 24.0 och en ASCII-lokal utan UTF-8-läge kraschade installationen med `UnicodeDecodeError` på å, ä och ö i en kommentar (provat 2026-10-09).
Inte i beroendefilerna: Jupyter-kärnan (`ipykernel`), som bara notebooken behöver. Den som kör notebooken installerar den själv.
Licenser: matplotlib har en PSF-licens och pytest är MIT enligt PyPI (kontrollerat 2026-10-09). Inget av dem ligger i repot, de installeras med pip, och de begränsar inte valet av licens för CutTrack, som är MIT (se Filstruktur).
Inte använt: statistics (all snittberäkning görs med egna loopar, inte statistics.mean), requests (Open Food Facts inte byggd).

## Programflöde
1. `python main.py` kör main(), som anropar run_menu() och fångar Ctrl+C och Ctrl+D.
2. show_welcome() visar välkomsttext, riktlinjer och ansvarsfriskrivning.
3. Fråga efter användarnamn. load_profile(name) laddar profilen om den finns. Finns den inte, eller går den inte att läsa (load_profile ger None i båda fallen), frågar create_profile(name) efter längd, ålder, kön, aktivitetsnivå, startvikt, målvikt och önskad takt, och visar ett första kaloriförslag och proteinmål direkt.
4. Meny i run_menu(), sex val: logga dagens data, visa analys, visa viktdiagram, visa kaloriförslag, läs in loggar från CSV, spara och avsluta.
5. Vid avslut (val 6) sparar save_profile profilen som JSON och export_logs_csv exporterar loggarna som CSV till användarens eget filnamn (<namn>_loggar.csv), innan programmet avslutas. Det är det enda tillfället då något sparas.

Uppslag av livsmedel (search_food) finns inte med i menyn, eftersom Open Food Facts-integrationen inte byggts, se Externt API nedan.

## Filstruktur
Håll input() och print() i egna funktioner, separat från klasserna och beräkningslogiken, så att CLI kan bytas mot en app senare utan att röra kärnlogiken.

Koden är uppdelad i fyra filer, i samma mapp:
- `models.py`: DailyLog, User, CutProfile, normalize_date
- `analysis.py`: make_safe_name, make_filename, make_csv_filename, save_profile, load_profile, export_logs_csv, import_logs_csv, plot_weight, plot_protein, plot_steps. Importerar DailyLog och CutProfile från models.py.
- `main.py`: show_welcome, ask_number, ask_period, create_profile, log_today, run_menu (UI-lagret) och main, startpunkten. Importerar från models.py och analysis.py. Startas med `python main.py`.
- `cuttrack.ipynb`: importerar från de tre andra filerna. Innehåller förklaringar samt alla test- och democeller, men kör inte menyn.

Exempeldata ligger i mappen `data/`: `exempel_loggar.csv` är simulerad data för 20 dagar och den enda CSV-filen som checkas in. Notebooken skriver den.

Beroendena ligger i `requirements.txt` (körning) och `requirements-dev.txt` (testerna) i rotmappen, se Bibliotek.

Licensen ligger i `LICENSE` i rotmappen: MIT, `Copyright (c) 2026 Niklas Ekeskär`, standardtexten från choosealicense.com. GitHub känner igen en licens genom att jämföra filen mot kända licenstexter, så texten ändras inte annat än i copyright-raden. README har ett avsnitt Licens, och skälen till valet står i statuslogg.md under Beslut.

Testerna ligger i mappen `tests/`, fyra filer, och `pytest.ini` i rotmappen anger hur de hittar `models.py`, `analysis.py` och `main.py` (se Tester).

Notebooken måste ligga i samma mapp som models.py, analysis.py och main.py för att importen ska fungera. Ändras något i en av .py-filerna medan notebooken är öppen måste kerneln startas om (Restart) innan ändringen syns, Python läser bara in en modul en gång per körning. Det är den praktiska konsekvensen av uppdelningen.

**Menyn ligger i main.py.** Klasser och funktioner finns bara i models.py, analysis.py och main.py, och notebooken importerar dem och förklarar dem i markdown. Programmet startas med `python main.py`. Notebooken kör inte menyn, eftersom allt en cell skriver ut sparas i `cuttrack.ipynb` och repot är publikt (kravspec.md D4). Raden `if __name__ == "__main__":` längst ned i main.py gör att menyn bara startar när filen körs som program och inte när notebooken importerar den: Python sätter `__name__` till `"__main__"` vid `python main.py` och till `"main"` vid `import main`.

Profil- och CSV-filerna skrivs i den mapp programmet startas från, inte i mappen där main.py ligger (analysis.py använder relativa filnamn). Startas programmet från rotmappen hamnar filerna där och ignoreras av git. Startas det från en annan mapp skapar det nya, tomma profiler där.

## Källor
Alla källor står med direktlänkar i README under Källor och antaganden. Vad varje källa ligger bakom:
- Mifflin-St Jeor 1990: formeln och aktivitetsfaktorerna
- 7700 kcal per kilo: ursprung 1958 (Wishnofsky), kritiken mot den i Hall m.fl. 2011
- Takt: Garthe m.fl. 2011, som jämförde 0,7 och 1,4 procent per vecka. Säkerhetstaket på 1,0 procent är en marginal, inte studiens resultat
- Protein: Morton m.fl. 2018 (nyttan planar ut runt 1,6 g/kg kroppsvikt, praktisk övre gräns kring 2,2), samt Helms m.fl. 2014 som räknar per kilo fettfri massa för tävlande
- Kalorigolv: Jensen m.fl. 2013 (AHA/ACC/TOS), 1200 till 1500 kcal för kvinnor och 1500 till 1800 för män, vanligen justerat efter kroppsvikt. CutTrack använder undre kanten
