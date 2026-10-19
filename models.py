"""Klasserna som utgör CutTracks datamodell: DailyLog, User och CutProfile, funktionen
normalize_date som kontrollerar och skriver om datum, och gränserna för vad som räknas som
rimliga värden.
Importeras i cuttrack_referens.ipynb med: from models import DailyLog, User, CutProfile"""
import math
from datetime import datetime, timedelta

# Gränser för vad som räknas som rimliga värden. De fångar tangentfel (825 i stället för 82.5,
# en nolla för mycket i stegen) och är inga hälsoråd: ett värde inom gränsen är inte därmed
# bra för kroppen. Klasserna kontrollerar dem, så de gäller lika för menyn, för CSV-filer och
# för profilfiler. Menyn använder gränserna för längd, ålder och namn för att fråga om direkt.
MAX_WEIGHT_KG = 300
MAX_CALORIES = 10000
MAX_PROTEIN_G = 1000
MAX_STEPS = 100000
MIN_WAIST_CM = 30
MAX_WAIST_CM = 250
MIN_HEIGHT_CM = 100
MAX_HEIGHT_CM = 250
# 18 år är undre gräns eftersom riktlinjerna som kaloriförslaget bygger på gäller vuxna (se README)
MIN_AGE = 18
MAX_AGE = 100
MIN_ACTIVITY_LEVEL = 1.0
MAX_ACTIVITY_LEVEL = 2.5
MAX_PROTEIN_PER_KG = 5
MAX_TRAINING_DAYS = 7
MAX_NAME_LENGTH = 50

# Standardvärden för målen, när användaren inte anger egna (F23)
DEFAULT_PROTEIN_PER_KG = 1.9
DEFAULT_STEP_GOAL = 8000
DEFAULT_TRAINING_DAYS = 3
MIN_MENU_PROTEIN_PER_KG = 0.5

# Midjemåttet jämförs med vikten (F18). Menyn ber om medelvärdet av tre mätningar per tillfälle,
# och en förändring måste vara minst 3,1 cm för att räknas. Gränsen kommer från mätfelet vid
# självmätning: Barrios m.fl. 2016 (BMC Medical Research Methodology 16:49) fann technical error
# of measurement 0,76 tum, ungefär 1,93 cm, för en enda mätning. Medelvärdet av tre mätningar
# har felet 1,93 delat med roten ur 3, och skillnaden mellan två sådana medelvärden har roten
# ur 2 gånger det. Gränsen är 1,96 gånger det, ungefär 3,1 cm, med 95 procent. Det är en
# nedre gräns, eftersom dubbelmätningarna i studien gjordes samma dag. Att räkna med TEM som
# standardavvikelse är en egen härledning, under antagandet att felen är oberoende. En
# viktnedgång under 1 kg räknas inte, eftersom vikten svänger flera hundra gram från dag till
# dag. Vikten jämförs som medelvärde av vägningarna inom WEIGHT_AROUND_WAIST_DAYS dagar före och
# efter varje midjemätning, så att en enstaka vägning inte avgör. Tre tillfällen med minst 14
# dagar mellan första och sista är egna val, inte siffror från studien.
WAIST_CHANGE_CM = 3.1
WAIST_MIN_MEASUREMENTS = 3
WEIGHT_CHANGE_KG = 1.0
WAIST_MIN_DAYS = 14
WEIGHT_AROUND_WAIST_DAYS = 3

# Vågens dagsvariation (beslut 2026-10-12). Preliminära värden, provade mot en enda riktig
# deff på 34 vägningar under åtta veckor, ingen källa. Där avvek dagsvikten i snitt cirka 0,5 kg
# från en rak linje, och bruset i takten blev cirka 0,4 kg per vecka med sjudagarsperioden och
# cirka 0,13 med fjortondagarsperioden (en standardavvikelse). UNCHANGED_RATE_KG är ungefär
# två sådana standardavvikelser med 14 dagar: en mindre skillnad går inte att skilja från
# vågens variation. Med färre än MIN_WEIGHINGS_PER_PERIOD vägningar jämförs i praktiken enstaka
# dagar.
MIN_WEIGHINGS_PER_PERIOD = 3
UNCHANGED_RATE_KG = 0.25

DATE_MESSAGE = "Datumet måste skrivas som ÅÅÅÅ-MM-DD, till exempel 2026-10-08."


def is_number(value):
    """True om value är ett vanligt tal, int eller float, men inte nan. True och False räknas
    inte som tal: bool är en sorts int i Python, så True skulle annars vara talet 1."""
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    # nan kontrolleras bara för decimaltal. math.isnan kastar OverflowError för ett heltal som
    # är för stort för att bli ett decimaltal, och det kan stå i en JSON-fil.
    if isinstance(value, float):
        return not math.isnan(value)
    return False


