# CutTrack

Ett verktyg för dig som deffar. Du loggar vikt, kalorier, protein, steg och träning varje dag, och CutTrack visar om utvecklingen går åt rätt håll. Programmet väntar med att dra slutsatser tills det finns underlag, eftersom en enskild vägning mest är brus.

![Viktutveckling](resultat_diagram.png)

Status: version 1 fungerar och byggs vidare. Gränssnittet är en textmeny som startas från terminalen med `python main.py`, och notebooken `cuttrack.ipynb` förklarar och provar koden. Skrivet i Python, med matplotlib för diagram.

## Varför CutTrack finns

Den som deffar vill tappa fett men behålla muskelmassan. Problemet är att en enskild vägning inte säger något pålitligt: vikten svänger flera hundra gram från dag till dag på grund av vätska och maginnehåll, mer än en hel veckas verkliga fettförlust. Utan ett sätt att skilja brus från trend blir varje dags siffra lika mycket värd som nästa, och det är svårt att veta om dieten fungerar.

Jag har löst det här manuellt, med klipp och klistra och skärmdumpar. Det fungerar för mig men går inte att ge vidare till någon annan. CutTrack gör samma sak i ett program där varje person har sin egen profil och sina egna loggar.

Projektet började som slutprojekt i kursen Utveckling med Python, grund, inom YH-utbildningen AI Developer på Jensen Education, och byggs nu vidare som ett eget projekt.

## Vad programmet gör

- Varje användare har en egen profil med längd, ålder, kön, aktivitetsnivå, startvikt, målvikt och önskad takt. Profilen sparas som JSON.
- Dagliga loggar med datum, vikt, kalorier, protein, steg, träning (ja eller nej) och midjemått (valfritt). Datumet kontrolleras och skrivs som ÅÅÅÅ-MM-DD med nollor, så 2026-10-8 sparas som 2026-10-08. En ny logg för ett datum som redan finns ersätter den gamla.
- Ett personligt kaloriförslag beräknat från profilen, med ett golv som programmet förklarar när det slår i.
- Analys över 7, 14 eller 30 dagar: viktens takt i procent per vecka, protein, träningsfrekvens och steg, plus en sak att fokusera på.
- Diagram för vikt (med rullande sjudagarssnitt och målvikt), protein och steg. Menyn visar än så länge bara viktdiagrammet.
- Export och import av loggar som CSV, med en egen exportfil per användare. Går det fel på hela filen läses ingenting in, och ett meddelande säger vad som är fel. En rad med ogiltiga värden hoppas över i stället för att stoppa hela importen.

## Så bedömer CutTrack din deff

| Område | Så bedöms det |
| --- | --- |
| Vikt | Takten räknas som procent av kroppsvikten per vecka, från skillnaden mellan snittet för den senaste perioden och snittet för perioden före. Går det långsammare än ditt eget mål flaggas det. Går det över 1,0 procent per vecka flaggas det alltid, oavsett ditt mål, eftersom risken för muskelförlust ökar. Ökar vikten, eller står den still (mindre än 0,05 kg per vecka), flaggas det också. |
| Protein | Dagligt snitt mot ett mål på 1,9 gram per kilo målvikt. |
| Träning | Antal träningsdagar mot ditt mål, standard tre per vecka, omräknat till vald period. |
| Steg | Dagligt snitt mot ditt stegmål, standard 8 000. |
| Prioritering | Alla fyra områden visas, sedan lyfts en sak fram att fokusera på: vikt först, därefter protein, träning och steg. |

Av målen frågar menyn bara efter målvikt och takt. Standardvärdena för protein, steg och träning ligger i koden och kan ändras i profilens JSON-fil.

Programmet väntar med bedömningen. En vald period (7, 14 eller 30 dagar) krävs för att visa ett snitt och två perioder för att bedöma takten, eftersom takten jämför snittet för den senaste perioden med snittet för perioden före. Med sjudagarsperiod börjar full analys på dag 14, med 14 dagars period på dag 28 och med 30 dagar på dag 60. Under väntetiden skriver programmet en förklaring och hur många dagar som återstår.

## Exempel

Exemplet kommer från en testperiod på 20 dagar med profilen Testperson: man, 189 cm, 39 år, startvikt 101,5 kg, målvikt 98 kg, önskad takt 0,6 procent per vecka, proteinmål 2,1 gram per kilo målvikt, stegmål 10 000 och fem träningsdagar i veckan. Loggarna är simulerade, inte en logg förd dag för dag, och finns i [data/exempel_loggar.csv](data/exempel_loggar.csv). Utskrifterna visar analysen över de senaste sju dagarna, jämförd med de sju dagarna före.

**Efter 14 dagar, första gången full analys är möjlig:**
```
Vikten: minskar med 1.66 procent per vecka (cirka 1.6 kg), över säkerhetsgränsen 1,0 procent (cirka 1.0 kg för dig). Risk för muskelförlust.
Protein: snitt 211 g mot mål 206 g. Målet nås.
Träning: 5 av 5 förväntade dagar under perioden. Målet nås.
Steg: snitt 10160 mot mål 10000. Målet nås.

Fokusera på: vikt.
```

