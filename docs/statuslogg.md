# Statuslogg CutTrack

## Vad "klart" betyder
Ett moment bockas av först när alla tre stämmer:
1. koden finns och körs utan fel
2. den är testad med realistisk data, och när det finns tester, av testerna
3. jag kan förklara den för en annan utvecklare utan att läsa innantill

## Nuläge, 2026-10-08
Version 1 är klar: tre klasser med arv (DailyLog, User, CutProfile), JSON för profiler och CSV för loggar, analys över valbar period med väntetid, tre diagram och en textmeny. Koden är uppdelad i models.py och analysis.py och körs från cuttrack.ipynb. Repot är publikt.

Projektet började som kursprojekt och är sedan 2026-10-08 ett portfolioprojekt. Den version som lämnades in i kursen finns bevarad i git-taggen `v1.0-course-submission`.

### Luckor mellan vision och kod
Kontrollerade mot koden 2026-10-08. Status per krav finns i kravspec.md.
- Vikttakten räknas från första och sista vägningen i perioden och delas med periodens längd, inte med antalet dagar mellan vägningarna (F24). En enskild vägning flyttar resultatet, och takten blir ungefär 14 procent för låg på sjudagarsperioden. I README-exemplet skriver programmet 1,31, 0,41 och 0,61 procent per vecka, medan jämförelse av veckosnitt ger 1,66, 1,54 och 1,12.
- Protein, steg och träning analyseras inte under väntetiden (F15). check_goals skriver väntetexten och avbryter.
- Sjudagarssnittet visas inte under dag 7 till 13, trots att väntetexten säger att det kan visas (F16).
- Midjemåttet sparas men läses inte av någon kod (F18).
- Protein- och stegdiagrammen finns i analysis.py men nås inte från menyn (F20).
- Friskrivningen visas vid start men inte vid kaloriförslaget, och ingen text säger att förslaget är en startpunkt som ska justeras (F22).
- Loggar som är äldre än profilens startdatum ger ett negativt antal dagar i väntetexten (`days_since_start`). Hittades 2026-10-08 när exempelfilen lästes in i en ny profil.
- Programmet går inte att starta utan Jupyter, menyn ligger i notebooken (N5).
- Notebookens sista cell kör `run_menu()`, och det programmet skriver ut (namn, vikter, kalorier) sparas i notebookens utdata. Provkörs menyn där med riktiga uppgifter följer de med vid nästa commit av `cuttrack.ipynb`, och repot är publikt. Löses av `main.py` (steg 0, punkt 3), förutsatt att notebooken sedan inte kör menyn. Tills dess: rensa cellens utdata före varje commit (D4).
- Det finns inga automatiska tester (N6).

### Kända småsaker
Felaktiga texter och saknade menyval. De ligger som egna punkter i roadmappen nedan, där de hänger ihop med annat arbete, så de behöver inte följas i en separat lista.

## Roadmap, i ordning

### Steg 0, grund
Görs först, så att varje senare ändring kan testas och inte behöver göras på två ställen.
- [x] Skilj exempeldata från användarens egna loggar (D4). Byggt och provkört 2026-10-08 och genomgånget samma dag. Exempelfilen ligger i `data/exempel_loggar.csv` och skrivs av notebookens exempelcell. Exporten får ett eget filnamn per användare, `<namn>_loggar.csv`: `analysis.py` har fått `make_safe_name` och `make_csv_filename`, och `export_logs_csv` och `import_logs_csv` använder det när inget filnamn anges. `.gitignore` släpper bara igenom `!data/exempel_loggar.csv`, längst ned, annars ignorerar `*.csv` även exempelfilen. `.gitattributes` har en rad för samma fil, så att git inte byter radslut och visar den som ändrad varje gång notebooken körs om. Provkört: alla 26 körbara kodceller i notebooken (utskrifterna stämmer med de sparade), menyn med skriven inmatning och ett tillfälligt git-repo (ignorering, radslut, omkörning, ny klon). Notebooken kördes sedan om på den egna datorn: exempelfilen skrevs om med samma bytes (825 byte, 21 CRLF) och git visar ren status, så `-text`-raden fungerar även utanför testrepot. Filnamnshjälparna har inga tester än, de ingår i nästa punkt
- [ ] Tester för models.py och analysis.py (N6): validering, kalenderdagsfönstret i get_logs, kaloriförslag och golv, vikttakt och väntetid, samt filhanteringen i analysis.py: make_safe_name, make_filename och make_csv_filename (F4, F8), export_logs_csv och import_logs_csv utan filnamn (F8), save_profile och load_profile (F3) och import_logs_csv med trasiga rader (F8). Skriv först ett test som låser dagens beteende i check_goals, ändra sedan takten (steg 1). pytest är ett alternativ (senaste version 9.1.1, släppt 2026-06-19, kräver Python 3.10 eller senare enligt PyPI, kontrollerat 2026-10-08), vanliga assert-satser räcker
- [ ] main.py: flytta menyn (show_welcome, ask_number, ask_period, create_profile, log_today, run_menu) från notebooken så att programmet startar med `python main.py`, och låt notebooken importera den i stället
- [ ] requirements.txt
- [ ] Välj licens. Utan licens gäller alla rättigheter förbehållna även om repot är publikt