def days_left_text(count):
    """"1 dag kvar" eller "4 dagar kvar", med rätt böjning av dag."""
    if count == 1:
        return "1 dag kvar"
    return f"{count} dagar kvar"


def days_data_text(count):
    """"1 dags data" eller "3 dagars data", med rätt böjning av dag."""
    if count == 1:
        return "1 dags data"
    return f"{count} dagars data"


def is_whole_number(value):
    """True om value är ett heltal (int). Ett decimaltal som 8000.0 räknas inte, och inte
    heller True och False."""
    return isinstance(value, int) and not isinstance(value, bool)


def normalize_date(date_text):
    """Kontrollerar att texten är ett riktigt datum och skriver det som ÅÅÅÅ-MM-DD med
    nollor, till exempel 2026-10-8 som 2026-10-08. Mellanslag före och efter datumet tas
    bort. Kastar ValueError om det inte är ett datum i det formatet."""
    # Ett värde som inte är text alls, till exempel None från en JSON-fil, ger samma ValueError
    # som en text som inte är ett datum, så den som anropar fångar bara en typ
    if not isinstance(date_text, str):
        raise ValueError(DATE_MESSAGE)

    # strip() tar bort mellanslag, tabbar och radslut runt datumet, som strptime inte godtar.
    # strptime kastar ValueError för text som inte passar formatet eller för ett datum som
    # inte finns (2026-02-30).
    try:
        parsed_date = datetime.strptime(date_text.strip(), "%Y-%m-%d")
    except ValueError:
        raise ValueError(DATE_MESSAGE)

    # isoformat() ger alltid ÅÅÅÅ-MM-DD med nollor, på alla datorer
    return parsed_date.date().isoformat()


class DailyLog:
    """En daglig logg med vikt, kalorier och annan data för ett datum."""

    def __init__(self, date, weight, calories, protein, steps, trained, waist=None):
        # Validering sker här, i klassen, så den gäller oavsett varifrån ett
        # DailyLog-objekt skapas, inte bara när det matas in via input()
        # Datumet skrivs om till ÅÅÅÅ-MM-DD med nollor, så att texterna sorteras rätt och
        # 2026-10-8 inte hamnar efter 2026-10-10 (D1)
        normalized_date = normalize_date(date)

        # Villkoren säger vad som är giltigt, "är ett tal och ligger inom gränserna", och
        # avvisar allt annat. Skrivna som "under eller över gränsen" skulle de släppa igenom
        # nan, eftersom varje jämförelse med nan är falsk och ingen av dem då slår till (N1).
        if not (is_number(weight) and 0 < weight <= MAX_WEIGHT_KG):
            raise ValueError("Vikten måste vara ett rimligt tal i kilogram, till exempel 82.5.")
        if not (is_number(calories) and 0 <= calories <= MAX_CALORIES):
            raise ValueError("Kalorierna måste vara ett rimligt tal, till exempel 2200.")
        if not (is_number(protein) and 0 <= protein <= MAX_PROTEIN_G):
            raise ValueError("Proteinet måste vara ett rimligt tal i gram, till exempel 150.")
        if not (is_whole_number(steps) and 0 <= steps <= MAX_STEPS):
            raise ValueError(
                f"Stegen måste vara ett heltal mellan 0 och {MAX_STEPS}, till exempel 8000."
            )
        # En text som "nej" är sann i Python, så träning som text skulle räknas som ja
        if not isinstance(trained, bool):
            raise ValueError("Träning måste vara True eller False.")
        # Midjemåttet är valfritt, None betyder att det inte är mätt (D2)
        if waist is not None and not (is_number(waist)
                                      and MIN_WAIST_CM <= waist <= MAX_WAIST_CM):
            raise ValueError(
                "Midjemåttet måste vara ett rimligt tal i centimeter, till exempel 92.5."
            )

        self.date = normalized_date
        self.weight = weight
        self.calories = calories
        self.protein = protein
        self.steps = steps
        self.trained = trained
        self.waist = waist