**Efter 18 dagar (bara viktraden visas här):**
```
Vikten: minskar med 1.54 procent per vecka (cirka 1.5 kg), över säkerhetsgränsen 1,0 procent (cirka 1.0 kg för dig). Risk för muskelförlust.
```

**Efter 20 dagar:**
```
Vikten: minskar med 1.12 procent per vecka (cirka 1.1 kg), över säkerhetsgränsen 1,0 procent (cirka 1.0 kg för dig). Risk för muskelförlust.
Protein: snitt 213 g mot mål 206 g. Målet nås.
Träning: 5 av 5 förväntade dagar under perioden. Målet nås.
Steg: snitt 9953 mot mål 10000. Under målet.

Fokusera på: vikt.
```

Takten räknas från snitten. Efter 14 dagar jämförs snittet för dag 8 till 14 (99,03 kg) med snittet för dag 1 till 7 (100,67 kg): skillnaden är 1,64 kg på en vecka, och det är 1,66 procent av 99,03 kg. Efter 18 och 20 dagar flyttas båda perioderna framåt, och takten blir 1,54 respektive 1,12 procent per vecka. Den ligger över säkerhetsgränsen vid alla tre tillfällena men minskar i takt med att veckosnittet för vikten planar ut (99,03, 98,26 och 98,13 kg vid de tre tillfällena). Efter 20 dagar ligger stegen under målet, men vikten har företräde i prioriteringen, så fokus ligger kvar på vikt. Utskrifterna visar vad programmet faktiskt skriver ut, inte vad som är sant om testpersonens utveckling.

Programmets kaloriförslag för samma profil blev 2409 kcal per dag. Det faktiska intaget i datan låg på 2300 kcal, 109 kcal under förslaget, vilket enligt 7700-regeln motsvarar cirka 0,1 kg i veckan och alltså inte förklarar nedgången i exemplet. Datan är simulerad och vikten är inte räknad ur intaget, så exemplet visar hur programmet beskriver en given logg, inte hur en kropp reagerar.

Midjemåttet loggades tre gånger och sjönk från 90,0 till 88,2 cm. CutTrack sparar det men analyserar det inte än (se Roadmap). Läst för hand pekar en sjunkande midja tillsammans med sjunkande vikt mot att det är fett som försvinner, resonemanget finns i [docs/produktvision.md](docs/produktvision.md).

Diagrammen från samma testperiod: viktdiagrammet står överst på sidan, protein och steg följer här.

![Proteinintag](resultat_protein.png)

![Steg](resultat_steg.png)

## Kom igång

1. Klona repot och gå in i mappen:
   ```
   git clone https://github.com/NiklasEkeskar/CutTrack.git
   cd CutTrack
   ```
2. Skapa och aktivera en virtuell miljö (rekommenderas):
   ```
   python -m venv .venv
   source .venv/bin/activate
   ```
   Kommandot `source` gäller bash och zsh. I PowerShell aktiveras miljön med `.venv\Scripts\Activate.ps1` på Windows och `.venv/bin/Activate.ps1` på macOS och Linux.
3. Installera det programmet behöver, som är matplotlib:
   ```
   python -m pip install -r requirements.txt
   ```
   `requirements.txt` godtar matplotlib 3.11 och senare, men inte version 4. matplotlib 3.11 kräver Python 3.11 eller senare, så det gäller även CutTrack. Installationen är provad på Python 3.11, 3.12, 3.13 och 3.14.
4. Starta programmet från projektets rotmapp:
   ```
   python main.py
   ```
   Menyn frågar efter ditt namn och skapar en profil åt dig första gången. Avsluta med val 6, Spara och avsluta. Varje ny logg som du lägger till med val 1 sparas direkt i profilfilen, så den finns kvar även om du avbryter med Ctrl+C eller Ctrl+D eller stänger terminalen. Det du läst in från en CSV-fil med val 5 sparas inte direkt, utan nästa gång du lägger till en logg med val 1 eller med val 6.

Notebooken `cuttrack.ipynb` går igenom koden steg för steg och provar den med exempeldata. Öppna den i VS Code (med tillägget Jupyter) eller i Jupyter, välj den virtuella miljön som kernel och kör cellerna uppifrån och ner. Miljön behöver en Jupyter-kärna för det (`python -m pip install ipykernel`), som inte ingår i requirements-filerna eftersom programmet och testerna inte behöver den. Notebooken kör inte menyn, eftersom allt en cell skriver ut sparas i filen och repot är publikt.

Ändrar du något i `models.py`, `analysis.py` eller `main.py` medan notebooken är öppen måste kerneln startas om (Restart), eftersom Python bara läser in en modul en gång per körning.