### Steg 1, rätta takten och bygg det visionen redan beskriver
- [ ] Rätta vikttakten (F24): jämför snittet för senaste perioden med snittet för perioden före, i stället för första och sista vägningen. Kräver att get_logs kan välja en period längre bak i tiden. Avgör samtidigt om två perioder verkligen ska krävas för långa perioder, idag krävs 60 dagars data innan takten bedöms på 30 dagars period. Uppdatera README:s exempel efteråt, utskrifterna ändras
- [ ] Rätta `days_since_start` så att loggar som är äldre än profilens startdatum inte ger ett negativt antal dagar. `create_profile` ger en ny profil dagens datum som startdatum, så en CSV-import av äldre data ger väntetexten "Ett råd byggt på -1 dagars data" (reproducerat 2026-10-08 med `data/exempel_loggar.csv` i menyn). Förslag: räkna från det tidigaste av startdatumet och första loggens datum, och skriv testet först. När det är rättat kan README låta nya användare prova programmet med exempelfilen
- [ ] Analysera protein, steg och träning redan under väntetiden (F15)
- [ ] Visa sjudagarssnittet av vikten under dag 7 till 13 (F16)
- [ ] Rätta väntetexterna efter F15 och F16, så att de beskriver de nya reglerna: "1 dagar kvar" ska vara "1 dag kvar", och show_welcome säger att programmet väntar 14 dagar innan takten bedöms, men väntetiden är två perioder: 14, 28 eller 60 dagar beroende på vald period
- [ ] Friskrivning och en rad om att förslaget är en startpunkt vid kaloriförslaget, både vid profilskapande och i menyval 4 (F22)
- [ ] Låt create_profile fråga efter protein-, steg- och träningsmål (F23), så att standardvärdena inte bara kan ändras i profilens JSON-fil, och rätta frågetexten "0.5 till 1.0" så att den stämmer med vad CutProfile godtar, allt över 0 till 1,0. Samma kod som F22, därför direkt efter
- [ ] Protein- och stegdiagram i menyn (F20)
- [ ] Låt CSV-importen skriva en sammanfattning i stället för en rad per inläst logg ("Loggen för ... lades till."), som blir långt vid stora filer
- [ ] Midjejämförelse i check_goals (F18). Tröskeln för vad som räknas som oförändrad måste motiveras med källa, mätfelet på ett måttband kan vara större än den förändring man vill upptäcka
- [ ] Gå igenom notebookens förklaringstexter mot koden (N7), de är inte genomgångna sedan kursfasen. Görs sist i steget, eftersom F24 och main.py ändrar vad texterna ska säga

### Steg 2, mer räkning på redan loggad data
Visionens första block. Ordning:
- [ ] Dagar till målvikt, linjär projektion av aktuell takt. Minst data, ingen ny regel att bestämma
- [ ] Platådetektion. Kräver en regel för vad stillastående betyder och helst flera veckors verkliga data att prova den mot
- [ ] Midjemått mot vikt över hela perioden
- [ ] Korrelation mellan protein, steg, träning och viktförändring. Ger bara brus på några veckors data, bygg den sist

### Steg 3, fler lägen
- [ ] MaintenanceProfile och BulkProfile som barnklasser till User
- [ ] Coachroll som kan läsa en användares analys utan att kunna ändra loggarna

