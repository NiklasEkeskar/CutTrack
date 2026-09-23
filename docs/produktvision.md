# CutTrack, produktvision

## Problem
Många som deffar har svårt att:
- tolka dagliga viktförändringar
- veta om dieten fungerar
- bedöma om protein, träning och aktivitet ligger rätt
- förstå när något behöver justeras
- skilja en verklig trend från tillfälliga svängningar i vätska och maginnehåll

Idag löser jag det här manuellt, med klipp och klistra och skärmdumpar. Det fungerar för mig men är inte begripligt för gemene man.

## Målgrupp
Andra personer som vill deffa och behålla muskelmassa, inte bara jag själv. Varje person ska kunna skapa sin egen profil i programmet.

## Vad användaren loggar per dag
- datum
- vikt
- kalorier
- protein
- antal steg
- träning, ja eller nej
- midjemått (valfritt, mäts typiskt en gång i veckan)

## Vad programmet gör
- räknar ut ett kaloriförslag utifrån profilen, så användaren slipper gissa
- räknar rullande sjudagarssnitt på vikten
- bedömer viktnedgångens takt som procent av kroppsvikt per vecka
- jämför midjemått mot vikt för att säga något om vad som faktiskt försvinner
- räknar snitt på kalorier, protein och steg samt antal träningsdagar
- visar viktutvecklingen i ett diagram
- ger en statusöversikt plus en sak att fokusera på

## Varför midjemått
Vikt ensam kan inte skilja fettförlust från muskelförlust. Två personer som tappar ett kilo i veckan ser identiska ut i datan, oavsett vad kilot bestod av. Midjan krymper när fett försvinner men i princip inte när muskler gör det. Vikt ner plus midja ner pekar mot fettförlust. Vikt ner plus midja oförändrad är en varningssignal. Det är en proxy, inte en mätning, men det är det bästa som går att få utan mätverktyg.

## Varför träning loggas som ja eller nej
Det som bevarar muskelmassa under en deff är att stimulansen finns kvar regelbundet, inte hur länge varje pass varar. Ett långt pass med mycket vila ger inte mer signal än ett kort och fokuserat. Frekvens går dessutom att bedöma mot en tydlig regel, antal dagar per vecka, medan minuter kräver ett godtyckligt tröskelvärde.

## Programmet väntar innan det ger råd
Dagliga viktsvängningar från vätska och maginnehåll ligger ofta på flera hundra gram, vilket är mer än en hel veckas verklig fettförlust. Ett råd byggt på tre dagars data är brus.

- dag 1 till 6: ingen trendanalys, programmet förklarar varför och visar hur många dagar som återstår
- dag 7 till 13: sjudagarssnitt visas, men takten kan inte bedömas än
- från dag 14: full analys

Protein, steg och träning analyseras direkt, de kräver bara ett snitt och ingen trend.

## Prioritering av råden
Programmet visar status på alla områden och lyfter sedan fram en sak att fokusera på. Ordning:
1. vikten går åt fel håll eller för snabbt
2. proteinet under målet
3. träningsfrekvensen
4. stegen

## Exempel på output
"Vikten minskar med 0,6 procent per vecka, vilket ligger i rätt intervall. Proteinmålet nås fem av sju dagar och träningsfrekvensen är stabil. Fokusera på stegen, snittet ligger under ditt mål."

## Ansvarsfriskrivning
Programmet ger allmänna riktvärden baserade på etablerade rekommendationer. Det är inte medicinsk rådgivning. Texten visas i README, vid skapande av ny profil och i samband med kaloriberäkningen.

## Extra funktion, om tiden räcker
Uppslag av livsmedel via Open Food Facts API, så att användaren kan slå upp protein och kalorier per 100 gram istället för att googla och skriva av för hand. Tilläggsfunktion, inte kärnan i betyget. Se teknisk_plan.md.

## Kopplingen till AI-branschen
Projektet behöver inte innehålla riktig AI. Kopplingen är att insamling, rengöring, analys och visualisering av data är grunden för framtida maskininlärning.

Till README, ungefär: Projektet visar hur användardata kan samlas in, struktureras och analyseras. Samma arbetsflöde kan senare användas som grund för en AI-modell som identifierar trender och ger personliga rekommendationer.

## Efter kursen
Grundkursen bygger kärnan. Kärnlogiken (klasser, beräkningar, regler) hålls separat från in- och utmatning så den går att återanvända, och är nu uppdelad i models.py och analysis.py, redo att importeras av andra gränssnitt. Senare kan projektet växa till:

**Mer räkning på redan loggad data, ingen ny datainsamling:**
- platådetektion, jämför flera sjudagarssnitt i rad för att upptäcka att vikten stått still trots rätt underskott, den vanligaste frustrationen vid en deff
- dagar-till-mål, en enkel linjär projektion av aktuell takt mot goal_weight. Konkret exempel på var CutTracks regelbaserade logik slutar och statistisk prognos börjar, samma typ av trendförlängning som ligger till grund för tidsserieprognoser inom AI
- korrelation mellan protein, steg, träning och viktförändring vecka för vecka, ett naturligt försteg till feature-tänk inom maskininlärning utan att bygga någon modell
- midjemått jämfört med vikt över hela perioden, inte bara senaste mätningen, en starkare varningssignal om de två divergerar över flera veckor

**Arkitekturen, redan förberedd men inte byggd:**
- lägen för deff, muskelbygge och viktbalans, byggda som nya barnklasser till User (BulkProfile med kaloriöverskott, MaintenanceProfile utan viktmål) utan att koden i User behöver ändras
- en roll för coach eller PT, en klass som kan läsa en användares check_goals-utskrift utan att äga eller kunna ändra loggarna

**Mer datainsamling och annat gränssnitt:**
- automatisk inläsning av steg från telefon eller klocka, löser den svagaste länken i datainsamlingen, att manuell inmatning av steg är trögt och lätt att sluta med
- ett enkelt webbgränssnitt ovanpå samma User- och CutProfile-klasser, möjligt just för att input och output redan hålls separat från kärnlogiken
- veckorapporter, integration med hälso- och träningsappar