Profilen sparas som `<namn>.json` i mappen du kör från. Den skrivs först till `<namn>.tmp.json` och får sitt riktiga namn när allt är skrivet, så att ett fel mitt i skrivningen inte förstör den profil som redan ligger där. Blir en `.tmp.json`-fil kvar efter en krasch kan du radera den, den skrivs över vid nästa sparning. Val 6 i menyn exporterar dessutom loggarna till `<namn>_loggar.csv` i samma mapp, med namnet byggt på samma sätt som för profilfilen: Anna Berg får `annaberg.json` och `annaberg_loggar.csv`. Git ignorerar alla `.json`- och `.csv`-filer, så dina egna profiler och loggar checkas inte in av misstag. Det enda undantaget är `data/exempel_loggar.csv`, den simulerade exempeldatan som exemplen i README bygger på. Den skrivs av notebookens exempelcell under Resultat och innehåller bara loggar, ingen profil och ingen riktig person.

**Så ska en CSV-fil se ut.** Menyval 5 läser samma format som exporten skriver: komma mellan kolumnerna, punkt som decimaltecken och teckenkodningen UTF-8, med eller utan BOM (en dold markering först i filen). Rubrikraden ska ha kolumnerna `date`, `weight`, `calories`, `protein`, `steps`, `trained` och `waist`, i valfri ordning, och andra kolumner ignoreras. Datum skrivs ÅÅÅÅ-MM-DD, steg som heltal och träning som `True` eller `False` med valfria versaler. Midjemåttet får vara en tom cell. En fil som inte följer det läses inte alls, och programmet säger vad som är fel: fel teckenkodning, ingen rubrikrad, semikolon mellan kolumnerna eller saknade kolumner. En enskild rad med fler eller färre celler än rubrikraden, ett värde som inte är ett tal eller en träningscell som inte är `True` eller `False` hoppas över med ett meddelande, och resten av filen läses in. Rader där alla celler är tomma hoppas över utan meddelande.

**Prova med exempeldatan.** Vill du se en analys utan att först logga i två veckor kan du läsa in exempelfilen i en testprofil. Starta programmet från projektets rotmapp, skriv ett namn som inte är ditt eget, till exempel `Test`, och svara på profilfrågorna med valfria värden. Välj 5 i menyn, skriv `data/exempel_loggar.csv` som filnamn och välj sedan 2 och 7. Du får utskriften för 20 dagar. Menyn frågar bara efter målvikt och takt, så protein, träning och steg räknas mot standardmålen och de raderna blir andra än i exemplet ovan. Använd inte ditt riktiga namn: loggar med samma datum ersätts av de simulerade, och ändringen sparas om du avslutar med val 6. Avsluta med Ctrl+C om inget ska sparas.

**Köra testerna.** Testerna använder pytest, som bara behövs för att utveckla, inte för att köra programmet. Installera det i samma virtuella miljö och kör från projektets rotmapp:
```
python -m pip install -r requirements-dev.txt
python -m pytest
```
`requirements-dev.txt` tar med `requirements.txt` och lägger till pytest 9.1 eller senare, men inte version 10. Varje test som rör filer körs i en egen tillfällig mapp, så testerna skriver inga profiler eller CSV-filer i projektet.

## Projektstruktur

```
CutTrack/
  models.py             DailyLog, User, CutProfile och normalize_date (data och regler)
  analysis.py           filhantering (JSON, CSV) och diagram
  main.py               textmenyn och programmets startpunkt (python main.py)
  cuttrack.ipynb        förklaringar och exempelkörning (kör inte menyn)
  tests/                automatiska tester (pytest)
  pytest.ini            inställning för pytest
  requirements.txt      beroenden för att köra programmet (matplotlib)
  requirements-dev.txt  beroenden för att köra testerna (pytest, tar med requirements.txt)
  data/                 exempel_loggar.csv, simulerad exempeldata
  docs/                 produktvision, kravspec, teknisk plan, statuslogg
  LICENSE               MIT-licensen
  README.md
  *.png                 bilder till README
```

## Hur det är byggt

**Klasser och arv.** `DailyLog` är en dags logg och validerar datum, vikt och kalorier när objektet skapas. `User` är basklassen med personens grunddata och metoderna som räknar på loggarna. `CutProfile` ärver från `User` med `super().__init__()` och lägger till mål, kaloriberäkning (Mifflin-St Jeor) och regelanalysen i `check_goals`. Att deffa är ett läge bland flera möjliga, så arvet gör det möjligt att lägga till andra lägen utan att ändra `User`.

**Kalenderdagar, inte antal loggar.** Fönstret för ett snitt räknas i kalenderdagar bakåt från det senast loggade datumet, inte som de senaste raderna i listan. Annars skulle sju loggar utspridda över en månad räknas som ett veckosnitt. Urvalet ligger i `get_logs`, som alla snitt använder, så regeln finns på ett enda ställe. Perioden före hämtas med samma regel: `get_logs(7, 7)` hoppar över de sju senaste dagarna och tar de sju därefter.

