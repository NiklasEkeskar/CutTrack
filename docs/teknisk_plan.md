# CutTrack, teknisk plan

## Språkregel för kod
Klasser, attribut, metoder, funktioner och variabler namnges på engelska enligt PEP 8. All text som visas för användaren (menyer, felmeddelanden, rekommendationer) skrivs på svenska. Markdown-celler i notebooken och README skrivs på svenska.

## Byggordning
Bygg G-versionen klar, testad och förklarbar först. Lägg inte till VG-delarna förrän G fungerar utan kritiska fel. Se avsnitten "G-version" och "VG-utbyggnad" nedan för vad som hör till respektive steg.

## G-version, det som ska fungera först
- läsa in loggar från en CSV-fil
- enkla beräkningar: medelvikt, viktförändring, medelkalorier, medelprotein, medelsteg, antal träningspass
- regelbaserade rekommendationer som text
- ett tydligt viktdiagram
- minst en klass och en barnklass med arv
- programmet ska köras utan kritiska fel
- varje rad ska gå att förklara muntligt
- allt kan ligga samlat i notebooken i det här steget

## VG-utbyggnad, läggs till efter att G fungerar
- dela upp koden i egna filer, till exempel models.py för klasserna och analysis.py för beräkningarna, som importeras in i notebooken
- konsekvent namngivning enligt PEP 8
- fler diagram: vikt, protein och steg, inte bara vikt
- mer specifik felhantering, egna felmeddelanden per feltyp istället för generella try/except
- ett val där användaren väljer analysperiod, till exempel 7, 14 eller 30 dagar
- djupare reflektion i README

## Klasser
### User (basklass)
Attribut: name, start_weight, created_date, logs (lista med DailyLog-objekt).
Metoder: add_log, get_logs, average_weight(days), weight_change(days).

### CutProfile(User), barnklass
Extra attribut: goal_weight, calorie_goal, protein_goal_per_kg, step_goal.
Extra metod: check_goals, som jämför loggarna mot målen och returnerar en textrekommendation på svenska enligt regler, till exempel "Vikten minskar, proteinmålet nås, fortsätt som nu" eller "Vikten står still, se över kaloriintaget".

### DailyLog
Ett objekt per dag: date, weight, calories, protein, steps, training_minutes.
Validerar i sin init att weight och calories är rimliga tal, annars ValueError, som fångas med try/except där loggen skapas.

## Funktioner (utöver klassmetoder)
- load_profile(filename): läser profil och loggar från JSON, try/except för filen saknas eller är korrupt
- save_profile(profile, filename): sparar till JSON
- export_logs_csv(profile, filename): sparar loggarna som CSV, detta är datafilen som lämnas in
- calculate_trend(logs, days=7): rullande medelvikt för att jämna ut dagliga svängningar
- plot_weight(logs): matplotlib, viktkurva över tid
- search_food(name): anropar Open Food Facts API, se avsnitt nedan
- run_menu(): CLI-loop med input(), separat från beräkningslogiken

Kravet på 3 till 5 egna funktioner räknas på funktioner definierade med def utanför klasserna. Metoder inuti en klass räknas till OOP-kravet, inte till funktionskravet.

## Datalagring
En JSON-fil per användare, med profil och alla loggar i samma fil. Vid inlämning exporteras loggarna även som CSV, eftersom kursen kräver att datafilen lämnas in och CSV är enklast att bläddra i för en granskare.

Jag har inte kunnat bekräfta om StrengthLog stödjer CSV-export (sökningarna hittade det för appen Strong, inte StrengthLog specifikt). Bygg därför inte in ett beroende av det. En generisk importfunktion för CSV är ett möjligt tillägg om tiden räcker, men inte en grundförutsättning.

## Externt API: Open Food Facts
Gratis, kräver ingen API-nyckel, base URL world.openfoodfacts.org. Används för att slå upp protein och kalorier per 100 gram för ett livsmedel.

