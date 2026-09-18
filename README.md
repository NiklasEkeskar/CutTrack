# CutTrack

## Mål

CutTrack är ett verktyg för personer som deffar, alltså bantar med målet att tappa fett men behålla muskelmassa, och som vill följa sin utveckling utan att gissa. Problemet CutTrack löser är att en enskild vägning inte säger något pålitligt: vikten svänger flera hundra gram från dag till dag på grund av vätska och maginnehåll, mer än en hel veckas verkliga fettförlust. Utan ett sätt att skilja brus från trend blir varje dags siffra lika mycket värd som nästa, vilket gör det svårt att veta om dieten faktiskt fungerar.

Programmet löser det genom att låta användaren logga vikt, kalorier, protein, steg, träning och (valfritt) midjemått dagligen, och genom att vänta med att dra slutsatser tills det finns tillräckligt med data. Det räknar ut ett personligt kaloriförslag, bedömer om viktnedgången håller rätt takt, och ger en prioriterad rekommendation utifrån vad som faktiskt avviker mest, vikt, protein, träningsfrekvens eller steg.

Kopplingen till AI-utvecklarrollen ligger inte i att programmet innehåller AI, utan i att det bygger den typ av strukturerad, validerad data som en framtida maskininlärningsmodell skulle behöva för att göra samma bedömning automatiskt. Se avsnittet Analys för ett utvecklat resonemang om det.

## Metod

CutTrack är byggt i en enda Jupyter Notebook, med tre klasser och elva fristående funktioner.

**Klasser och arv:** `DailyLog` representerar en enskild dags logg och validerar vikt och kalorier vid skapandet. `User` är basklassen med en persons grunddata och metoderna som räknar på loggarna (medelvärden, viktförändring, träningsfrekvens). `CutProfile` ärver från `User` med `super().__init__()` och lägger till mål, kaloriberäkningar (Mifflin-St Jeor) och den regelbaserade analysen i `check_goals`.

**Datahantering:** Profilen sparas och läses som JSON (`save_profile`, `load_profile`), med filnamnet byggt säkert från användarnamnet i `make_filename`. Loggarna exporteras och kan läsas in som CSV (`export_logs_csv`, `import_logs_csv`), vilket är den datafil som lämnas in vid examination.

**Felhantering:** try/except används genomgående, bland annat tre skilda except-block i `load_profile` för trasig JSON, saknade fält och ogiltiga värden, samt try/except inne i importloopen i `import_logs_csv` så att en trasig rad i en CSV-fil inte stoppar resten av importen.

**Bibliotek:** Standardbiblioteken `json`, `csv`, `datetime` och `os`. Externa biblioteket `matplotlib` för viktdiagrammet, som visar både daglig vikt och ett rullande sjudagarssnitt.

**Gränssnitt:** En textbaserad meny (`run_menu`) med sex val: logga dagens data, visa analys, visa diagram, visa kaloriförslag, läsa in loggar från CSV, samt spara och avsluta. All inmatning och utskrift hålls i egna funktioner, separat från klasserna, så att logiken går att återanvända om gränssnittet byts ut senare.

## Resultat

Nedan visas CutTracks utskrifter från en testperiod på 20 dagar, med en profil och datamängd konstruerad för att spegla min egen verkliga rutin (längd 189 cm, ålder 39, startvikt 101,5 kg, målvikt 98 kg, kalorier, proteinintervall, stegintervall och träningsfrekvens), men där siffrorna är simulerade och inte en logg förd dag för dag.

**Efter 14 dagar, första gången full analys är möjlig:**
```
Vikten: minskar med 1.31 procent per vecka, över säkerhetsgränsen 1,0 procent. Risk för muskelförlust.
Protein: snitt 211 g mot mål 206 g. Målet nås.
Träning: 5 av 5 planerade dagar den senaste veckan. Målet nås.
Steg: snitt 10160 mot mål 10000. Målet nås.

Fokusera på: vikt.
```

**Efter 18 dagar, takten har hunnit sakta in:**
```
Vikten: minskar med 0.41 procent per vecka, långsammare än ditt mål på 0.6 procent.
```

**Efter 20 dagar, vikten har hittat rätt takt och är nära målvikten, stegen har istället blivit det som avviker:**
```
Vikten: minskar med 0.61 procent per vecka, vid eller över ditt mål på 0.6 procent och inom säkerhetsgränsen.
Protein: snitt 213 g mot mål 206 g. Målet nås.
Träning: 5 av 5 planerade dagar den senaste veckan. Målet nås.
Steg: snitt 9953 mot mål 10000. Under målet.

Fokusera på: steg.
```