**Dagar sedan start.** `days_since_start` räknar dagarna från starten till det senast loggade datumet, båda dagarna medräknade. Starten är profilens startdatum, eller den tidigaste loggen om den ligger före startdatumet. Det händer när äldre loggar läses in i en ny profil, till exempel exempelfilen, som annars hade gett ett negativt antal dagar. Datumen görs om till datum och jämförs inte som text. Räkningen slutar vid senaste loggade dagen och inte vid dagens datum, av samma skäl som i `get_logs`. `waiting_message` använder antalet för att avgöra om det finns underlag för ett snitt (en period) och för takten (två perioder).

**Datum.** Funktionen `normalize_date` i `models.py` kontrollerar att en text är ett riktigt datum och skriver om det som ÅÅÅÅ-MM-DD med nollor, så `2026-10-8` blir `2026-10-08`. Den används av `DailyLog` för loggens datum, av `User` för startdatumet och av `log_today` i menyn, som kontrollerar datumet före de andra frågorna så att ett fel datum stoppar direkt. Alla datum sparas därmed på samma sätt. Det gör att `current_weight` och `weight_change` kan jämföra dem som text, och att samma dag skriven med och utan nolla räknas som en och samma dag. Ett datum som inte finns (`2026-02-30`) eller en text som inte är ett datum ger ett svenskt felmeddelande i menyn. I en CSV-fil hoppas en sådan rad över, och i en profilfil säger programmet att filen innehåller ogiltiga värden. Mellanslag före och efter datumet tas bort. Kontrollen gäller att datumet finns och har rätt format, inte att det är rimligt (se Begränsningar).

**Kontroll av värden.** `DailyLog`, `User` och `CutProfile` kontrollerar själva att varje värde är ett tal av rätt sort inom rimliga gränser, och kastar `ValueError` med ett svenskt meddelande annars. Gränserna står som konstanter överst i `models.py`. Eftersom kontrollen ligger i klasserna gäller den lika för menyn, CSV-filer och profilfiler. Menyn frågar om längd, ålder och namn direkt när svaret är fel, godtar decimalkomma, och tolkar j, ja, n och nej på träningsfrågan.

**Takten jämför två perioder.** `check_goals` räknar medelvikten för den senaste perioden och för perioden före. Ett snitt ligger mitt i sin period, så de två snitten hör till tidpunkter som ligger lika många dagar isär som perioden är lång. Skillnaden delas därför med periodens längd och multipliceras med sju, vilket ger kilo per vecka, och procenttalet räknas på det senaste snittet. Då ger en och samma nedgång per vecka samma kilotal för 7, 14 och 30 dagar, och en enskild vägning är bara en av många i snittet. Är skillnaden under 0,05 kg per vecka avrundas den till 0,0 kg, och vikten får texten oförändrad i stället för "minskar med 0.0 kg". Saknas vägningar i någon av perioderna står det att det är för lite data.

**Saknade värden.** `None` betyder att ett värde saknas, 0 betyder att det mättes till noll. Ett midjemått som inte mätts är `None`, och kontrollen görs med `is not None` eftersom 0 och `None` annars behandlas lika i ett vanligt if-test.

**Validering i klassen.** `DailyLog` och `CutProfile` kastar `ValueError` vid orimliga värden och vid ett datum som inte finns, så kontrollen gäller oavsett om objektet skapas av inmatning, CSV-import eller en JSON-fil.

**Felhantering.** `load_profile` har sex separata except-block (trasig JSON, fel teckenkodning, saknat fält, fel uppbyggnad, ogiltigt värde och en fil som inte går att öppna) eftersom felen betyder olika saker för användaren. Ger `load_profile` `None` för en fil som finns men inte går att läsa stannar menyn med ett meddelande och ändrar inte filen, eftersom en ny profil annars skulle skriva över filen vid val 6. `save_profile` skriver först till en temporär fil och byter namn när allt är skrivet (`os.replace`), så att ett fel mitt i skrivningen lämnar den gamla profilen orörd. Menyn sparar profilen direkt efter varje ny logg, och val 6 avslutar bara om sparningen lyckades. `import_logs_csv` skiljer på fel i hela filen och fel i en rad. Hela filen läses in innan någon logg läggs till, så en fil som inte är UTF-8, inte går att tolka som CSV, saknar rubrikrad, har semikolon eller saknar kolumner ger ett meddelande och ingen halvt inläst profil. Ett fel i en rad fångas med try/except inne i loopen, så att raden hoppas över i stället för att stoppa importen. Skrivfel fångas med `OSError`.

**Säkra filnamn.** Filnamnen byggs aldrig direkt av det användaren skriver. `make_safe_name` behåller bara a till z och siffror, så ett namn som `../../etc/passwd` inte kan styra var filen hamnar. `make_filename` och `make_csv_filename` lägger sedan till `.json` respektive `_loggar.csv`, så varje användare får en egen profilfil och en egen exportfil.

