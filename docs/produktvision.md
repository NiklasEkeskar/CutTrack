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
- träning, ja eller nej, plus antal minuter

## Vad programmet räknar ut
- genomsnittsvikt över en period
- viktförändring över perioden
- genomsnittliga kalorier
- genomsnittligt protein
- genomsnittligt antal steg
- antal träningspass
- om användaren når sina mål
- viktutveckling i diagram

## Exempel på output
"Vikten minskar, proteinmålet uppnås och träningsfrekvensen är stabil. Fortsätt enligt nuvarande plan."

## Extra funktion, om tiden räcker
Uppslag av livsmedel via Open Food Facts API, så att användaren kan slå upp protein och kalorier per 100 gram istället för att googla och skriva av för hand. Det här är den delen som direkt attackerar mitt eget klipp och klistra-problem, men det är en tilläggsfunktion, inte kärnan i betyget. Se teknisk_plan.md för detaljer och risker.

## Kopplingen till AI-branschen
Projektet behöver inte innehålla riktig AI. Kopplingen är att insamling, rengöring, analys och visualisering av data är grunden för framtida maskininlärning.

Till README, ungefär: Projektet visar hur användardata kan samlas in, struktureras och analyseras. Samma arbetsflöde kan senare användas som grund för en AI-modell som identifierar trender och ger personliga rekommendationer.

## Efter kursen
Det här är steg ett. Grundkursen bygger kärnan, kärnlogiken (klasser, beräkningar, regler) hålls separat från in- och utmatning i notebooken så den går att återanvända. Senare kan projektet växa till en större AI-baserad träningscoach med:
- sjudagarstrender
- midjemått och styrkeutveckling
- personliga kost- och träningsrekommendationer
- lägen för deff, muskelbygge och viktbalans
- veckorapporter från AI
- integration med hälso- och träningsappar