class User:
    """Basklass för en användare av CutTrack."""

    def __init__(self, name, height_cm, age, sex, activity_level, start_weight, created_date):
        # Samma slags kontroll som i DailyLog: klassen avgör vad som är rimligt, så det gäller
        # både för menyn och för en profilfil som har redigerats för hand (N1)
        if not isinstance(name, str) or name.strip() == "":
            raise ValueError("Namnet måste vara en text med minst ett tecken.")
        if len(name.strip()) > MAX_NAME_LENGTH:
            raise ValueError(f"Namnet får vara högst {MAX_NAME_LENGTH} tecken.")
        if not (is_number(height_cm) and MIN_HEIGHT_CM <= height_cm <= MAX_HEIGHT_CM):
            raise ValueError(
                f"Längden måste vara ett tal mellan {MIN_HEIGHT_CM} och {MAX_HEIGHT_CM} cm."
            )
        if not (is_whole_number(age) and MIN_AGE <= age <= MAX_AGE):
            raise ValueError(
                f"Åldern måste vara ett heltal mellan {MIN_AGE} och {MAX_AGE} år. "
                "CutTrack bygger på riktlinjer för vuxna."
            )
        # Exakt man eller kvinna. Före den här kontrollen räknades allt utom "man" som
        # kvinna i calculate_bmr, så ett fel i en profilfil gav fel formel utan meddelande.
        if sex != "man" and sex != "kvinna":
            raise ValueError("Kön måste vara man eller kvinna.")
        if not (is_number(activity_level)
                and MIN_ACTIVITY_LEVEL <= activity_level <= MAX_ACTIVITY_LEVEL):
            raise ValueError(
                f"Aktivitetsnivån måste vara ett tal mellan {MIN_ACTIVITY_LEVEL} "
                f"och {MAX_ACTIVITY_LEVEL}."
            )
        if not (is_number(start_weight) and 0 < start_weight <= MAX_WEIGHT_KG):
            raise ValueError(
                "Startvikten måste vara ett rimligt tal i kilogram, till exempel 90.0."
            )

        # Mellanslag runt namnet sparas inte
        self.name = name.strip()
        self.height_cm = height_cm
        self.age = age
        self.sex = sex
        self.activity_level = activity_level
        self.start_weight = start_weight
        # Samma regel som för loggarnas datum, så att days_since_start och profilfilen
        # alltid får ett riktigt datum
        self.created_date = normalize_date(created_date)
        # Tom lista, en ny användare har per definition inga loggar än
        self.logs = []

    def add_log(self, new_log, announce=True):
        """Lägger till loggen, eller ersätter en logg med samma datum. Returnerar True om en
        logg ersattes. Med announce=False skrivs inget ut, så att CSV-importen kan skriva en
        sammanfattning i stället för en rad per logg."""
        # Samma datum finns redan, ersätt den gamla posten i stället för en dubblett
        for i in range(len(self.logs)):
            if self.logs[i].date == new_log.date:
                self.logs[i] = new_log
                if announce:
                    print(f"Loggen för {new_log.date} uppdaterades.")
                return True
        self.logs.append(new_log)
        if announce:
            print(f"Loggen för {new_log.date} lades till.")
        return False

    def get_logs(self, days, offset_days=0):
        """Returnerar loggarna från de senaste days kalenderdagarna. Med offset_days flyttas
        fönstret så många dagar bakåt, så get_logs(7, 7) är de sju dagarna före de sju senaste."""
        if offset_days < 0:
            raise ValueError("Förskjutningen får inte vara negativ.")
        if len(self.logs) == 0:
            return []

        # Steg 1: hitta det senaste loggade datumet, fönstret räknas bakåt från det
        latest_date = None
        for log in self.logs:
            log_date = datetime.strptime(log.date, "%Y-%m-%d")
            if latest_date is None or log_date > latest_date:
                latest_date = log_date

        # Steg 2: ta med loggar som ligger inom antalet dagar räknat bakåt, efter att de
        # offset_days senaste dagarna hoppats över
        selected_logs = []
        for log in self.logs:
            log_date = datetime.strptime(log.date, "%Y-%m-%d")
            days_ago = (latest_date - log_date).days
            if offset_days <= days_ago < offset_days + days:
                selected_logs.append(log)

        return selected_logs

    def average_weight(self, days, offset_days=0):
        """Medelvikt över perioden. Med offset_days flyttas perioden bakåt, se get_logs.
        Returnerar None om det inte finns några loggar."""
        selected_logs = self.get_logs(days, offset_days)

        if len(selected_logs) == 0:
            return None

        # Ackumulatormönster: summera alla värden, dela med antalet
        total_weight = 0
        for log in selected_logs:
            total_weight = total_weight + log.weight

        return total_weight / len(selected_logs)

    def average_protein(self, days):
        """Medelprotein i gram över perioden. Returnerar None om det inte finns några loggar."""
        selected_logs = self.get_logs(days)

        if len(selected_logs) == 0:
            return None

        # Samma ackumulatormönster som average_weight, bara protein istället för vikt
        total_protein = 0
        for log in selected_logs:
            total_protein = total_protein + log.protein

        return total_protein / len(selected_logs)

    def average_steps(self, days):
        """Medelantal steg över perioden. Returnerar None om det inte finns några loggar."""
        selected_logs = self.get_logs(days)

        if len(selected_logs) == 0:
            return None

        # Samma ackumulatormönster som average_weight, bara steg istället för vikt
        total_steps = 0
        for log in selected_logs:
            total_steps = total_steps + log.steps

        return total_steps / len(selected_logs)

    def training_days(self, days):
        """Antal dagar med träning under perioden."""
        selected_logs = self.get_logs(days)

        # Räknar antal True-värden i fönstret. Returnerar 0, inte None, när det
        # inte finns några loggar, eftersom noll träningsdagar är ett giltigt svar
        total_days = 0
        for log in selected_logs:
            if log.trained:
                total_days = total_days + 1

        return total_days