**Tester.** `tests/` innehåller automatiska tester med pytest. `test_models.py` täcker reglerna: validering (även av datum), kalenderdagsfönstret, snitt, kaloriförslag och golv, väntetid och vilken gren `check_goals` väljer. `test_analysis.py` täcker filhanteringen: filnamn, profilfiler (även en sparning som avbryts mitt i och profilfiler som inte går att läsa), CSV-export och inläsning, med både trasiga rader och trasiga filer. `test_readme_example.py` låser vad `check_goals` skriver ut i exemplet ovan, kontrollerar att README visar samma rader som koden och att exempelfilen ger samma analys i en profil som skapats efter loggarna, och innehåller testerna av hur vikttakten räknas. `test_main.py` täcker menyn, bland annat att profilen sparas efter varje ny logg och att menyn stannar vid en profilfil som inte går att läsa: testet skriver in svaren åt programmet i stället för tangentbordet, och fyra tester kör Python som ett eget program, för att se att `python main.py` startar, att menyn inte startar vid import och att en trasig profilfil lämnas orörd. Ett av menytesterna följer instruktionen för exempeldatan ovan: en ny användare läser in exempelfilen och får en analys. Förväntade värden är uträknade för hand i kommentarerna, inte kopierade från programmets utskrift. Diagrammen testas inte.

**Beroenden.** Det programmet behöver står i `requirements.txt` och det som bara behövs för att utveckla i `requirements-dev.txt`, så att den som bara vill köra programmet slipper installera pytest. Varje rad anger en lägsta och en högsta version, till exempel `matplotlib>=3.11,<4`. Den lägsta är den första utgåvan som är provad, och den högsta utesluter nästa huvudversion, som kan ändra hur biblioteket fungerar.

**Gränssnittet är separat från logiken.** All inmatning och utskrift ligger i `main.py`, skilda från klasserna i `models.py` och filhanteringen i `analysis.py`, så att menyn kan bytas mot ett annat gränssnitt utan att röra beräkningarna.

**Kaloriberäkningen visuellt.** Diagrammet nedan visar hela kedjan i `suggest_calorie_goal` och `check_goals`, från TDEE till det slutliga kaloriförslaget, med ett fristående räkneexempel (inte samma profil som i exemplet ovan). Det är en illustration som förklarar golvlogiken, inte en skärmdump från CutTrack.

![Hur CutTrack styr en deff, med räkneexempel](golvlogik_diagram.png)

## Källor och antaganden

- Mifflin MD, St Jeor ST, Hill LA, Scott BJ, Daugherty SA, Koh YO. *A new predictive equation for resting energy expenditure in healthy individuals.* Am J Clin Nutr. 1990;51(2):241-247. https://pubmed.ncbi.nlm.nih.gov/2305711/
- Wishnofsky M. *Caloric equivalents of gained or lost weight.* Am J Clin Nutr. 1958;6(5):542-546. https://pubmed.ncbi.nlm.nih.gov/13594881/
- Hall KD, Sacks G, Chandramohan D, Chow CC, Wang YC, Gortmaker SL, Swinburn BA. *Quantification of the effect of energy imbalance on bodyweight.* Lancet. 2011;378(9793):826-837. https://pubmed.ncbi.nlm.nih.gov/21872751/
- Garthe I, Raastad T, Refsnes PE, Koivisto A, Sundgot-Borgen J. *Effect of two different weight-loss rates on body composition and strength and power-related performance in elite athletes.* Int J Sport Nutr Exerc Metab. 2011;21(2):97-104. https://pubmed.ncbi.nlm.nih.gov/21558571/
- Helms ER, Aragon AA, Fitschen PJ. *Evidence-based recommendations for natural bodybuilding contest preparation: nutrition and supplementation.* J Int Soc Sports Nutr. 2014;11:20. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4033492/
- Morton RW, Murphy KT, McKellar SR, m.fl. *A systematic review, meta-analysis and meta-regression of the effect of protein supplementation on resistance training-induced gains in muscle mass and strength in healthy adults.* Br J Sports Med. 2018;52(6):376-384. https://pmc.ncbi.nlm.nih.gov/articles/PMC5867436/
- Jensen MD m.fl. *2013 AHA/ACC/TOS Guideline for the Management of Overweight and Obesity in Adults.* Circulation. 2014;129(25 Suppl 2). https://doi.org/10.1161/01.cir.0000437739.71477.ee

**Basalomsättning (`calculate_bmr`)** räknas enligt Mifflin-St Jeor.

**Underskottet i `suggest_calorie_goal`** bygger på tumregeln 7700 kcal per kilo kroppsfett, ursprungligen Wishnofsky 1958. Regeln antar ett konstant energiunderskott, vilket inte stämmer: förbrukningen sjunker i takt med vikten, vilket gör att regeln överskattar den faktiska viktnedgången över tid. Hall m.fl. 2011 visar det med en dynamisk modell. CutTrack använder 7700-regeln medvetet som en enkel startpunkt, inte för att den är exakt.

