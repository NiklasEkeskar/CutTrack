"""Klasserna som utgör CutTracks datamodell: DailyLog, User och CutProfile, funktionen
normalize_date som kontrollerar och skriver om datum, och gränserna för vad som räknas som
rimliga värden.
Importeras i cuttrack.ipynb med: from models import DailyLog, User, CutProfile"""
import math
from datetime import datetime

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

    def add_log(self, new_log):
        # Samma datum finns redan, ersätt den gamla posten i stället för en dubblett
        for i in range(len(self.logs)):
            if self.logs[i].date == new_log.date:
                self.logs[i] = new_log
                print(f"Loggen för {new_log.date} uppdaterades.")
                return
        self.logs.append(new_log)
        print(f"Loggen för {new_log.date} lades till.")

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

    def weight_change(self, days):
        """Viktförändring i kg över perioden. Negativt tal betyder att vikten gått ner.
        Returnerar None om det finns färre än två loggar."""
        selected_logs = self.get_logs(days)

        # Minst två loggar krävs, annars finns ingen förändring att mäta
        if len(selected_logs) < 2:
            return None

        # Hittar tidigaste och senaste loggen genom att jämföra datumsträngarna
        # direkt, utan att sortera listan. Fungerar eftersom DailyLog skriver alla datum som
        # ÅÅÅÅ-MM-DD med nollor, och det formatet sorteras rätt även som text.
        first_log = selected_logs[0]
        last_log = selected_logs[0]
        for log in selected_logs:
            if log.date < first_log.date:
                first_log = log
            if log.date > last_log.date:
                last_log = log

        return last_log.weight - first_log.weight

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
                 goal_weight, target_rate_percent, protein_goal_per_kg=1.9, step_goal=8000,
                 training_goal_days=3):
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

        # En period krävs för att visa ett snitt alls
        if total_days < days:
            remaining = days - total_days
            return ("Vikten svänger flera hundra gram från dag till dag på grund av vätska och "
                    "maginnehåll, mer än ett par dagars verkliga fettförlust. Ett råd byggt på "
                    f"{total_days} dagars data vore bara brus. {remaining} dagar kvar tills ett "
                    f"{days}-dagarssnitt visas.")

        # Två perioder krävs innan takten bedöms: takten är skillnaden mellan snittet för
        # den senaste perioden och snittet för perioden före (se check_goals)
        if total_days < days * 2:
            remaining = days * 2 - total_days
            return ("Snittet är nu tillräckligt med data för att visas, men "
                    "takten går inte att bedöma säkert än. "
                    f"{remaining} dagar kvar tills full analys är möjlig.")

        return None

    def check_goals(self, days=7):
        """Statusöversikt för vald analysperiod (7, 14 eller 30 dagar), plus en sak att
        fokusera på. Prioritetsordning: vikt, protein, träningsfrekvens, steg."""
        waiting_text = self.waiting_message(days)
        if waiting_text is not None:
            print(waiting_text)
            return

        focus_area = None

        # Vikt: undre gränsen är personens eget mål, övre gränsen är ett fast säkerhetstak.
        # Takten är skillnaden mellan snittet för den senaste perioden och snittet för
        # perioden före. Ett snitt ligger mitt i sin period, så de två snitten hör till
        # tidpunkter som ligger days dagar från varandra (med loggar de flesta dagar, luckor
        # gör takten mindre exakt). Skillnaden delas därför med days och multipliceras med 7,
        # annars blir en förändring över 30 dagar feltolkad som en veckotakt.
        avg_weight = self.average_weight(days)
        previous_avg_weight = self.average_weight(days, days)
        if avg_weight is not None and previous_avg_weight is not None and avg_weight > 0:
            weekly_change = (avg_weight - previous_avg_weight) / days * 7
            rate_percent = -weekly_change / avg_weight * 100
            actual_kg = round(abs(weekly_change), 1)
            safety_kg = round(avg_weight * 1.0 / 100, 1)
            target_kg = round(avg_weight * self.target_rate_percent / 100, 1)

            # Under 0,05 kg per vecka avrundas kilotalet till 0.0. Då vore "minskar med 0.0
            # kg" missvisande, så vikten räknas som oförändrad
            if abs(weekly_change) < 0.05:
                print("Vikten: oförändrad jämfört med perioden före. "
                      "Underskottet räcker inte.")
                focus_area = "vikt"
            elif weekly_change > 0:
                print(f"Vikten: ökar med {actual_kg} kg per vecka i snitt. "
                      "Underskottet räcker inte.")
                focus_area = "vikt"
            elif rate_percent > 1.0:
                print(f"Vikten: minskar med {round(rate_percent, 2)} procent per vecka "
                      f"(cirka {actual_kg} kg), över säkerhetsgränsen 1,0 procent "
                      f"(cirka {safety_kg} kg för dig). Risk för muskelförlust.")
                if focus_area is None:
                    focus_area = "vikt"
            elif rate_percent < self.target_rate_percent:
                print(f"Vikten: minskar med {round(rate_percent, 2)} procent per vecka "
                      f"(cirka {actual_kg} kg), långsammare än ditt mål på "
                      f"{self.target_rate_percent} procent (cirka {target_kg} kg för dig).")
                if focus_area is None:
                    focus_area = "vikt"
            else:
                print(f"Vikten: minskar med {round(rate_percent, 2)} procent per vecka "
                      f"(cirka {actual_kg} kg), vid eller över ditt mål på "
                      f"{self.target_rate_percent} procent och inom säkerhetsgränsen.")
        else:
            print("Vikten: för lite data för att bedöma takten.")

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

        # Träningsfrekvens är ett veckomål, det skalas till den valda perioden
        training_count = self.training_days(days)
        expected_training = round(self.training_goal_days * days / 7)
        if training_count < expected_training:
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

        print()
        if focus_area is None:
            print("Allt ligger inom mål just nu. Fortsätt som du gör.")
        else:
            print(f"Fokusera på: {focus_area}.")