Programmets kaloriförslag för samma profil blev 2409 kcal per dag. Det faktiska intaget i datan låg på 2300 kcal, något under förslaget, vilket är en bidragande orsak till att takten periodvis låg över säkerhetsgränsen tidigt i perioden.

Midjemåttet minskade från 90,0 till 88,2 cm under perioden, vilket enligt produktvisionens resonemang stärker bilden av att det är fett snarare än muskelmassa som gått ner.

![Viktutveckling](resultat_diagram.png)

## Analys – yrkesroller, verksamheter och trender

CutTrack löser i grunden ett dataproblem. Enskilda vägningar påverkas av exempelvis vätska och ger därför begränsad information. Programmet samlar i stället in data konsekvent, kontrollerar att värdena är rimliga, lagrar dem strukturerat och analyserar utvecklingen över tid. Genom att använda tydliga datatyper och skilja saknade värden från nollor minskar risken för missvisande resultat.

Detta motsvarar de första stegen i ett dataflöde inom AI och maskininlärning. CutTrack är i nuläget regelbaserat: jag bestämmer exempelvis hur ett veckosnitt beräknas och att viktnedgången inte bör överstiga 1,0 procent per vecka. En framtida ML-modell skulle i stället kunna tränas på historiska data för att identifiera samband mellan vikt, kaloriintag, protein och träningsfrekvens. Det skulle dock kräva betydligt fler observationer, relevanta variabler och testdata för att resultatet skulle bli tillförlitligt.

Projektet berör flera yrkesroller inom AI- och dataområdet. En data engineer arbetar med insamling, lagring och kvalitetssäkring av data. En data scientist analyserar information och utvecklar modeller, medan en AI- eller ML-engineer tränar, utvärderar och driftsätter dem. Systemutvecklare integrerar sedan funktionerna i en användbar tjänst. I CutTrack arbetar jag främst med delar som är gemensamma för data engineering och systemutveckling: datainsamling, validering, lagring och regelbaserad analys.

Liknande dataflöden används inom healthtech, träningsappar och andra datadrivna verksamheter. Om CutTrack utvecklades till en kommersiell AI-tjänst skulle även integritet, informationssäkerhet, samtycke och ansvarsfull hantering av personuppgifter behöva ingå.

Behovet av denna kompetens ökar. Enligt SCB använde 35 procent av svenska företag med minst tio anställda AI under 2025, jämfört med cirka 25 procent 2024. Sverige låg därmed över EU-genomsnittet på omkring 20 procent. AI-användningen var samtidigt betydligt högre bland stora företag, vilket tyder på att tillgång till resurser, kompetens och fungerande datahantering har betydelse för möjligheten att införa AI.

CutTrack innehåller ännu ingen AI-modell, men projektet visar en central del av AI-utvecklarens arbete: att omvandla rå information till tillförlitlig och återanvändbar data som kan ligga till grund för analys, beslutsstöd och framtida maskininlärning.

**Källor**
- SCB – It-användning i företag 2025
- SCB – Artificiell intelligens i Sverige 2025

## Certifikat

Ett naturligt första certifikat efter den här kursen är **AI-901, Microsoft Azure AI Fundamentals**. Det är Microsofts nybörjarcertifiering för AI på Azure, ingen förkunskap krävs. Notera att AI-901 ersatte det tidigare AI-900 den 30 juni 2026, det gamla provet går inte längre att boka. Skillnaden är att AI-901 lutar mer åt praktisk implementation, med Python, REST-API:er, SDK:er och Microsoft Foundry, jämfört med AI-900 som mest var konceptuellt. Det passar bra ihop med den här kursen, eftersom AI-901 faktiskt förutsätter grundläggande Python-kunskap, vilket den här kursen ger. Kostnad omkring 99 USD, prissatt per land.

Ett rimligt nästa steg efter det är **AI-103, Azure AI Apps and Agents Developer Associate**, som ersatte det tidigare AI-102 samma datum. Den kräver mer utvecklingserfarenhet och fokuserar på att bygga AI-appar och agenter i Azure, snarare än bara att beskriva vad tjänsterna gör. Kostnad omkring 165 USD.

Ingen av de här är tagen ännu, det här är en kort redogörelse för vad som är relevant, inte en bekräftelse på avklarad certifiering.