### Steg 4, datainsamling och gränssnitt
- [ ] Automatisk inläsning av steg
- [ ] Webbgränssnitt ovanpå samma klasser
- [ ] Veckorapporter och koppling till hälso- och träningsappar

## Beslut
- Träning loggas som ja eller nej (bool), inte som antal minuter.
- BMR räknas på aktuell vikt, inte startvikt.
- Proteinmålet räknas på målvikten och ligger fast genom hela deffen.
- Vikttrendens undre gräns är personens eget mål, övre gränsen är ett fast säkerhetstak på 1,0 procent per vecka.
- Kalorigolvet är det högsta av en fast gräns och personens basalomsättning, och programmet justerar aldrig tyst.
- Koden är uppdelad i models.py och analysis.py. Gränssnittet hålls separat från logiken.
- Open Food Facts byggs inte i version 1. Extern data hanteras via CSV-inläsning.
- Exempeldatan i README är simulerad och anges öppet som det.
- AI-användningen dokumenteras öppet i README.
- Kodstil: ren och underhållbar kod framför smart kod, befintliga mönster följs innan nya införs, och ny funktionalitet ska ha tester.
- 2026-10-08: CutTrack går från kursuppgift till portfolioprojekt. Kursfasens kravspec och statuslogg ersätts, den inlämnade versionen bevaras i git-taggen.
- 2026-10-08: Roadmapens ordning är grund, sedan det visionen redan beskriver, sedan visionens första block (mer räkning), arkitekturen och sist datainsamling och gränssnitt.
- 2026-10-08: De kända småsakerna är egna punkter i roadmappen, placerade där de hänger ihop med annat arbete, och inte en separat lista.
- 2026-10-08: Testerna omfattar även analysis.py (filnamn, profilfiler, CSV-inläsning), inte bara models.py, eftersom hanteringen av skadade filer och trasiga rader (N3) finns där.
- 2026-10-08: CSV-exporten får ett eget filnamn per användare, `<namn>_loggar.csv`, byggt av samma säkra namn som profilfilen. Det gemensamma namnet `cuttrack_loggar.csv` är borta, så två användares exporter skriver inte över varandra.
- 2026-10-08: Exempelfilen `data/exempel_loggar.csv` är den enda CSV-filen som checkas in. Den checkas in med programmets egna radslut (CRLF) genom `-text` i `.gitattributes`, i stället för att ändra exporten till LF. Programmets beteende ändras alltså inte för git:s skull.
- 2026-10-08: Commit-kommandon skrivs med `--trailer` för raderna `Co-Authored-By` och `Claude-Session` (kräver git 2.32 eller nyare), inte med `$'...\n...'`. `$'...'` tolkades inte av terminalen, så commit 804d0a5 och 28c860d har en trailer-rad som börjar med `$` och innehåller ett bokstavligt `\n`. De har inte skrivits om, eftersom pushad historik inte skrivs om för en kosmetisk rad.

## Källor, verifierade
Alla står med direktlänkar i README under Källor och antaganden. Nyanser att komma ihåg:
- [x] Mifflin-St Jeor 1990, formeln stämmer exakt mot koden.
- [x] 7700 kcal per kilo kroppsfett: Wishnofsky 1958 (ursprung) och Hall m.fl. 2011 (kritiken, dynamisk modell).
- [x] Takt: Garthe m.fl. 2011 rekommenderar specifikt 0,7 procent per vecka. Säkerhetstaket på 1,0 är en marginal, inte studiens resultat.
- [x] Protein: Helms m.fl. 2014 räknar per kilo fettfri massa för tävlande, inte kroppsvikt. CutTrack loggar inget kroppsfett och räknar därför på målvikt, med 1,9 g/kg hämtat ur Morton m.fl. 2018.
- [x] Kalorigolv: Jensen m.fl. 2013 (AHA/ACC/TOS) rekommenderar 1 200 till 1 500 kcal per dag för kvinnor och 1 500 till 1 800 för män, vanligen justerat efter kroppsvikt. Texten kontrollerad mot ACC och MDedge, artikelns uppgifter och DOI mot Crossref 2026-10-08. Sidnummer är inte kontrollerade och står därför inte i README. Riktlinjerna gäller personer med övervikt eller fetma.

## Senaste uppdateringar
(fylls på löpande, senaste överst)