**Kalorigolvet** är det högsta av en fast gräns och personens egen basalomsättning. De fasta gränserna, 1 200 kcal för kvinnor och 1 500 kcal för män, är nedre kanten i riktlinjerna för behandling av övervikt och fetma hos vuxna (Jensen m.fl. 2013), som rekommenderar 1 200 till 1 500 kcal per dag för kvinnor och 1 500 till 1 800 för män, vanligen justerat efter kroppsvikt. Riktlinjerna gäller personer med övervikt eller fetma, CutTrack använder dem som golv för alla användare, vilket är en förenkling. Basalomsättningen läggs till eftersom ett förslag under vad kroppen gör av med i vila är svårt att motivera, och för att golvet då följer personen i stället för ett fast tal. Slår golvet i justerar programmet aldrig tyst: det säger vad som hände, vilket golv som gällde och vilken takt användaren faktiskt får.

**Säkerhetstaket på 1,0 procent per vecka i `check_goals`** utgår från Garthe m.fl. 2011, som jämförde 0,7 mot 1,4 procent viktnedgång per vecka hos idrottare. Gruppen på 0,7 procent ökade fettfri massa, gruppen på 1,4 procent gjorde det inte. CutTracks tak på 1,0 procent ligger mellan de två, som en säkerhetsmarginal snarare än en exakt återgivning av studiens resultat.

**Proteinmålet (1,9 g per kilo målvikt)** utgår inte direkt från Helms m.fl. 2014, som rekommenderar 2,3 till 3,1 g per kilo fettfri massa för tävlande bodybuildare under tävlingsförberedelse. CutTrack loggar ingen kroppsfettsprocent och kan därför inte räkna på fettfri massa. 1,9 g/kg kroppsvikt ligger i stället i linje med Morton m.fl. 2018, vars metaanalys visar att nyttan för muskelbevarande planar ut runt 1,6 g/kg kroppsvikt med en praktisk övre gräns kring 2,2, ett intervall som passar bättre för en icke-tävlande användare.

## Begränsningar

