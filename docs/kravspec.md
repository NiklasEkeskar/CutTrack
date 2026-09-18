# Kravspec (från examinationsbeskrivningen och kursplanen)

## Två separata examinationer
Kursen examineras i två helt separata delar, med egna beskrivningar och eget innehåll. De har inget med varandra att göra. Båda ska genomföras, även av den som examineras på annat datum än det ordinarie.

**1. Teoretisk examination.** Testar kursens allmänna innehåll, inte CutTrack. Onlinequiz vid de ordinarie tillfällena 28 och 30 september, upplagt ungefär som quizen efter varje lektion men längre och mer omfattande. 40 frågor, minst 10 rätt krävs. Jag tillhör grupp 1, quiz **28 september**. Den som examineras på annat datum gör i stället en muntlig teoriexamination med 3 till 5 öppna frågor utan svarsalternativ, max 10 minuter. Frågor om material som inte hunnits gå igenom, bland annat lektion 14 (Databricks) och 15 (Multi-Agent System), kan påpekas under quizet och exkluderas då från bedömningen.

**2. Praktisk examination.** Individuellt projektarbete med muntlig redovisning, max 10 minuter. Examinerar mål 1 till 8. Jag ska presentera både kod och README-analysen, inte bara koden.

## Deadlines
- Teoriprov: **28 september** (grupp 1)
- Projektinlämning: sker **före** redovisningen, gäller även vid tidigare redovisningstillfälle
- Inlämning sker på två ställen med samma deadline: zip-fil på lärarplattformen och repo på GitHub
- Redovisning: ordinarie tillfälle, eller tidigare efter överenskommelse via Discord i god tid

## Inlämning
Tre filer, samlade i en enda .zip, samt samma filer i GitHub-repot.
1. **Jupyter Notebook (.ipynb)** med hela projektets kod och tydliga markdown-celler som förklarar logiken
2. **Datafil (.csv eller .json)** med data programmet hämtat, sparat eller analyserat under körning
3. **README (.md eller .pdf)** med mål, metod, branschanalys, certifikat och reflektion

Filnamn på zip: projekt_python_fornamn_efternamn.zip

## Obligatoriska tekniska delar
| Område | Vad som förväntas |
| --- | --- |
| Variabler och datatyper | int, float, str, bool, listor, dict |
| If-satser | Villkor och beslut |
| Loopar | Minst en for- eller while-loop |
| Funktioner | Minst 3 till 5 egna funktioner med parametrar och returvärden |
| Felhantering | try/except där det är rimligt (API-anrop, filhantering) |
| Datahantering | Läsa eller spara data i JSON eller CSV, denna fil lämnas in |
| Klasser | Minst en klass med attribut och metoder |
| Arv | Minst en barnklass som ärver från basklass |
| Standardbibliotek | json, csv, random, datetime, os, math |
| Externt bibliotek | requests, matplotlib, beautifulsoup4 |
| API eller extern data | Hämta data från ett offentligt API eller läsa från extern fil |
| GitHub | Repository med projektet, länk i README |
| Versionshantering | Minst 5 commits med tydliga meddelanden |

## README ska innehålla
| Avsnitt | Innehåll |
| --- | --- |
| Titel | Projektets namn |
| Mål | Vad projektet ska lösa, kopplat till verkligheten och AI-utvecklarrollen |
| Metod | Hur målet nåddes, vilka tekniska delar som användes (API, klasser, bibliotek) |
| Resultat | Vad blev resultatet, med exempel på utskrifter eller data |
| Analys | Tolkning av resultatet, vad betyder det för AI-utvecklarrollen och branschen. Mål 1 kräver analys av **bransch, yrkesroller och trender** |
| Certifikat | Kort redogörelse för yrkescertifikat relevanta för rollen, till exempel AWS, Azure eller Databricks (mål 5) |
| Reflektion | Vad gick bra, vad var svårt, vad skulle jag göra annorlunda (mål 8) |
| GitHub-länk | Länk till repot, ska anges tydligt |
| Installation | Hur man kör projektet |
| **AI-användning** | **AI-genererad kod ska dokumenteras och förklaras i README (Del 12)** |