class CutProfile(User):
    """En användare som deffar. Ärver allt från User och lägger till mål och kaloriberäkningar."""

    def __init__(self, name, height_cm, age, sex, activity_level, start_weight, created_date,
                 goal_weight, target_rate_percent, protein_goal_per_kg=DEFAULT_PROTEIN_PER_KG,
                 step_goal=DEFAULT_STEP_GOAL, training_goal_days=DEFAULT_TRAINING_DAYS):
        # super() sätter alla ärvda attribut, inklusive self.logs, innan de
        # egna attributen sätts nedan. Utan den här raden hade self.logs saknats.
        super().__init__(name, height_cm, age, sex, activity_level, start_weight, created_date)

        # Valideras här, i klassen, av samma skäl som i DailyLog: gäller oavsett
        # hur objektet skapas, inte bara vid inmatning via input(). Först kontrolleras att
        # värdet är ett tal, sedan jämförs det: start_weight är redan kontrollerad av User,
        # så jämförelsen med målvikten kan inte bli falsk av ett nan.
        if not is_number(goal_weight):
            raise ValueError("Målvikten måste vara ett tal i kilogram, till exempel 80.0.")
        if goal_weight <= 0 or goal_weight >= start_weight:
            raise ValueError("Målvikten måste vara lägre än startvikten.")
        if not is_number(target_rate_percent):
            raise ValueError("Takten måste vara ett tal, till exempel 0.7.")
        if target_rate_percent <= 0 or target_rate_percent > 1.0:
            raise ValueError(
                "Takten måste ligga mellan 0 och 1,0 procent av kroppsvikten per vecka."
            )
        if not (is_number(protein_goal_per_kg)
                and 0 < protein_goal_per_kg <= MAX_PROTEIN_PER_KG):
            raise ValueError(
                f"Proteinmålet per kilo måste vara ett tal över 0 och högst "
                f"{MAX_PROTEIN_PER_KG}, till exempel 1.9."
            )
        if not (is_whole_number(step_goal) and 0 < step_goal <= MAX_STEPS):
            raise ValueError(
                f"Stegmålet måste vara ett heltal mellan 1 och {MAX_STEPS}, till exempel 8000."
            )
        if not (is_whole_number(training_goal_days)
                and 0 <= training_goal_days <= MAX_TRAINING_DAYS):
            raise ValueError(
                f"Träningsmålet måste vara ett heltal mellan 0 och {MAX_TRAINING_DAYS} "
                "dagar per vecka."
            )

        self.goal_weight = goal_weight
        self.target_rate_percent = target_rate_percent
        self.protein_goal_per_kg = protein_goal_per_kg
        self.step_goal = step_goal
        self.training_goal_days = training_goal_days
        self.calorie_goal = None

    def current_weight(self):
        """Senaste loggade vikten. Startvikten om inga loggar finns."""
        # Faller tillbaka på startvikten så BMR går att räkna innan någon logg finns
        if len(self.logs) == 0:
            return self.start_weight

        # Datumen jämförs som text, vilket fungerar eftersom DailyLog skriver dem som
        # ÅÅÅÅ-MM-DD med nollor
        latest_log = self.logs[0]
        for log in self.logs:
            if log.date > latest_log.date:
                latest_log = log

        return latest_log.weight

    def calculate_bmr(self):
        """Basalomsättning i kalorier per dygn, enligt Mifflin-St Jeor."""
        # Räknas på aktuell vikt, inte startvikt, eftersom förbrukningen sjunker
        # i takt med vikten under en deff
        weight = self.current_weight()
        bmr = 10 * weight + 6.25 * self.height_cm - 5 * self.age

        # Mifflin-St Jeor, formeln är lika för båda könen förutom sista termen
        if self.sex == "man":
            bmr = bmr + 5
        else:
            bmr = bmr - 161

        return bmr

    def calculate_tdee(self):
        """Totalt dagligt energibehov, basalomsättningen gånger aktivitetsfaktorn."""
        return self.calculate_bmr() * self.activity_level

    def protein_goal(self):
        """Proteinmål i gram per dag, räknat på målvikten."""
        # Räknas på målvikten, inte aktuell vikt, så målet ligger fast
        # genom hela deffen i stället för att sjunka i takt med vikten
        return self.goal_weight * self.protein_goal_per_kg

    def suggest_calorie_goal(self):
        """Räknar ut ett dagligt kaloriförslag utifrån önskad takt.
        Går aldrig under golvet, som är det högsta av basalomsättningen
        och en fast gräns (1500 kcal för män, 1200 för kvinnor)."""
        tdee = self.calculate_tdee()
        bmr = self.calculate_bmr()
        weight = self.current_weight()

        weekly_loss_kg = weight * self.target_rate_percent / 100
        daily_deficit = weekly_loss_kg * 7700 / 7
        suggested_calories = tdee - daily_deficit

        # Fast golv, olika för män och kvinnor
        if self.sex == "man":
            fixed_floor = 1500
        else:
            fixed_floor = 1200

        # Golvet är det högsta av det fasta talet och personens egen basalomsättning
        if bmr > fixed_floor:
            floor = bmr
        else:
            floor = fixed_floor

        # Slår golvet i: justera upp och förklara varför, aldrig tyst
        if suggested_calories < floor:
            print("Kaloriförslaget hamnade under ditt golv och har justerats upp.")
            print(f"Golvet är {round(floor)} kcal, det högsta av din basalomsättning "
                  f"({round(bmr)}) och den fasta gränsen ({fixed_floor}).")
            suggested_calories = floor

            actual_deficit = tdee - floor
            if actual_deficit <= 0:
                print("Med ditt golv går det inte att skapa något underskott genom maten.")
                print("Vägen framåt är att röra dig mer, inte att äta mindre.")
            else:
                actual_weekly_loss = actual_deficit * 7 / 7700
                actual_rate = actual_weekly_loss / weight * 100
                print(f"Takten blir därför {round(actual_rate, 2)} procent per vecka "
                      f"i stället för {self.target_rate_percent}.")
                print("Vill du gå ner snabbare är vägen dit att röra dig mer, "
                      "inte att äta mindre.")

        self.calorie_goal = round(suggested_calories)
        return self.calorie_goal

    def days_since_start(self):
        """Antal dagar från start till senaste loggade dagen, båda dagarna medräknade.
        Starten är profilens startdatum, eller den tidigaste loggen om den ligger före
        startdatumet, till exempel när äldre data har lästs in i en ny profil."""
        if len(self.logs) == 0:
            return 0

        # Datumen jämförs som datum och inte som text, som i get_logs. Som text är
        # 2026-10-8 senare än 2026-10-10
        start_date = datetime.strptime(self.created_date, "%Y-%m-%d")
        latest_date = None
        for log in self.logs:
            log_date = datetime.strptime(log.date, "%Y-%m-%d")
            if log_date < start_date:
                start_date = log_date
            if latest_date is None or log_date > latest_date:
                latest_date = log_date

        # Räknar till senaste loggade dagen, inte till dagens riktiga datum,
        # av samma skäl som get_logs: har du inte loggat på några dagar ska
        # analysen ändå utgå från din senaste aktiva period
        return (latest_date - start_date).days + 1

    def waiting_message(self, days=7):
        """Text tills tillräckligt med data finns för vald analysperiod (days).
        Kräver en period för att visa ett snitt, två perioder för att bedöma takten."""
        total_days = self.days_since_start()

        # En period krävs för att visa ett snitt alls. Bara vikten väntar, protein, träning
        # och steg analyseras redan (F15).
        if total_days < days:
            remaining = days - total_days
            return ("Vikten svänger flera hundra gram från dag till dag på grund av vätska och "
                    "maginnehåll, mer än ett par dagars verkliga fettförlust. En bedömning av "
                    f"vikten byggd på {days_data_text(total_days)} vore bara brus. "
                    f"{days_left_text(remaining)} tills ett {days}-dagarssnitt visas.")

        # Två perioder krävs innan takten bedöms: takten är skillnaden mellan snittet för
        # den senaste perioden och snittet för perioden före (se check_goals)
        if total_days < days * 2:
            remaining = days * 2 - total_days
            return ("Snittet är nu tillräckligt med data för att visas, men "
                    "takten går inte att bedöma säkert än. "
                    f"{days_left_text(remaining)} tills takten bedöms.")

        return None

    def has_enough_weighings(self, days, period_count):
        """Säger om var och en av de period_count senaste perioderna har minst
        MIN_WEIGHINGS_PER_PERIOD vägningar. Takten (två perioder) och platån (tre) kräver det."""
        for period_number in range(period_count):
            if len(self.get_logs(days, period_number * days)) < MIN_WEIGHINGS_PER_PERIOD:
                return False
        return True

    def goal_projection(self, days=7):
        """Hur länge det dröjer till målvikten med nuvarande takt, en linjär projektion (steg
        2). Takten räknas som i check_goals. Returnerar en text, eller None under väntetiden,
        när det saknas vägningar och när vikten inte går ner."""
        if self.waiting_message(days) is not None:
            return None

        # Samma krav som takten i check_goals, annars visas en prognos för en takt som
        # check_goals inte bedömer
        if not self.has_enough_weighings(days, 2):
            return None

        avg_weight = self.average_weight(days)
        previous_avg_weight = self.average_weight(days, days)

        if avg_weight <= self.goal_weight:
            return (f"Målvikten {self.goal_weight} kg: snittet ligger redan på eller under "
                    "målvikten.")

        # Kilo per vecka, samma uträkning som i check_goals. Under UNCHANGED_RATE_KG säger
        # check_goals att det inte finns någon tydlig förändring, och då finns ingen takt att
        # räkna med här heller.
        weekly_loss = -(avg_weight - previous_avg_weight) / days * 7
        if weekly_loss < UNCHANGED_RATE_KG:
            return None

        weeks_left = (avg_weight - self.goal_weight) / weekly_loss
        latest_date = None
        for log in self.logs:
            log_date = datetime.strptime(log.date, "%Y-%m-%d")
            if latest_date is None or log_date > latest_date:
                latest_date = log_date
        days_left = max(1, round(weeks_left * 7))
        goal_date = latest_date + timedelta(days=days_left)

        # Under en vecka i dagar, annars i hela veckor
        if days_left < 7:
            time_text = days_left_text(days_left).replace(" kvar", "")
        elif round(weeks_left) == 1:
            time_text = "1 vecka"
        else:
            time_text = f"{round(weeks_left)} veckor"
        return (f"Målvikten {self.goal_weight} kg: med den här takten om cirka {time_text}, "
                f"omkring {goal_date.date().isoformat()}. En grov uppskattning, takten "
                "brukar avta när vikten går ner.")

    def weight_around(self, center_date):
        """Medelvikt för vägningarna högst WEIGHT_AROUND_WAIST_DAYS dagar före eller efter
        center_date. Returnerar None om det finns färre än MIN_WEIGHINGS_PER_PERIOD vägningar,
        så att ett enstaka extremvärde inte kan avgöra jämförelsen."""
        total_weight = 0
        weighing_count = 0
        for log in self.logs:
            log_date = datetime.strptime(log.date, "%Y-%m-%d")
            if abs((log_date - center_date).days) <= WEIGHT_AROUND_WAIST_DAYS:
                total_weight = total_weight + log.weight
                weighing_count = weighing_count + 1

        if weighing_count < MIN_WEIGHINGS_PER_PERIOD:
            return None
        return total_weight / weighing_count

    def waist_comparison(self):
        """Jämför första och senaste midjemåttet med vikten runt samma dagar (F18). Kräver tre
        tillfällen med midjemått och minst 14 dagar mellan första och sista. Vikten är
        medelvärdet av vägningarna runt varje mätning, se weight_around. Returnerar en text,
        eller None om inget midjemått är loggat."""
        measured_logs = []
        for log in self.logs:
            if log.waist is not None:
                measured_logs.append(log)

        if len(measured_logs) == 0:
            return None

        # Första och senaste mätningen efter datum, inte efter plats i listan
        first_log = measured_logs[0]
        last_log = measured_logs[0]
        for log in measured_logs:
            if log.date < first_log.date:
                first_log = log
            if log.date > last_log.date:
                last_log = log

        first_date = datetime.strptime(first_log.date, "%Y-%m-%d")
        last_date = datetime.strptime(last_log.date, "%Y-%m-%d")
        if (len(measured_logs) < WAIST_MIN_MEASUREMENTS
                or (last_date - first_date).days < WAIST_MIN_DAYS):
            return (f"Midjan: för få mätningar för att jämföra. Det behövs minst "
                    f"{WAIST_MIN_MEASUREMENTS} mätningar, med minst {WAIST_MIN_DAYS} dagar "
                    "mellan den första och den sista.")

        first_weight = self.weight_around(first_date)
        last_weight = self.weight_around(last_date)
        if first_weight is None or last_weight is None:
            return ("Midjan: för få vägningar för att jämföra vikten. Det behövs minst "
                    f"{MIN_WEIGHINGS_PER_PERIOD} vägningar inom {WEIGHT_AROUND_WAIST_DAYS} dagar "
                    "före eller efter varje midjemätning.")

        waist_change = round(last_log.waist - first_log.waist, 1)
        weight_loss = round(first_weight - last_weight, 1)
        weight_went_down = weight_loss >= WEIGHT_CHANGE_KG

        if waist_change <= -WAIST_CHANGE_CM:
            waist_text = f"Midjan: {abs(waist_change)} cm mindre sedan {first_log.date}"
            if weight_went_down:
                return (f"{waist_text}, och vikten {weight_loss} kg lägre. "
                        "Det pekar mot att det är fett som försvinner.")
            return waist_text + "."

        if waist_change >= WAIST_CHANGE_CM:
            return f"Midjan: {waist_change} cm större sedan {first_log.date}."

        # Mindre än gränsen åt något håll: inom mätfelet, så midjan räknas som nästan oförändrad.
        # :+.1f skriver talet med tecken och en decimal, till exempel -1.8 eller +0.5.
        unchanged_text = (f"Midjan: nästan oförändrad sedan {first_log.date} "
                          f"({waist_change:+.1f} cm, inom mätfelet på "
                          f"{round(WAIST_CHANGE_CM)} cm)")
        if weight_went_down:
            return (f"{unchanged_text}. Vikten är {weight_loss} kg lägre, men midjemåttet räcker "
                    "inte för att avgöra om det är fett eller muskler som går förlorade. Mät "
                    "på samma ställe och på samma sätt varje gång, och titta igen efter "
                    "fler veckor.")
        return unchanged_text + "."

    def plateau_message(self, days=7):
        """Text om vikten har stått still i två jämförelser i rad (platå, steg 2), annars None.
        Varje jämförelse räknas som takten i check_goals: snittet för en period mot snittet
        för perioden före, i kg per vecka. Två jämförelser kräver tre hela perioder med
        vägningar."""
        if not self.has_enough_weighings(days, 3):
            return None

        averages = []
        for period_number in range(3):
            averages.append(self.average_weight(days, period_number * days))

        # averages[0] är den senaste perioden, averages[2] den äldsta
        latest_change = (averages[0] - averages[1]) / days * 7
        earlier_change = (averages[1] - averages[2]) / days * 7

        # Samma gräns som texten om ingen tydlig förändring i check_goals
        if abs(latest_change) < UNCHANGED_RATE_KG and abs(earlier_change) < UNCHANGED_RATE_KG:
            return ("Platå: vikten har stått still i två jämförelser i rad, alltså de "
                    f"senaste {days * 3} dagarna. Kontrollera först att allt du äter och "
                    "dricker loggas. Stämmer loggningen behöver underskottet bli större, se "
                    "kaloriförslaget.")
        return None

    def check_goals(self, days=7):
        """Statusöversikt för vald analysperiod (7, 14 eller 30 dagar), plus en sak att
        fokusera på. Prioritetsordning: vikt, protein, träningsfrekvens, steg. Under
        väntetiden bedöms vikten inte, men protein, träning och steg gör det (F15)."""
        waiting_text = self.waiting_message(days)
        focus_area = None
        # Säger varför vikten inte bedömdes, när den inte gjorde det. Slutraden använder den, så
        # att den inte säger att allt ligger inom mål när vikten aldrig bedömdes (F17).
        weight_not_assessed = None

        if waiting_text is not None:
            # Vikten kräver två hela perioder (se waiting_message). Protein, träning och steg
            # kräver bara ett snitt, så de analyseras ändå nedan.
            print(waiting_text)
            print()
            weight_not_assessed = "Vikten bedöms när väntetiden är över."
            # Efter en hel period finns ett snitt att visa, fast takten inte går att bedöma
            # förrän perioden före också är full (F16). Snittet bedöms inte och blir aldrig
            # fokusområde.
            if self.days_since_start() >= days:
                avg_weight = self.average_weight(days)
                if avg_weight is not None:
                    print(f"Vikten: snitt {round(avg_weight, 1)} kg de senaste {days} dagarna. "
                          "Takten bedöms inte än.")
        else:
            # Vikt: undre gränsen är personens eget mål, övre gränsen är ett fast säkerhetstak.
            # Takten är skillnaden mellan snittet för den senaste perioden och snittet för
            # perioden före. Ett snitt ligger mitt i sin period, så de två snitten hör till
            # tidpunkter som ligger days dagar från varandra (med loggar de flesta dagar, luckor
            # gör takten mindre exakt). Skillnaden delas därför med days och multipliceras med 7,
            # annars blir en förändring över 30 dagar feltolkad som en veckotakt.
            if self.has_enough_weighings(days, 2):
                avg_weight = self.average_weight(days)
                previous_avg_weight = self.average_weight(days, days)
                weekly_change = (avg_weight - previous_avg_weight) / days * 7
                # Procenttalet avrundas en gång och används både i texten och i jämförelserna,
                # så att raden aldrig säger "0.7 procent, långsammare än ditt mål på 0.7".
                # Kilotalen visas med två decimaler av samma skäl.
                rate_percent = round(-weekly_change / avg_weight * 100, 2)
                actual_kg = f"{abs(weekly_change):.2f}"
                safety_kg = f"{avg_weight * 1.0 / 100:.2f}"
                target_kg = f"{avg_weight * self.target_rate_percent / 100:.2f}"

                # En skillnad under UNCHANGED_RATE_KG går inte att skilja från vågens vanliga
                # variation mellan dagar
                if abs(weekly_change) < UNCHANGED_RATE_KG:
                    print("Vikten: ingen tydlig förändring jämfört med perioden före. "
                          f"Skillnaden är under {UNCHANGED_RATE_KG} kg per vecka, inom vågens "
                          "vanliga variation.")
                    # Har vikten stått still även i jämförelsen före är det en platå
                    plateau_text = self.plateau_message(days)
                    if plateau_text is not None:
                        print(plateau_text)
                    focus_area = "vikt"
                elif weekly_change > 0:
                    print(f"Vikten: ökar med {actual_kg} kg per vecka i snitt. "
                          "Underskottet räcker inte.")
                    focus_area = "vikt"
                elif rate_percent > 1.0:
                    print(f"Vikten: minskar med {rate_percent} procent per vecka "
                          f"(cirka {actual_kg} kg), över säkerhetsgränsen 1,0 procent "
                          f"(cirka {safety_kg} kg för dig). Risk för muskelförlust.")
                    if focus_area is None:
                        focus_area = "vikt"
                elif rate_percent < self.target_rate_percent:
                    print(f"Vikten: minskar med {rate_percent} procent per vecka "
                          f"(cirka {actual_kg} kg), långsammare än ditt mål på "
                          f"{self.target_rate_percent} procent (cirka {target_kg} kg för dig).")
                    if focus_area is None:
                        focus_area = "vikt"
                else:
                    print(f"Vikten: minskar med {rate_percent} procent per vecka "
                          f"(cirka {actual_kg} kg), vid eller över ditt mål på "
                          f"{self.target_rate_percent} procent och inom säkerhetsgränsen.")
            else:
                previous_count = len(self.get_logs(days, days))
                latest_count = len(self.get_logs(days))
                print(f"Vikten: för få vägningar för att bedöma takten, {previous_count} i "
                      f"perioden före och {latest_count} i den senaste. Det behövs minst "
                      f"{MIN_WEIGHINGS_PER_PERIOD} i varje.")
                weight_not_assessed = ("Vikten gick inte att bedöma, eftersom det finns för få "
                                       "vägningar i någon av perioderna.")

            # Hur länge till målvikten med den här takten (steg 2). Bara en uppgift, den
            # påverkar inte fokus.
            projection_text = self.goal_projection(days)
            if projection_text is not None:
                print(projection_text)

        # Protein, dagligt mål, ingen skalning behövs
        avg_protein = self.average_protein(days)
        protein_target = self.protein_goal()
        if avg_protein is not None:
            if avg_protein < protein_target:
                print(f"Protein: snitt {round(avg_protein)} g mot mål {round(protein_target)} g. "
                      "Under målet.")
                if focus_area is None:
                    focus_area = "protein"
            else:
                print(f"Protein: snitt {round(avg_protein)} g mot mål {round(protein_target)} g. "
                      "Målet nås.")
        else:
            print("Protein: för lite data.")

        # Träningsfrekvens är ett veckomål, det skalas till den valda perioden. Under väntetiden
        # har perioden inte hunnit bli full, så målet skalas till dagarna hittills.
        covered_days = min(days, self.days_since_start())
        training_count = self.training_days(days)
        expected_training = round(self.training_goal_days * covered_days / 7)
        # Ett mål på 0 dagar ger alltid förväntan 0, och det är inte för få dagar utan inget mål
        if expected_training == 0 and self.training_goal_days > 0:
            print("Träning: för få dagar för att bedöma än.")
        elif training_count < expected_training:
            print(f"Träning: {training_count} av {expected_training} förväntade dagar under "
                  "perioden. Under målet.")
            if focus_area is None:
                focus_area = "träning"
        else:
            print(f"Träning: {training_count} av {expected_training} förväntade dagar under "
                  "perioden. Målet nås.")

        # Steg, dagligt mål, ingen skalning behövs
        avg_steps = self.average_steps(days)
        if avg_steps is not None:
            if avg_steps < self.step_goal:
                print(f"Steg: snitt {round(avg_steps)} mot mål {self.step_goal}. Under målet.")
                if focus_area is None:
                    focus_area = "steg"
            else:
                print(f"Steg: snitt {round(avg_steps)} mot mål {self.step_goal}. Målet nås.")
        else:
            print("Steg: för lite data.")

        # Midjan bedöms inte mot något mål och blir aldrig fokusområde, den är en signal (F18)
        waist_text = self.waist_comparison()
        if waist_text is not None:
            print(waist_text)

        print()
        if focus_area is None and weight_not_assessed is not None:
            print(f"Det som gick att bedöma ligger inom mål. {weight_not_assessed}")
        elif focus_area is None:
            print("Allt ligger inom mål just nu. Fortsätt som du gör.")
        else:
            print(f"Fokusera på: {focus_area}.")
