# CutTrack, teknisk plan

## Språkregel för kod
Klasser, attribut, metoder, funktioner och variabler namnges på engelska enligt PEP 8. All text som visas för användaren skrivs på svenska. Markdown-celler i notebooken och README skrivs på svenska. Commit-meddelanden på engelska.

Ingen dekorativ utskrift. Inga emojis, inga `print("=" * 60)`. Kursnotebooksens struktur följs (klasser, `__init__`, `self`, try/except, filhantering), men inte deras utsmyckning.

## Byggordning
Bygg G-versionen klar, testad och förklarbar först. Lägg inte till VG-delarna förrän G fungerar utan kritiska fel.

Profilens fält läggs in från start, även de som bara används av kaloriberäkningen. Skälet är att en ändrad datamodell gör redan sparade JSON-filer oläsbara. Själva beräkningsfunktionen skrivs däremot efter att grundflödet fungerar.

## G-version, det som ska fungera först
- läsa in loggar från CSV
- snitt: vikt, kalorier, protein, steg, antal träningspass
- rullande sjudagarssnitt och bedömning av takt
- regelbaserade rekommendationer som text
- viktdiagram
- minst en klass och en barnklass med arv
- körs utan kritiska fel
- varje rad går att förklara muntligt
- allt kan ligga samlat i notebooken i det här steget

## VG-utbyggnad
- dela upp koden i models.py och analysis.py som importeras in i notebooken
- konsekvent PEP 8-namngivning
- fler diagram: protein och steg, inte bara vikt
- specifik felhantering per feltyp istället för generella try/except
- val av analysperiod, 7, 14 eller 30 dagar
- djupare reflektion i README

## Klasser
### User (basklass)
Attribut: name, height_cm, age, sex, activity_level, start_weight, created_date, logs (lista med DailyLog).
Metoder: add_log, get_logs, average_weight(days), weight_change(days).

### CutProfile(User), barnklass
Extra attribut: goal_weight, calorie_goal, protein_goal_per_kg, step_goal, target_rate_percent.
Extra metoder: calculate_bmr, calculate_tdee, suggest_calorie_goal, check_goals.

### DailyLog
Attribut: date, weight, calories, protein, steps, training_minutes, waist (valfritt).
Validerar i `__init__` att weight och calories är rimliga tal, annars ValueError som fångas med try/except där loggen skapas.

## Hantering av valfria värden
`waist` kan vara `None` när användaren inte mätt. `None` betyder avsaknad av värde, inte noll. Skillnaden spelar roll: 0 cm är ett mätfel, `None` är en utebliven mätning.

Två regler:
- kontrollera alltid med `if log.waist is not None:` och aldrig med `if log.waist:`, eftersom 0 och None båda räknas som falska i ett vanligt if-test
- när snitt räknas, hoppa över tomma värden i loopen och räkna antalet träffar, kontrollera att antalet är större än noll innan du dividerar

Det här är den enda konstruktionen i projektet som ligger över ren nybörjarnivå. Den ska kunna förklaras muntligt med orden ovan.

## Regler och beräkningar

### Kaloriförslag
Mifflin-St Jeor för basalomsättning:
- man: BMR = 10 × vikt(kg) + 6,25 × längd(cm) − 5 × ålder + 5
- kvinna: BMR = 10 × vikt(kg) + 6,25 × längd(cm) − 5 × ålder − 161

TDEE = BMR × aktivitetsfaktor:
- 1,2 stillasittande
- 1,375 lätt aktiv
- 1,55 måttligt aktiv
- 1,725 mycket aktiv
- 1,9 extremt aktiv

Underskott räknas från önskad takt via tumregeln 7700 kcal per kilo kroppsfett.

VIKTIGT att kunna förklara muntligt och att skriva om i README: 7700-regeln (3500 kcal per pound) är omdiskuterad. Den går tillbaka till en artikel från 1958 och antar ett konstant energiunderskott, vilket inte stämmer. I takt med att vikten går ner sjunker förbrukningen, så samma underskott ger mindre effekt över tid. Forskning visar att regeln överskattar faktisk viktnedgång. Programmet använder den som startpunkt och säger uttryckligen att siffran ska justeras efter verkligt utfall efter två veckor. Det är ett medvetet val av en enkel modell med kända begränsningar, vilket hör hemma i README:s reflektion (mål 8).

Programmet ska vägra räkna fram orimliga underskott. Om användaren begär en takt över 1 procent per vecka ska funktionen returnera både en varning och den takt som är rimlig utifrån deras vikt.

### Takt på viktnedgången
Bedöms som procent av kroppsvikt per vecka, inte i kilo, så att samma gränser fungerar för olika kroppsstorlekar.
- vikten ökar: underskottet räcker inte
- under 0,5 procent: går för långsamt
- 0,5 till 1,0 procent: rätt takt
- över 1,0 procent: för snabbt, risk för muskelförlust

### Proteinmål
Räknas mot målvikten, inte nuvarande vikt, och ligger därmed fast genom hela deffen. Utgångspunkt 1,9 gram per kilo målvikt.

### Trend och tidsfönster
Sjudagarssnittet räknas på de sju senaste kalenderdagarna, inte de sju senaste loggarna. Skälet är att trend handlar om tid. Sju loggar utspridda över en månad är inte ett veckosnitt.

Minst fyra loggar inom fönstret krävs för att snittet ska användas. Färre än så säger programmet att underlaget är för tunt.