## Regler kring AI-verktyg (Del 12)
- AI får användas som stöd för idéer, felsökning och kodgenerering
- **Viktigaste regeln: jag måste förstå ALL kod som lämnas in**
- Personuppgifter (PII) får aldrig skickas till AI-verktyg
- **AI-genererad kod ska dokumenteras och förklaras i README**
- Inte tillåtet: lämna in kod jag inte kan förklara under redovisningen
- Konsekvens om jag inte kan förklara koden: betyg IG
- Plagiat, kopiering utan egna ändringar och förståelse, är förbjudet

## Vid redovisningen
- Max 10 minuter, individuellt
- Presentera både kod och README-analysen
- Ta med en fungerande dator, fulladdad, uppdaterad, med internetanslutning. Kontrollera i förväg att projektet och alla program fungerar
- Kunna förklara all inlämnad kod och sina designval
- **Kunna göra mindre ändringar i koden på egen hand under redovisningen**
- Kommentarer i koden rekommenderas av läraren som stöd vid förklaringen

## Vad som INTE krävs
Avancerad matematik, avancerade AI-modeller (neurala nätverk), avancerad databashantering, stora komplexa system, professionell frontend eller webbdesign.

Kursplanens egen formulering: gör inte projektet överkomplicerat, det räcker gott att använda grundläggande moment i Python. En enkel men fungerande lösning som jag förstår är alltid bättre än en avancerad lösning som jag inte kan förklara.

## Betygskriterier
| Betyg | Beskrivning | Huvudkrav |
| --- | --- | --- |
| IG | Når inte alla kursmål eller kan inte förklara sin lösning | Saknar obligatoriska moment ELLER förstår inte sin egen kod |
| G | Når kursmålen och visar grundläggande förståelse | Alla obligatoriska delar finns (klasser, arv, API, GitHub, README med certifikat-redogörelse) |
| VG | Visar god struktur, självständighet och säkerhet i sina lösningar | Allt för G plus tydlig kodstruktur (mål 6), bra felhantering, djup reflektion (mål 8), extra funktionalitet, 10+ commits |

### VG-kriterier i detalj
- **Kodstruktur:** uppdelad i flera moduler, exempelvis api_handler.py, analyzer.py
- **Namngivning:** konsekvent, självförklarande funktions- och variabelnamn enligt PEP 8
- **Felhantering:** specifika felmeddelanden för API-fel, nätverksproblem och filhantering via try/except
- **Visualisering:** avancerade matplotlib-diagram som är integrerade i lösningen och förklaras i texten
- **Reflektion:** djupgående reflektion över tekniska val och hur resultatet speglar aktuella AI-trender
- **Certifikat:** analys av vilka yrkescertifikat som är relevanta för projektets teknikstack
- **GitHub:** 15+ commits med tydlig struktur och beskrivande meddelanden
- **Självständighet:** extra funktionalitet utöver minimikraven

## Checklista inför inlämning
- [ ] Notebook, datafil och README finns
- [ ] Alla filer samlade i en enda .zip
- [ ] Programmet körs utan kritiska fel
- [ ] Minst en klass med arv används
- [ ] try/except används för API-anrop eller filinläsning
- [ ] Både standardbibliotek och externa bibliotek används
- [ ] Repot har minst 5 commits med tydliga meddelanden
- [ ] README innehåller analys kopplad till yrkesroller och trender i AI-branschen
- [ ] README innehåller kort redogörelse för relevanta certifikat
- [ ] README innehåller djupgående reflektion över tekniska val och resultat
- [ ] README innehåller AI-användningen dokumenterad och förklarad
- [ ] Giltig GitHub-länk tydligt angiven i README
- [ ] Jag är förberedd på att förklara all kod och mina designval muntligt
- [ ] Jag är förberedd på att göra mindre ändringar i koden live

## Viktigaste enskilda risken
Att inte kunna förklara egen eller AI-genererad kod under redovisningen ger automatiskt IG. Kursplanen säger det rakt ut: studenten måste förstå ALL kod som lämnas in. Med det skärpta kravet på att kunna ändra koden live räcker det inte att känna igen den, jag ska veta var varje del ligger och kunna redigera den utan hjälp.