- Vikttakten bygger på att det finns vägningar i båda perioderna, men programmet kräver bara en vägning per period. En period med få vägningar ger ett snitt som är nästan lika osäkert som en enskild vägning. Luckor i loggningen gör dessutom att avståndet mellan de två snitten inte är exakt lika långt som perioden, så takten blir mindre exakt ju fler dagar som saknas. Loggar du de flesta dagar är felet litet.
- Kaloriförslaget är en uppskattning. 7700-regeln överskattar viktnedgången över tid, så siffran ska justeras efter verkligt utfall efter ett par veckors loggning.
- Proteinmålet räknas på målvikt eftersom programmet inte känner till kroppsfett.
- Under väntetiden visar programmet bara en förklaring. Protein, steg och träning analyseras inte förrän perioden är full, och snittet visas inte under dag 7 till 13.
- Midjemåttet sparas men används inte i någon analys än.
- Takten jämför två hela perioder, så vald period styr väntetiden: med 30 dagar krävs 60 dagars data innan takten bedöms.
- Menyn visar bara viktdiagrammet.
- Testerna täcker reglerna, filhanteringen och menyn, inte diagrammen.
- Menyn sparar profilen efter varje ny logg (val 1), men inte efter en CSV-inläsning (val 5). Det du läst in sparas nästa gång du lägger till en logg med val 1, eftersom hela profilen sparas då, eller med val 6. Avbryter du innan är det inlästa borta, men CSV-filen finns kvar att läsa in igen. Sparningen går via en temporär fil och byter namn när allt är skrivet, men tvingar inte ut filen till disken (`fsync`) först, så ett strömavbrott i fel ögonblick kan ändå ge en förlorad eller trasig fil. En krasch eller ett avbrott mitt i skrivningen kan lämna en `.tmp.json`-fil kvar. CSV-exporten skrivs fortfarande rakt in i målfilen, så en export som avbryts mitt i kan förstöra den förra kopian. Misslyckas sparningen vid val 6 stannar menyn och du kan försöka igen, men det du inte sparat är borta om du avbryter i stället.
- Värdena kontrolleras mot gränser som fångar skrivfel, inte mot vad som är bra för kroppen: vikt över 0 och högst 300 kg, kalorier 0 till 10 000, protein 0 till 1 000 g, steg 0 till 100 000, midjemått 30 till 250 cm, längd 100 till 250 cm och ålder 18 till 100 år. CutTrack är byggt för vuxna, eftersom riktlinjerna bakom kaloriförslaget gäller vuxna. Menyn godtar decimalkomma men inte tusentalsavgränsare: `2,000` läses som 2, inte 2000, och `2.000` likaså. Felmeddelanden för de vanligaste filfelen är på svenska, men ett ovanligt fel visas med operativsystemets egen text.
- Två namn kan ge samma profilfil, eftersom filnamnet bara behåller a till z och siffror: Åke och Äke får båda `ke.json`. Programmet laddar bara profilen när namnet i filen är samma som det du skrev, med valfria versaler och mellanslag, och stannar annars utan att ändra filen. Den som kommer sist får välja ett annat namn, till exempel med efternamnet.
- En profilfil som inte går att läsa (kapad, tom, fel teckenkodning, fel uppbyggnad, saknade fält eller en mapp med profilfilens namn) får programmet att stanna med ett meddelande, utan att ändra filen. Du får själv rätta filen eller flytta den ut ur projektmappen, programmet försöker inte laga den. Byter du bara namn på den, till exempel till `annaberg.json.bak`, ignorerar git den inte längre, eftersom bara `.json` och `.csv` ignoreras. Programmet slutar då utan felkod, så ett skript som startar det ser inte att det stannade.
- Programmet kontrollerar att ett datum finns och har formatet ÅÅÅÅ-MM-DD, men inte att det är rimligt. Ett datum i framtiden eller med fel år, till exempel 2062 i stället för 2026, godtas, och då räknas dagar sedan start och analysen från det datumet. Kontrollera själv att året stämmer när du loggar.
- CSV-inläsningen läser bara komma mellan kolumnerna och punkt som decimaltecken. Ett kalkylprogram kan spara med semikolon: enligt [Microsoft Support](https://support.microsoft.com/en-us/office/import-or-export-text-txt-or-csv-files-5250ac4c-663c-47ce-937b-339e391393ba) är Excels avgränsare ett komma som standard, och ett komma som decimaltecken ger semikolon. En sådan fil läses inte alls, och programmet säger det. Spara om den med komma mellan kolumnerna och punkt som decimaltecken. Ett tal med decimalkomma i en fil med komma mellan kolumnerna hoppas över med ett meddelande. Träning läses bara som `True` eller `False`, med valfria versaler, så `ja` och `SANT` hoppas över med ett meddelande. Värden utanför gränserna, till exempel negativt protein eller `nan`, hoppas också över med ett meddelande.
- CutTrack kräver Python 3.11 eller senare, eftersom matplotlib 3.11 gör det. Äldre Python är inte provat.
- Exempeldatan är simulerad.

## Ansvarsfriskrivning

CutTrack ger allmänna riktvärden baserade på etablerade rekommendationer. Det är inte medicinsk rådgivning. Rådgör med läkare eller dietist vid sjukdom, graviditet eller medicinering.

## Licens

CutTrack är öppen källkod under MIT-licensen, se [LICENSE](LICENSE). Du får använda, ändra och sprida koden, även kommersiellt, så länge copyright- och licenstexten följer med. Koden levereras som den är, utan garanti.

Licensen gäller programvaran och dokumentationen i det här repot. Den gäller inte matplotlib och pytest, som installeras separat och har egna licenser. Licensens ansvarsbegränsning ersätter inte ansvarsfriskrivningen ovan: CutTrack är inte medicinsk rådgivning.

## Vad jag lärde mig

**Bygg en del i taget och testa innan nästa.** Jag planerade och skissade lösningen innan jag skrev kod, byggde en del i taget och testade varje funktion innan jag gick vidare. Det gjorde koden lättare att förstå och minskade risken att fel följde med till senare delar.

**`get_logs` var det svåraste.** Metoden väljer vilka loggar som ingår i ett snitt eller en trend utifrån kalenderdagar räknade bakåt från det senast loggade datumet. Den hämtar alltså inte bara de senaste raderna i listan, vilket spelar roll eftersom användaren kan ha missat att logga vissa dagar. Samma metod används för medelvikt, viktförändring och träningsfrekvens, så när jag förstod `get_logs` blev resten av `User`-klassen lättare att följa. Jag såg också fördelen med att samla urvalet på ett ställe i stället för att upprepa logiken i flera metoder.

**Bestäm strukturen tidigt.** Under arbetet skapades dubbla mappar och filer hamnade både i docs och i projektroten. Det kostade en hel kväll att reda ut och gjorde det svårare att veta vilken version som var aktuell. Den viktigaste lärdomen är att en tydlig struktur runt koden är lika viktig som att själva koden fungerar.

**Regler först, maskininlärning senare.** CutTrack är regelbaserat med avsikt: jag har bestämt sjudagarsfönstret, säkerhetstaket på 1,0 procent per vecka och hur proteinmålet räknas, och `check_goals` jämför mot de gränserna. En framtida modell skulle kunna tränas på historiska data för att hitta samband mellan vikt, kalorier, protein och träning, men det kräver betydligt fler observationer och mer testdata än ett enskilt projekt har. Klasserna, valideringen, filhanteringen och datainsamlingen skulle kunna återanvändas. Det som skulle behövas är dataförberedelse, träning och utvärdering av modellen, och en `check_goals` som baserar sin återkoppling på modellens förutsägelse i stället för på mina fasta regler. En modell kan inte ge tillförlitliga bedömningar utan tillräcklig och välstrukturerad data, och det är den delen CutTrack bygger.

## Roadmap

Nästa steg, i den ordning jag tänker ta dem. Detaljer finns i [docs/produktvision.md](docs/produktvision.md) och [docs/statuslogg.md](docs/statuslogg.md).

1. **Grund.** Automatiska tester för reglerna, filhanteringen och menyn är klara (se Hur det är byggt). Programmet startar med `python main.py` utan Jupyter, och beroendena installeras med `requirements.txt` och `requirements-dev.txt`. Licensen är MIT (se Licens).
2. **Rätta vikttakten och bygg det visionen redan beskriver.** Vikttakten räknas nu på snitt: snittet för den senaste perioden jämförs med snittet för perioden före. Antalet dagar sedan start räknas nu från det tidigaste av profilens startdatum och första loggen, så exempelfilen går att läsa in i en ny profil. Datum kontrolleras nu och skrivs om till ÅÅÅÅ-MM-DD med nollor, så ett datum utan nolla rättas och ett datum som inte finns ger ett meddelande. CSV-filer med fel teckenkodning, semikolon, saknade kolumner, rader med fel antal celler eller något annat än True och False i träningskolumnen ger nu ett meddelande i stället för ett Python-fel eller ett tyst fel. Profilfiler som inte går att läsa ger nu ett meddelande, och programmet ändrar inte filen. Profilen sparas direkt efter varje ny logg och skrivs via en temporär fil, så att ett fel mitt i skrivningen inte förstör den. Därefter analys av protein, steg och träning redan under väntetiden, snittet under dag 7 till 13, friskrivningen även vid kaloriförslaget, protein- och stegdiagram i menyn och sist midjemått jämfört med vikt.
3. **Mer räkning på redan loggad data.** Dagar till målvikt (linjär projektion av aktuell takt), platådetektion (vikten har stått still trots rätt underskott), midjemått mot vikt över hela perioden, och korrelation mellan protein, steg, träning och viktförändring.
4. **Fler lägen.** Viktbalans och muskelbygge som nya barnklasser till `User`, samt en coachroll som kan läsa en användares analys utan att kunna ändra loggarna.
5. **Mer datainsamling och andra gränssnitt.** Automatisk inläsning av steg från telefon eller klocka, ett webbgränssnitt ovanpå samma klasser, veckorapporter och koppling till hälso- och träningsappar.

## AI-användning

Jag har använt Claude (Anthropic) som bollplank och kodassistent genom hela projektet. Idén, produktvisionen och de bärande besluten är mina. Stora delar av koden har skrivits av Claude utifrån mina beslut och krav, och jag har gått igenom, testat och lagt in den själv. Testerna i `tests/` är skrivna av Claude utifrån kraven i `docs/kravspec.md`, med förväntade värden som är uträknade för hand i kommentarerna. Claude har också förklarat koncept som var nya för mig och ifrågasatt mina val när de haft brister. Jag har gått igenom koden i `models.py` och `analysis.py` och testerna `test_models.py`, `test_analysis.py` och `test_readme_example.py` funktion för funktion och kan förklara vad varje del gör och varför den är skriven som den är. Det gäller nu också `main.py`, `test_main.py` och beroendefilerna `requirements.txt` och `requirements-dev.txt`. Sex undantag. Det första är ändringen av `days_since_start` i `models.py` (dagarna räknas från det tidigaste av profilens startdatum och första loggen) och de tio nya testerna för den i `test_models.py`, `test_readme_example.py` och `test_main.py`. Det andra är datumkontrollen: funktionen `normalize_date` i `models.py`, anropen av den i `DailyLog`, `User` och `log_today` i `main.py`, de 59 nya testerna för den i `test_models.py`, `test_main.py` och `test_analysis.py` och ett ändrat test i `test_models.py`. Det tredje är den tåligare CSV-inläsningen: konstanten `CSV_COLUMNS` och funktionerna `parse_number`, `parse_trained`, `is_empty_row` och `make_log_from_row` i `analysis.py`, den omskrivna `import_logs_csv`, de 44 nya testerna för den i `test_analysis.py`, ett test som ersattes av nya och ett som ändrades. Det fjärde är att inte tappa loggar: den nya `save_profile` i `analysis.py` (temporär fil och `os.replace`), funktionen `profile_file_exists`, de tre nya except-blocken i `load_profile` (`UnicodeDecodeError`, `TypeError` och `OSError`), att `log_today` i `main.py` returnerar `True` eller `False`, ändringarna i `run_menu` (sparning efter varje ny logg, att menyn stannar vid en profilfil som inte går att läsa och att val 6 bara avslutar när sparningen lyckades) och meddelandet i `main()`, de 40 nya testerna för det i `test_analysis.py` och `test_main.py` och två ändrade tester, ett i vardera filen. Det femte är kontrollen av inmatningen: gränserna och funktionerna `is_number` och `is_whole_number` i `models.py` och kontrollerna i `DailyLog`, `User` och `CutProfile`, att `normalize_date` tar bort mellanslag runt datumet, funktionerna `is_usable_name` och `describe_os_error` i `analysis.py`, funktionerna `to_number` och `ask_name` i `main.py` och ändringarna i `ask_number`, `create_profile`, `log_today` och `run_menu`, de 443 nya testerna för det i `test_models.py`, `test_analysis.py` och `test_main.py` och ett ändrat test i `test_analysis.py`. Det sjätte är att två namn inte delar profil: funktionen `names_match` i `analysis.py`, kontrollen av namnet i `load_profile`, det ändrade meddelandet i `run_menu` och de 16 nya testerna för det i `test_analysis.py` och `test_main.py`. Det här är skrivet men ännu inte genomgånget av mig.
