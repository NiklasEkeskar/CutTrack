"""Textmenyn för CutTrack. All inmatning och utskrift ligger här, skilt från klasserna
i models.py och filhanteringen i analysis.py.
Startas från terminalen med: python main.py
Importeras i cuttrack.ipynb med:
from main import (show_welcome, ask_number, ask_period,
                  create_profile, log_today, run_menu)"""
from datetime import datetime

from models import DailyLog, CutProfile, normalize_date
from analysis import (make_csv_filename, save_profile, load_profile, profile_file_exists,
                      export_logs_csv, import_logs_csv, plot_weight)


def show_welcome():
    """Visar välkomsttext, riktlinjer och ansvarsfriskrivning."""
    print()
    print("CutTrack")
    print()
    print("Ett verktyg för dig som deffar och vill behålla muskelmassan på vägen.")
    print()
    print("Vad som krävs för att lyckas:")
    print()
    print("  Styrketräna regelbundet. Frekvensen är det som håller muskelmassan uppe,")
    print("  inte hur långa passen är.")
    print()
    print("  Ät tillräckligt med protein. Målet räknas på din målvikt och ligger fast")
    print("  genom hela deffen.")
    print()
    print("  Håll din dagliga aktivitet uppe. Steg utanför träningen påverkar")
    print("  förbrukningen mer än de flesta tror.")
    print()
    print("  Håll ett måttligt kaloriunderskott. För stort underskott kostar")
    print("  muskelmassa utan att gå snabbare i längden.")
    print()
    print("  Logga varje dag. Programmet väntar 14 dagar innan det bedömer takten,")
    print("  eftersom dagliga vägningar svänger mer än en hel veckas fettförlust.")
    print()
    print("Observera: CutTrack ger allmänna riktvärden baserade på etablerade")
    print("rekommendationer. Det är inte medicinsk rådgivning. Rådgör med läkare")
    print("eller dietist vid sjukdom, graviditet eller medicinering.")
    print()


def ask_number(question, is_integer=False):
    """Frågar tills användaren skriver ett giltigt tal."""
    # while True med return inuti try: loopen upprepas bara vid fel,
    # ett giltigt svar returneras direkt och avslutar funktionen
    while True:
        answer = input(question)
        try:
            if is_integer:
                return int(answer)
            return float(answer)
        except ValueError:
            print("Skriv ett tal, till exempel 82.5.")


def ask_period():
    """Frågar efter analysperiod, 7, 14 eller 30 dagar."""
    # Bygger på ask_number för själva taltolkningen, men kontrollerar dessutom
    # att svaret finns i listan av giltiga perioder, inte bara att det är ett tal
    valid_periods = [7, 14, 30]
    period = 0
    while period not in valid_periods:
        period = ask_number("Analysperiod i dagar (7, 14 eller 30): ", True)
        if period not in valid_periods:
            print("Välj 7, 14 eller 30.")
    return period


def create_profile(name):
    """Frågar efter uppgifterna som behövs och skapar en ny CutProfile."""
    print()
    print("Ny profil. Svara på några frågor så räknar programmet ut ditt kaloriförslag.")
    print()

    height_cm = ask_number("Längd i cm: ", True)
    age = ask_number("Ålder: ", True)

    sex = ""
    while sex != "man" and sex != "kvinna":
        sex = input("Kön (man/kvinna): ").lower()
        if sex != "man" and sex != "kvinna":
            print("Skriv man eller kvinna.")

    print()
    print("Aktivitetsnivå:")
    print("  1  Stillasittande")
    print("  2  Lätt aktiv")
    print("  3  Måttligt aktiv")
    print("  4  Mycket aktiv")
    print("  5  Extremt aktiv")

    # Dictionary så användaren slipper veta vad faktorerna betyder
    activity_levels = {1: 1.2, 2: 1.375, 3: 1.55, 4: 1.725, 5: 1.9}

    activity_choice = 0
    while activity_choice not in activity_levels:
        activity_choice = ask_number("Välj 1 till 5: ", True)
        if activity_choice not in activity_levels:
            print("Välj ett tal mellan 1 och 5.")

    activity_level = activity_levels[activity_choice]

    print()
    # Vikterna och takten valideras tillsammans i CutProfile, så alla tre frågas om vid fel
    while True:
        start_weight = ask_number("Startvikt i kg: ")
        goal_weight = ask_number("Målvikt i kg: ")
        target_rate = ask_number("Önskad takt i procent per vecka (0.5 till 1.0): ")

        # Konkret exempel innan profilen skapas, eftersom procent är abstrakt utan ett kilotal
        example_kg = round(start_weight * target_rate / 100, 1)
        print(f"Det motsvarar cirka {example_kg} kg per vecka vid din nuvarande vikt.")

        try:
            created_date = datetime.now().strftime("%Y-%m-%d")
            profile = CutProfile(name, height_cm, age, sex, activity_level,
                                 start_weight, created_date, goal_weight, target_rate)
            return profile
        except ValueError as error:
            print(f"Det gick inte: {error}")
            print("Försök igen.")


