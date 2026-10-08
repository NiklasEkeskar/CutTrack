# Statuslogg CutTrack

## Vad "klart" betyder
Ett moment bockas av först när allt tre stämmer:
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
- Programmet går inte att starta utan Jupyter, menyn ligger i notebooken (N5).
- Det finns inga automatiska tester (N6).

### Kända småsaker
- Väntetexten skriver "1 dagar kvar", ska vara "1 dag kvar".
- Frågetexten i create_profile säger "0.5 till 1.0", medan CutProfile godtar allt över 0 till 1,0.
- Med 30 dagars period krävs 60 dagars data innan takten bedöms. Avgör om två perioder verkligen ska krävas för långa perioder.
- Notebookens exempelcell och menyns export skriver båda till cuttrack_loggar.csv, som är undantaget från .gitignore. Filen finns inte i repot (den har aldrig committats), men den syns som ny fil när programmet körts, och riktiga loggar kan committas av misstag (D4).
- Välkomsttexten (show_welcome) säger att programmet väntar 14 dagar innan takten bedöms, men väntetiden är två perioder: 14, 28 eller 60 dagar beroende på vald period.
- Notebookens förklaringstexter är inte genomgångna mot koden sedan kursfasen (N7).
- Menyn frågar inte efter protein-, steg- och träningsmål. Standardvärdena kan bara ändras i profilens JSON-fil (F23).
- CSV-importen skriver en rad per inläst logg ("Loggen för ... lades till."), vilket blir långt vid stora filer.

## Roadmap, i ordning

### Steg 0, grund
Görs först, så att varje senare ändring kan testas och inte behöver göras på två ställen.
- [ ] Skilj exempeldata från användarens egna loggar: checka in en exempelfil i en egen mapp (till exempel data/exempel_loggar.csv), låt exporten få ett eget filnamn per användare och ta bort undantaget `!cuttrack_loggar.csv` ur .gitignore så att git ignorerar all export
- [ ] Tester för models.py: validering, kalenderdagsfönstret i get_logs, kaloriförslag och golv, vikttakt, väntetid. Skriv först ett test som låser dagens beteende i check_goals, ändra sedan takten (steg 1). pytest är ett alternativ (senaste version 9.1.1, släppt 2026-06-19, kräver Python 3.10 eller senare enligt PyPI, kontrollerat 2026-10-08), vanliga assert-satser räcker
- [ ] main.py: flytta menyn (show_welcome, ask_number, ask_period, create_profile, log_today, run_menu) från notebooken så att programmet startar med `python main.py`, och låt notebooken importera den i stället
- [ ] requirements.txt
- [ ] Välj licens. Utan licens gäller alla rättigheter förbehållna även om repot är publikt

### Steg 1, rätta takten och bygg det visionen redan beskriver
- [ ] Rätta vikttakten (F24): jämför snittet för senaste perioden med snittet för perioden före, i stället för första och sista vägningen. Kräver att get_logs kan välja en period längre bak i tiden. Uppdatera README:s exempel efteråt, utskrifterna ändras
- [ ] Analysera protein, steg och träning redan under väntetiden (F15)
- [ ] Visa sjudagarssnittet av vikten under dag 7 till 13 (F16)
- [ ] Friskrivning och en rad om att förslaget är en startpunkt vid kaloriförslaget, både vid profilskapande och i menyval 4 (F22)
- [ ] Protein- och stegdiagram i menyn (F20)
- [ ] Midjejämförelse i check_goals (F18). Tröskeln för vad som räknas som oförändrad måste motiveras med källa, mätfelet på ett måttband kan vara större än den förändring man vill upptäcka

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

## Källor, verifierade
Alla står med direktlänkar i README under Källor och antaganden. Nyanser att komma ihåg:
- [x] Mifflin-St Jeor 1990, formeln stämmer exakt mot koden.
- [x] 7700 kcal per kilo kroppsfett: Wishnofsky 1958 (ursprung) och Hall m.fl. 2011 (kritiken, dynamisk modell).
- [x] Takt: Garthe m.fl. 2011 rekommenderar specifikt 0,7 procent per vecka. Säkerhetstaket på 1,0 är en marginal, inte studiens resultat.
- [x] Protein: Helms m.fl. 2014 räknar per kilo fettfri massa för tävlande, inte kroppsvikt. CutTrack loggar inget kroppsfett och räknar därför på målvikt, med 1,9 g/kg hämtat ur Morton m.fl. 2018.
- [x] Kalorigolv: Jensen m.fl. 2013 (AHA/ACC/TOS) rekommenderar 1 200 till 1 500 kcal per dag för kvinnor och 1 500 till 1 800 för män, vanligen justerat efter kroppsvikt. Texten kontrollerad mot ACC och MDedge, artikelns uppgifter och DOI mot Crossref 2026-10-08. Sidnummer är inte kontrollerade och står därför inte i README. Riktlinjerna gäller personer med övervikt eller fetma.

## Senaste uppdateringar
(fylls på löpande, senaste överst)

- 2026-10-08: Projektet går från kursuppgift till portfolioprojekt. README skrevs om: kursspecifika avsnitt (Analys, Certifikat, kursreflektionen) togs bort, Begränsningar och Roadmap tillkom, och utskrifterna i Exempel kontrollerades mot koden. Två rader med föråldrad text rättades ("planerade dagar den senaste veckan" blev "förväntade dagar under perioden"). Kravspecen ersattes av en produktkravspec med statuskolumn, produktvision och teknisk_plan rensades från kursframing och den här loggen startades om. Kontrollen mot koden visade åtta luckor mot visionen, se Nuläge. Den allvarligaste är att vikttakten räknas från första och sista vägningen, vilket gör att README-exemplets utskrifter (1,31, 0,41 och 0,61 procent per vecka) mest speglar enskilda dagars svängningar. README beskriver nu det öppet under Exempel och Begränsningar. Källan till kalorigolvet lades till i README, och en felaktig formulering rättades: README sa att kalorigolvet bygger på 7700-regeln, men det är underskottet som gör det. Dokumenten kontrollerades därefter mot själva repot: cuttrack_loggar.csv har aldrig checkats in (den skapas när notebooken körs), så påståendena om en incheckad exempelfil togs bort och D4 beskriver nu hur det faktiskt är. Notebooken i repot har inga kodkopior som markdown (de fanns bara i en äldre referenskopia), så skuldpunkten om kod på två ställen togs bort ur teknisk_plan, kravspec N7 och den här loggen.
- Kursfasen, 2026-09-15 till 2026-10-04: se git-taggen `v1.0-course-submission` och tidigare versioner av den här filen i git-historiken.
