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