def log_today(user):
    """Frågar användaren om dagens värden och lägger till en DailyLog på user. Ger True om
    loggen lades till och False om inmatningen var fel, så att anroparen vet om det finns
    något nytt att spara."""
    date_text = input("Datum (ÅÅÅÅ-MM-DD): ")

    # Allt inuti try-blocket delar samma feltyp (ValueError), från fel datumformat,
    # text där tal förväntas, eller orimliga värden i DailyLog. Ett gemensamt except
    # räcker därför. Går något fel sparas ingen logg, hela blocket hoppas över.
    try:
        # Datumet kontrolleras först, så att ett fel datum stoppar innan användaren har
        # skrivit in resten, och skrivs om till ÅÅÅÅ-MM-DD med nollor
        date_text = normalize_date(date_text)
        weight = float(input("Vikt i kg: "))
        calories = float(input("Kalorier: "))
        protein = float(input("Protein i gram: "))
        steps = int(input("Steg: "))

        trained_text = input("Tränade du idag? (j/n): ")
        trained = trained_text.lower() == "j"

        waist_text = input("Midjemått i cm (lämna tomt om du inte mätt): ")
        if waist_text == "":
            waist = None
        else:
            waist = float(waist_text)

        new_log = DailyLog(date_text, weight, calories, protein, steps, trained, waist)
        user.add_log(new_log)
        return True

    except ValueError as error:
        print(f"Loggen sparades inte. Något var fel i inmatningen: {error}")
        return False


def run_menu():
    """Programmets huvudloop."""
    show_welcome()

    name = input("Vad heter du? ")
    profile = load_profile(name)

    if profile is None:
        # load_profile ger None både när filen saknas och när den inte går att läsa. Finns
        # filen men går inte att läsa får ingen ny profil skapas: menyval 6 skulle skriva
        # över filen med den tomma profilen, och loggarna som låg i filen vore borta.
        if profile_file_exists(name):
            print()
            print("Programmet avslutas utan att ändra filen. Rätta filen eller flytta den "
                  "till en annan mapp och starta om.")
            print("En ny profil skapas inte, eftersom den skulle skriva över filen.")
            return

        profile = create_profile(name)
        print()
        print(f"Profil skapad för {profile.name}.")
        print()
        profile.suggest_calorie_goal()
        print(f"Ditt kaloriförslag: {profile.calorie_goal} kcal per dag.")
        print(f"Ditt proteinmål: {round(profile.protein_goal())} gram per dag.")

    running = True
    while running:
        print()
        print("Meny")
        print("  1  Logga dagens data")
        print("  2  Visa analys")
        print("  3  Visa viktdiagram")
        print("  4  Visa kaloriförslag")
        print("  5  Läs in loggar från CSV")
        print("  6  Spara och avsluta")
        print()

        # input() ger alltid text, choice jämförs därför som text, inte omvandlas till int
        choice = input("Välj: ")

        if choice == "1":
            log_added = log_today(profile)
            if log_added:
                # Sparar direkt, så att loggen inte försvinner om programmet avbryts före
                # menyval 6. Misslyckas det ligger loggen kvar i programmet, och menyval 6
                # försöker igen.
                saved = save_profile(profile)
                if not saved:
                    print("Loggen finns i programmet men är inte sparad på disk. "
                          "Välj 6 för att försöka spara igen.")
        elif choice == "2":
            print()
            period = ask_period()
            profile.check_goals(period)
        elif choice == "3":
            period = ask_period()
            plot_weight(profile, period)
        elif choice == "4":
            print()
            profile.suggest_calorie_goal()
            print(f"Kaloriförslag: {profile.calorie_goal} kcal per dag.")
            print(f"Proteinmål: {round(profile.protein_goal())} gram per dag.")
        elif choice == "5":
            default_filename = make_csv_filename(profile.name)
            filename = input(f"Filnamn (tomt för {default_filename}): ")
            if filename == "":
                filename = default_filename
            import_logs_csv(profile, filename)
        elif choice == "6":
            saved = save_profile(profile)
            if saved:
                # CSV-filen är en extra kopia av loggarna och skrivs bara när profilen har
                # sparats. Misslyckas disken är en halvskriven CSV-fil sämre än ingen, den
                # skulle ersätta den förra kopian.
                export_logs_csv(profile)
                print("Hej då.")
                running = False
            else:
                print("Profilen sparades inte, så programmet avslutas inte.")
                print("Rätta felet ovan och välj 6 igen.")
                print("Avbryter du i stället går det du inte sparat förlorat.")
        else:
            print("Välj ett tal mellan 1 och 6.")


def main():
    """Startar programmet. Ctrl+C och Ctrl+D avbryter utan Python-felutskrift."""
    try:
        run_menu()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C ger KeyboardInterrupt, och Ctrl+D eller en stängd inmatning ger
        # EOFError. Båda är användarens sätt att avbryta, inte fel i programmet.
        # Menyval 1 sparar hela profilen efter varje ny logg. Det som lästs in från CSV
        # (menyval 5) sparas inte direkt, bara av nästa ny logg eller av menyval 6, så
        # båda sägs rakt ut.
        print()
        print("Avbrutet.")
        print("Varje logg du lade till med menyval 1 sparades direkt, om inte programmet "
              "sa att sparningen misslyckades.")
        print("Loggar som lästs in från CSV sparas först när du lägger till en ny logg "
              "eller väljer 6.")


if __name__ == "__main__":
    main()