- 2026-10-08, steg 0 punkt 1 klar: Punkten är genomgången och bockad, och kravspec D4 och F8 är satta till Klart. Allt ligger i commit 28c860d, som är pushad. Omkörningen av notebooken på den egna datorn bekräftade det som tidigare bara provats i ett tillfälligt repo: exempelfilen skrevs om med samma bytes och git visar ren status. Filnamnshjälparnas tester ingår i punkt 2, vars lista nu nämner `make_safe_name`, `make_csv_filename` och funktionerna utan filnamn. Två saker hittades vid genomgången. Dels att det menyn skriver ut sparas i notebookens utdata och kan följa med i en commit, vilket ligger som lucka under Nuläge och som förbehåll i D4. Dels att commit 804d0a5 och 28c860d har en trasig trailer-rad, se Beslut. Nästa punkt är 2, testerna.
- 2026-10-08, steg 0 punkt 1: Exempeldata och användarens egna loggar är åtskilda i koden, men punkten är inte bockad förrän den är genomgången. `analysis.py` fick `make_safe_name` och `make_csv_filename`, och exporten och inläsningen använder användarens eget filnamn när inget anges. `.gitignore` släpper bara igenom `data/exempel_loggar.csv`, `.gitattributes` fick en rad för samma fil, och notebooken följer med (fem förklaringsceller och fem kodceller: importen, CSV-testerna, exportcellen och menyval 5). Provkörningen visade två saker som inte stod i planen. Dels att git byter radslut på exempelfilen och visar den som ändrad efter varje omkörning av notebooken, vilket raden i .gitattributes förhindrar. Dels att en profil som skapas idag och läser in exempelfilen får "-1 dagars data" i väntetexten, eftersom filens datum ligger före profilens startdatum. Det senare ligger som egen punkt i steg 1 och är noterat i kravspec F14, teknisk_plan och README:s begränsningar. Kravspec D4 och F8 står kvar som Delvis tills punkten är genomgången. Små rättelser: "allt tre" blev "alla tre" under Vad klart betyder.
- 2026-10-08, senare: Roadmappen gicks igenom en gång till. De åtta kända småsakerna placerades som egna punkter i stegen och listan ersattes av en hänvisning. Steg 0 punkt 1 kompletterades: det räcker inte att ta bort undantaget `!cuttrack_loggar.csv`, eftersom `*.csv` då ignorerar även den incheckade exempelfilen (`git add` vägrade i ett tillfälligt testrepo), så raden `!data/exempel_loggar.csv` behövs. Testpunkten utökades till analysis.py, där filnamn, profilfiler och CSV-inläsning ligger (kravspec N6 följer med). README:s roadmap fick samma ordning som loggen, med midjemåttet sist i steg 1.
- 2026-10-08: Projektet går från kursuppgift till portfolioprojekt. README skrevs om: kursspecifika avsnitt (Analys, Certifikat, kursreflektionen) togs bort, Begränsningar och Roadmap tillkom, och utskrifterna i Exempel kontrollerades mot koden. Två rader med föråldrad text rättades ("planerade dagar den senaste veckan" blev "förväntade dagar under perioden"). Kravspecen ersattes av en produktkravspec med statuskolumn, produktvision och teknisk_plan rensades från kursframing och den här loggen startades om. Kontrollen mot koden visade åtta luckor mot visionen, se Nuläge. Den allvarligaste är att vikttakten räknas från första och sista vägningen, vilket gör att README-exemplets utskrifter (1,31, 0,41 och 0,61 procent per vecka) mest speglar enskilda dagars svängningar. README beskriver nu det öppet under Exempel och Begränsningar. Källan till kalorigolvet lades till i README, och en felaktig formulering rättades: README sa att kalorigolvet bygger på 7700-regeln, men det är underskottet som gör det. Dokumenten kontrollerades därefter mot själva repot: cuttrack_loggar.csv har aldrig checkats in (den skapas när notebooken körs), så påståendena om en incheckad exempelfil togs bort och D4 beskriver nu hur det faktiskt är. Notebooken i repot har inga kodkopior som markdown (de fanns bara i en äldre referenskopia), så skuldpunkten om kod på två ställen togs bort ur teknisk_plan, kravspec N7 och den här loggen.
- Kursfasen, 2026-09-15 till 2026-10-04: se git-taggen `v1.0-course-submission` och tidigare versioner av den här filen i git-historiken.