Kända fallgropar att hantera med try/except:
- API:t kan svara 200 OK men ändå ha status 0 i svaret, vilket betyder att livsmedlet inte hittades. Det räcker alltså inte att kolla statuskoden, man måste läsa fältet i JSON-svaret.
- Nätverksfel eller timeout, requests.exceptions.
- Saknade fält i svaret för vissa produkter, kräver .get() med default istället för direkt nyckelåtkomst.

Detta är en tilläggsfunktion. Om den tar för mycket tid, prioritera bort den och behåll manuell inmatning av protein och kalorier. Kärnan i betyget sitter i klasserna, felhanteringen och den regelbaserade analysen, inte i API-anropet.

## Bibliotek
Standard: json, csv, datetime, os, statistics.
Externt: requests (API), matplotlib (diagram).

## Programflöde (CLI, notebook-vänligt)
1. Fråga efter användarnamn. Finns profilen, ladda den. Finns den inte, skapa en ny CutProfile med start och målvärden.
2. Meny: logga dagens data, slå upp livsmedel, visa analys, visa diagram, avsluta.
3. Vid avslut, spara profilen automatiskt och exportera CSV.

## Var varje obligatoriskt moment används i CutTrack
Tanken med det här avsnittet är att du ska kunna peka på en konkret plats i koden för varje krav, både när du bygger och under redovisningen.

### Variabler och datatyper
- int: steps, training_minutes
- float: weight, calories, protein
- str: name, date
- bool: om ett mål är uppnått eller inte
- lista: logs, alla DailyLog-objekt i en profil
- dict: JSON-datan när profilen läses in och sparas

### If-satser
Används där programmet ska välja mellan olika utfall. Typiska ställen:
- i check_goals, jämför uppmätt värde mot mål och välj vilken rekommendation som returneras
- i run_menu, vilket menyval användaren skrev
- i load_profile, om filen finns eller inte
- i search_food, om API-svaret innehåller status 0, alltså livsmedlet hittades inte

Exempel på nivån det handlar om:

    if average_protein >= protein_goal:
        recommendation = "Proteinmålet nås."
    else:
        recommendation = "Öka proteinet."

### Loopar
Används där du gör samma sak med många saker. Typiska ställen:
- for-loop över logs för att räkna ihop medelvärden
- for-loop när loggarna skrivs rad för rad till CSV
- for-loop när JSON-datan görs om till DailyLog-objekt vid inläsning
- while-loop i run_menu, som kör tills användaren väljer avsluta

Exempel:

    for log in logs:
        total_weight = total_weight + log.weight

och

    while True:
        choice = input("Välj: ")
        if choice == "5":
            break

### Funktioner
Kravet är minst 3 till 5. Räkna load_profile, save_profile, export_logs_csv, calculate_trend och plot_weight som de fem. Varje funktion ska ta parametrar och returnera något, inte bara skriva ut.

### Felhantering
- try/except vid filinläsning, filen saknas eller är trasig JSON
- try/except när en DailyLog skapas, ValueError vid orimliga värden
- try/except vid API-anropet, nätverksfel och timeout

### Datahantering
JSON vid spara och läsa profil, CSV vid export. CSV-filen är den som lämnas in.

### Klasser och arv
User är basklass, CutProfile ärver från den och lägger till mål och check_goals. DailyLog är en egen klass för en dags data.

### Bibliotek
Standardbibliotek: json, csv, datetime, statistics. Externt: matplotlib, och requests om API-delen byggs.

### API eller extern data
Open Food Facts via requests. Om den delen prioriteras bort uppfylls kravet istället genom inläsning av extern CSV-fil, vilket kursen godkänner som alternativ.

## Filstruktur (inför att det senare blir en app)
Håll input/output (input(), print()) i egna funktioner, separat från klasserna och beräkningslogiken. Det gör det enklare att byta ut CLI mot en app senare utan att röra kärnlogiken.
