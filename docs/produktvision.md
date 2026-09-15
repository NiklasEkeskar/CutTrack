# CutTrack, produktvision

## Problem
Många som deffar har svårt att:
- tolka dagliga viktförändringar
- veta om dieten fungerar
- bedöma om protein, träning och aktivitet ligger rätt
- förstå när något behöver justeras
- skilja en verklig trend från tillfälliga svängningar i vätska och maginnehåll

Idag löser jag det här manuellt i ett Claude-projekt (GYM 101), med klipp och klistra och skärmdumpar. Det fungerar för mig men är inte begripligt för gemene man.

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
Grundkursen bygger kärnan. Kärnlogiken (klasser, beräkningar, regler) hålls separat från in- och utmatning så den går att återanvända. Senare kan projektet växa till:
- midjemått och styrkeutveckling över tid
- träningsvolym, inte bara frekvens
- personliga kost- och träningsrekommendationer
- lägen för deff, muskelbygge och viktbalans
- veckorapporter
- integration med hälso- och träningsappar