Kräver `datetime` från standardbiblioteket för att göra om datumsträngar till datumobjekt som kan jämföras.

### Väntetexter
Dag 1 till 6 och dag 7 till 13 visar programmet en kort förklaring av varför det inte ger råd än, plus hur många dagar som återstår. Två till tre meningar, inte mer. Läggs i en egen funktion, inte inbakat i check_goals.

### Prioritering av råd
Statusöversikt över alla områden plus en sak att fokusera på. Ordning: vikt, protein, träningsfrekvens, steg.

## Funktioner (utöver klassmetoder)
- load_profile(filename): läser profil och loggar från JSON, try/except
- save_profile(profile, filename): sparar till JSON
- export_logs_csv(profile, filename): loggarna som CSV, detta är datafilen som lämnas in
- calculate_trend(logs, days=7): rullande medelvikt över kalenderdagar
- plot_weight(logs): matplotlib
- search_food(name): Open Food Facts API, tilläggsfunktion
- run_menu(): CLI-loop med input(), separat från beräkningslogiken

Kravet på 3 till 5 egna funktioner räknas på funktioner definierade med def utanför klasserna. Metoder inuti en klass räknas till OOP-kravet.

## Datalagring
En JSON-fil per användare med profil och loggar. Vid inlämning exporteras loggarna även som CSV. CSV-kolumnerna namnges på engelska så de matchar attributnamnen.

Profilen innehåller längd, ålder och kön, vilket gör programmet till en behandlare av personuppgifter. Kursens GDPR-regel är relevant: skicka aldrig riktig persondata till AI-verktyg, och överväg att hålla den egna profilfilen utanför GitHub.

## Externt API: Open Food Facts
Gratis, ingen API-nyckel, base URL world.openfoodfacts.org. Slår upp protein och kalorier per 100 gram.

Fallgropar att hantera med try/except:
- API:t kan svara 200 OK men ha status 0 i svaret, vilket betyder att livsmedlet inte hittades. Det räcker inte att kolla statuskoden.
- nätverksfel och timeout, requests.exceptions
- saknade fält för vissa produkter, använd .get() med default

Tilläggsfunktion. Prioriteras bort om tiden inte räcker. Kravet på extern data uppfylls då genom CSV-inläsning istället.

## Bibliotek
Standard: json, csv, datetime, os, statistics.
Externt: requests (API), matplotlib (diagram).

## Programflöde
1. Fråga efter användarnamn. Finns profilen, ladda den. Annars skapa ny CutProfile och fråga efter längd, ålder, kön, aktivitetsnivå, startvikt, målvikt och önskad takt.
2. Visa ansvarsfriskrivning vid skapande av ny profil.
3. Meny: logga dagens data, slå upp livsmedel, visa analys, visa diagram, avsluta.
4. Vid avslut, spara profilen och exportera CSV.

## Var varje obligatoriskt moment används

### Variabler och datatyper
- int: steps, training_minutes, age
- float: weight, calories, protein, waist
- str: name, date, sex
- bool: om ett mål är uppnått
- lista: logs
- dict: JSON-datan vid läsning och sparning

### If-satser
- check_goals, jämför värden mot mål
- run_menu, vilket menyval användaren skrev
- load_profile, om filen finns
- kontroll av `waist is not None`
- kontroll av hur många loggar som finns innan analys

Exempel:

    if average_protein >= protein_goal:
        recommendation = "Proteinmålet nås."
    else:
        recommendation = "Öka proteinet."

### Loopar
- for över logs för att räkna snitt
- for när loggarna skrivs till CSV
- for när JSON-data görs om till DailyLog-objekt
- while i run_menu

Exempel:

    for log in logs:
        total_weight = total_weight + log.weight

och

    while True:
        choice = input("Välj: ")
        if choice == "5":
            break

### Funktioner
load_profile, save_profile, export_logs_csv, calculate_trend, plot_weight.

### Felhantering
- filinläsning, filen saknas eller är trasig JSON
- DailyLog-validering, ValueError
- API-anrop, nätverksfel och timeout
- division med noll när inga loggar finns i fönstret

### Datahantering
JSON vid spara och läsa profil, CSV vid export.

### Klasser och arv
User är basklass, CutProfile ärver och lägger till mål och beräkningar. DailyLog är egen klass.

### Bibliotek
Standard: json, csv, datetime, statistics. Externt: matplotlib, requests.

### API eller extern data
Open Food Facts, alternativt CSV-inläsning.

## Filstruktur
Håll input() och print() i egna funktioner, separat från klasserna och beräkningslogiken, så att CLI kan bytas mot en app senare utan att röra kärnlogiken.

## Källor att ange i README
- Mifflin-St Jeor: formeln och aktivitetsfaktorerna
- 7700 kcal per kilo: ursprung 1958, samt kritiken mot den (Hall & Chow, Thomas m.fl. 2013)
- Takt 0,5 till 1,0 procent per vecka: Garthe m.fl. 2011, samt översiktsartikel om fettförlust hos styrketränande
- Protein: Helms m.fl. 2014 för 2,3 till 3,1 g per kilo fettfri massa, samt nyare metaanalys som anger 1,9 g per kilo kroppsvikt för icke-tävlande

Slå upp och läs källorna själv innan de går in i koden. Du kan få frågan muntligt om vilken som helst av dem.