## Reflektion

Det jag uppskattade mest var arbetssättet. Jag planerade och skissade lösningen innan jag började skriva kod, byggde en del i taget och testade varje funktion innan jag gick vidare. Det gjorde projektet lättare att förstå och minskade risken för att fel skulle följa med till senare delar. Jag fick också bättre kontroll över koden än om jag hade försökt bygga hela notebooken på en gång.

Den största tekniska utmaningen var metoden `get_logs` i klassen `User`. Metoden väljer vilka loggar som ska ingå i ett genomsnitt eller en trend utifrån kalenderdagar räknade bakåt från det senast registrerade datumet. Den hämtar alltså inte bara de senaste raderna i listan. Det är viktigt eftersom användaren kan ha missat att registrera vissa dagar. Samma metod används sedan av beräkningar för bland annat medelvikt, viktförändring och träningsfrekvens. När jag förstod `get_logs` blev därför även resten av `User`-klassen lättare att följa. Jag såg också fördelen med att samla filtreringen på ett ställe i stället för att upprepa samma logik i flera metoder.

Om jag gjorde om projektet skulle jag bestämma fil- och mappstrukturen redan från början. Under arbetet skapades dubbla mappar och vissa filer hamnade både i docs och i projektroten. Det kostade en hel kväll att reda ut och gjorde det svårare att veta vilken version som var aktuell. Nästa gång skulle jag tidigt skilja på exempelvis kod, data, dokumentation och tester. Den viktigaste lärdomen är därför att en tydlig struktur runt koden är lika viktig som att själva koden fungerar.

## GitHub

https://github.com/NiklasEkeskar/CutTrack

## Installation

1. Klona repot: `git clone https://github.com/NiklasEkeskar/CutTrack.git`
2. Öppna mappen i VS Code eller Jupyter.
3. Skapa och aktivera en virtuell miljö (rekommenderas):
   ```
   python -m venv .venv
   ```
   Aktivera den enligt din plattform, i VS Code väljs den automatiskt som kernel.
4. Installera det externa biblioteket:
   ```
   python -m pip install matplotlib
   ```
5. Öppna `cuttrack.ipynb` och kör cellerna i ordning, uppifrån och ner (eller Run All).
6. Den sista cellen startar menyn och väntar på inmatning i notebooken.

## AI-användning

Jag har använt Claude som bollplank och studiecoach genom hela projektet. Idén, produktvisionen och de bärande besluten är mina. AI:n har bidragit med förslag och invändningar, men riktlinjerna för hur programmet skulle utformas har vi arbetat fram gemensamt utifrån mina beslut.

Konkret har AI:n skrivit kodförslag som jag gått igenom, testat och lagt in i notebooken, förklarat koncept som varit nya för mig, och ifrågasatt mina val när de haft brister.

Under arbetets gång har vi gått igenom koden funktion för funktion, där jag förklarat vad varje del gör och varför den är skriven som den är. Det som återstod att förstå har vi repeterat tills det satt.
# CutTrack

Ett Python-verktyg för dig som deffar och vill följa din viktnedgång utan att tappa muskelmassa. Du loggar vikt, kalorier, protein, steg och träning varje dag. Programmet räknar ut medelvärden och trender och ger enkla, regelbaserade råd om hur du ligger till mot dina mål.

Skolprojekt i kursen Utveckling med Python, grund, på Jensen Education.

## Status
Under utveckling.

## Mål

Den som deffar har svårt att veta om det går åt rätt håll. Vikten svänger flera hundra gram om dagen på grund av vätska och maginnehåll, vilket ofta är mer än en hel veckas verklig fettförlust. Det gör att enskilda vägningar säger nästan ingenting, och att man lätt drar fel slutsats och ändrar något som egentligen fungerade.

Samtidigt räcker det inte att bara gå ner i vikt. Går det för snabbt kommer en större del av förlusten från muskler istället för fett. Då sjunker vikten på pappret medan resultatet blir sämre än tänkt.

CutTrack ska lösa tre saker:

1. Räkna ut ett kaloriförslag utifrån användarens profil, så att den som inte vet var man börjar ändå kommer igång.
2. Jämna ut de dagliga svängningarna med rullande medelvärden och bedöma takten på viktnedgången, inte bara riktningen.
3. Ge tydliga, regelbaserade råd om vad som bör justeras, en sak i taget.

Programmet är byggt för att andra än utvecklaren ska kunna använda det. Varje användare skapar sin egen profil och loggar sin egen data.

### Koppling till AI-utvecklarrollen

Projektet innehåller ingen maskininlärning. Kopplingen ligger i arbetsflödet: samla in data, strukturera den, hantera saknade värden, räkna ut mått över tidsfönster och presentera resultatet. Det är samma steg som föregår varje AI-modell, och i praktiken den del av arbetet som tar mest tid. En modell som ska ge personliga rekommendationer skulle utgå från exakt den datastruktur som byggs här.

## Metod

### Klasser och arv
Programmet är uppbyggt kring tre klasser. `User` är basklass med användarens grunddata och loggar. `CutProfile` ärver från `User` och lägger till mål och beräkningar. `DailyLog` representerar en dags loggning.

### Kaloriberäkning
Basalomsättningen räknas med Mifflin-St Jeor-ekvationen, som bygger på vikt, längd, ålder och kön. Den valdes för att den i jämförande studier träffar närmare uppmätt basalomsättning än äldre formler som Harris-Benedict. Resultatet multipliceras med en aktivitetsfaktor mellan 1,2 och 1,9 för att uppskatta det dagliga behovet.

Underskottet räknas därefter med tumregeln att ett kilo kroppsfett motsvarar ungefär 7700 kalorier.

**Den regeln har kända brister, och det är ett medvetet val att ändå använda den.** Regeln går tillbaka till en beräkning från 1958 och förutsätter att energiunderskottet är konstant över tid. Det stämmer inte. När vikten sjunker minskar också förbrukningen, så samma underskott ger gradvis mindre effekt. Forskning visar att regeln därför överskattar hur mycket någon faktiskt går ner. Alternativet är dynamiska modeller som är betydligt mer komplexa.

För det här projektet väger enkelhet och förklarbarhet tyngre än precision. Programmet presenterar därför siffran som en startpunkt, inte ett facit, och uppmanar användaren att justera efter vad vägningarna faktiskt visar efter två veckor. Användarens egen data slår formeln så snart den finns.

### Takt på viktnedgången
Takten bedöms som procent av kroppsvikt per vecka, inte i kilo, så att samma gränser fungerar oavsett kroppsstorlek. Intervallet 0,5 till 1,0 procent per vecka används som riktvärde för att bevara muskelmassa.

Stödet för det intervallet kommer bland annat från Garthe med flera (2011), som jämförde en långsam nedgång på 0,7 procent per vecka mot en snabb på 1,4 procent hos elitidrottare med styrketräning. Den långsamma gruppen ökade sin fettfria massa, medan den snabba gruppen låg oförändrad.

### Proteinmål
Proteinmålet räknas mot målvikten och inte mot nuvarande vikt, så att målet ligger fast genom hela perioden. Skälet är att proteinbehovet för att behålla muskler inte minskar bara för att fett har försvunnit. Målvikt ligger dessutom närmare fettfri massa än nuvarande vikt gör.

Utgångspunkten är 1,9 gram per kilo. Helms med flera (2014) anger 2,3 till 3,1 gram per kilo fettfri massa för energibegränsade styrketränande, skalat uppåt med hur hård restriktionen är. Eftersom fettfri massa inte mäts i det här programmet används det lägre värdet mot målvikt istället.

### Tidsfönster och saknade värden
Medelvärden räknas över de senaste sju kalenderdagarna, inte över de sju senaste loggarna. Trend handlar om tid, och sju loggar utspridda över en månad är inte ett veckosnitt. Minst fyra loggar krävs inom fönstret för att snittet ska användas.

Programmet ger ingen trendanalys de första sex dagarna, utan förklarar istället varför det väntar. Att avstå från ett svagt underbyggt svar är ett designval, inte en brist.

Midjemåttet är valfritt och kan saknas. Det hanteras med `None` och kontrolleras med `is not None`, eftersom noll och `None` annars behandlas lika i ett vanligt villkor.

### Datalagring
Profil och loggar sparas som JSON. Loggarna exporteras även till CSV. Filhantering och API-anrop skyddas med try/except.

## Ansvarsfriskrivning

CutTrack ger allmänna riktvärden baserade på etablerade rekommendationer. Det är inte medicinsk rådgivning och ersätter inte kontakt med läkare eller dietist. Har du en sjukdom, äter medicin eller är osäker, prata med vården innan du ändrar kost eller träning.
