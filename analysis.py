"""Filhantering (JSON, CSV) och diagram för CutTrack.
Importeras i cuttrack.ipynb med:
from analysis import (make_filename, save_profile, load_profile,
                       export_logs_csv, import_logs_csv,
                       plot_weight, plot_protein, plot_steps)"""
import json
import csv
import os
import matplotlib.pyplot as plt

from models import DailyLog, CutProfile


ALLOWED_CHARACTERS = "abcdefghijklmnopqrstuvwxyz0123456789"


def make_filename(name):
    """Bygger ett säkert filnamn från användarens namn.
    Behåller bara a till z och siffror, allt annat tas bort."""
    safe_name = ""
    for character in name.lower():
        if character in ALLOWED_CHARACTERS:
            safe_name = safe_name + character

    # Fallback om namnet bara bestod av tecken som togs bort
    if safe_name == "":
        safe_name = "anvandare"

    return safe_name + ".json"


def save_profile(profile):
    """Sparar profilen och alla loggar som JSON. Returnerar True om det gick bra."""
    filename = make_filename(profile.name)

    # Loggarna måste göras om till dictionaries, JSON kan inte spara objekt
    log_list = []
    for log in profile.logs:
        log_list.append({
            "date": log.date,
            "weight": log.weight,
            "calories": log.calories,
            "protein": log.protein,
            "steps": log.steps,
            "trained": log.trained,
            "waist": log.waist
        })

    data = {
        "name": profile.name,
        "height_cm": profile.height_cm,
        "age": profile.age,
        "sex": profile.sex,
        "activity_level": profile.activity_level,
        "start_weight": profile.start_weight,
        "created_date": profile.created_date,
        "goal_weight": profile.goal_weight,
        "target_rate_percent": profile.target_rate_percent,
        "protein_goal_per_kg": profile.protein_goal_per_kg,
        "step_goal": profile.step_goal,
        "training_goal_days": profile.training_goal_days,
        "logs": log_list
    }

    # OSError fångar problem med själva skrivningen, till exempel att disken
    # är full eller att mappen saknar skrivrättigheter
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Profilen sparades i {filename}.")
        return True
    except OSError as error:
        print(f"Profilen kunde inte sparas: {error}")
        return False


def load_profile(name):
    """Läser en profil från JSON. Returnerar None om filen saknas eller inte går att läsa."""
    filename = make_filename(name)

    # Att filen saknas är inte ett fel, det är normalt för en ny användare
    if not os.path.exists(filename):
        print(f"Ingen sparad profil hittades för {name}.")
        return None

    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        profile = CutProfile(
            data["name"], data["height_cm"], data["age"], data["sex"],
            data["activity_level"], data["start_weight"], data["created_date"],
            data["goal_weight"], data["target_rate_percent"],
            data["protein_goal_per_kg"], data["step_goal"], data["training_goal_days"]
        )

        for log_data in data["logs"]:
            log = DailyLog(
                log_data["date"], log_data["weight"], log_data["calories"],
                log_data["protein"], log_data["steps"], log_data["trained"],
                log_data["waist"]
            )
            profile.logs.append(log)

        print(f"Profilen för {profile.name} laddades, {len(profile.logs)} loggar.")
        return profile

    # Tre skilda except-block, inte ett gemensamt, eftersom felen betyder olika
    # saker och kräver olika åtgärder av användaren
    except json.JSONDecodeError:
        # Filen finns men innehållet är inte giltig JSON, t.ex. redigerad för hand
        print(f"Filen {filename} är skadad och kunde inte läsas.")
        return None
    except KeyError as error:
        # Giltig JSON men saknar ett fält koden förväntar sig, t.ex. en äldre filversion
        print(f"Filen {filename} saknar fältet {error}.")
        return None
    except ValueError as error:
        # Fälten finns men värdena är orimliga, DailyLog eller CutProfile vägrar dem
        print(f"Filen {filename} innehåller ogiltiga värden: {error}")
        return None


def export_logs_csv(profile, filename="cuttrack_loggar.csv"):
    """Sparar alla loggar som CSV. Detta är datafilen som lämnas in."""
    if len(profile.logs) == 0:
        print("Det finns inga loggar att exportera.")
        return False

    column_names = ["date", "weight", "calories", "protein", "steps", "trained", "waist"]

    # newline="" krävs av csv-modulen, annars kan filen få extra tomrader på Windows
    try:
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(column_names)

            for log in profile.logs:
                # None skrivs som tom cell, inte som texten "None"
                if log.waist is None:
                    waist_text = ""
                else:
                    waist_text = log.waist

                writer.writerow([log.date, log.weight, log.calories, log.protein,
                                 log.steps, log.trained, waist_text])

        if len(profile.logs) == 1:
            print(f"1 logg exporterades till {filename}.")
        else:
            print(f"{len(profile.logs)} loggar exporterades till {filename}.")
        return True

    except OSError as error:
        print(f"Loggarna kunde inte exporteras: {error}")
        return False


def import_logs_csv(profile, filename="cuttrack_loggar.csv"):
    """Läser in loggar från en CSV-fil och lägger till dem på profilen.
    Rader med ogiltiga värden hoppas över, resten läses in."""
    if not os.path.exists(filename):
        print(f"Filen {filename} hittades inte.")
        return 0

    imported_count = 0

    try:
        with open(filename, "r", newline="", encoding="utf-8") as file:
            # DictReader läser varje rad som en dictionary, med kolumnnamnen från
            # första raden som nycklar, så ordningen på kolumnerna spelar ingen roll
            reader = csv.DictReader(file)

            for row in reader:
                # try/except inne i loopen, så en trasig rad inte stoppar hela importen
                try:
                    # Allt som läses från CSV är text, även talen, därför float()/int()
                    if row["waist"] == "":
                        waist = None
                    else:
                        waist = float(row["waist"])

                    log = DailyLog(
                        row["date"],
                        float(row["weight"]),
                        float(row["calories"]),
                        float(row["protein"]),
                        int(row["steps"]),
                        row["trained"] == "True",
                        waist
                    )
                    profile.add_log(log)
                    imported_count = imported_count + 1

                except ValueError as error:
                    print(f"Hoppade över en rad med ogiltiga värden: {error}")
                except KeyError as error:
                    print(f"Hoppade över en rad som saknar kolumnen {error}.")

        print(f"{imported_count} loggar lästes in från {filename}.")
        return imported_count

    except OSError as error:
        print(f"Filen kunde inte läsas: {error}")
        return 0


def plot_weight(profile, days=30):
    """Visar ett diagram över viktutvecklingen, med loggad vikt,
    rullande sjudagarssnitt och målvikt."""
    selected_logs = profile.get_logs(days)

    if len(selected_logs) < 2:
        print("Det behövs minst två loggar för att rita ett diagram.")
        return

    # Loggarna kan ligga i fel ordning, och en hoppig linje blir obegriplig.
    # Datumet används som nyckel i en dictionary, sedan sorteras nycklarna.
    logs_by_date = {}
    for log in selected_logs:
        logs_by_date[log.date] = log

    sorted_dates = sorted(logs_by_date)

    sorted_logs = []
    for date in sorted_dates:
        sorted_logs.append(logs_by_date[date])

    dates = []
    weights = []
    for log in sorted_logs:
        dates.append(log.date)
        weights.append(log.weight)

    # Rullande sjudagarssnitt, ett värde per dag från och med den sjunde
    average_dates = []
    average_weights = []
    for i in range(len(sorted_logs)):
        if i >= 6:
            total = 0
            for j in range(i - 6, i + 1):
                total = total + sorted_logs[j].weight
            average_dates.append(sorted_logs[i].date)
            average_weights.append(total / 7)

    plt.figure(figsize=(10, 5))
    plt.plot(dates, weights, marker="o", label="Loggad vikt")

    if len(average_weights) > 0:
        plt.plot(average_dates, average_weights, linewidth=2, label="Sjudagarssnitt")

    plt.axhline(y=profile.goal_weight, linestyle="--", label="Målvikt")

    plt.title(f"Viktutveckling för {profile.name}")
    plt.xlabel("Datum")
    plt.ylabel("Vikt i kg")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_protein(profile, days=30):
    """Visar ett diagram över proteinintaget, med loggat protein per dag,
    rullande sjudagarssnitt och proteinmålet."""
    # Samma mönster som plot_weight, bara protein istället för vikt
    selected_logs = profile.get_logs(days)

    if len(selected_logs) < 2:
        print("Det behövs minst två loggar för att rita ett diagram.")
        return

    logs_by_date = {}
    for log in selected_logs:
        logs_by_date[log.date] = log

    sorted_dates = sorted(logs_by_date)

    sorted_logs = []
    for date in sorted_dates:
        sorted_logs.append(logs_by_date[date])

    dates = []
    proteins = []
    for log in sorted_logs:
        dates.append(log.date)
        proteins.append(log.protein)

    average_dates = []
    average_proteins = []
    for i in range(len(sorted_logs)):
        if i >= 6:
            total = 0
            for j in range(i - 6, i + 1):
                total = total + sorted_logs[j].protein
            average_dates.append(sorted_logs[i].date)
            average_proteins.append(total / 7)

    plt.figure(figsize=(10, 5))
    plt.plot(dates, proteins, marker="o", label="Loggat protein")

    if len(average_proteins) > 0:
        plt.plot(average_dates, average_proteins, linewidth=2, label="Sjudagarssnitt")

    plt.axhline(y=profile.protein_goal(), linestyle="--", label="Proteinmål")

    plt.title(f"Proteinintag för {profile.name}")
    plt.xlabel("Datum")
    plt.ylabel("Protein i gram")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_steps(profile, days=30):
    """Visar ett diagram över antal steg, med loggade steg per dag,
    rullande sjudagarssnitt och stegmålet."""
    # Samma mönster som plot_weight, bara steg istället för vikt
    selected_logs = profile.get_logs(days)

    if len(selected_logs) < 2:
        print("Det behövs minst två loggar för att rita ett diagram.")
        return

    logs_by_date = {}
    for log in selected_logs:
        logs_by_date[log.date] = log

    sorted_dates = sorted(logs_by_date)

    sorted_logs = []
    for date in sorted_dates:
        sorted_logs.append(logs_by_date[date])

    dates = []
    steps = []
    for log in sorted_logs:
        dates.append(log.date)
        steps.append(log.steps)

    average_dates = []
    average_steps = []
    for i in range(len(sorted_logs)):
        if i >= 6:
            total = 0
            for j in range(i - 6, i + 1):
                total = total + sorted_logs[j].steps
            average_dates.append(sorted_logs[i].date)
            average_steps.append(total / 7)

    plt.figure(figsize=(10, 5))
    plt.plot(dates, steps, marker="o", label="Loggade steg")

    if len(average_steps) > 0:
        plt.plot(average_dates, average_steps, linewidth=2, label="Sjudagarssnitt")

    plt.axhline(y=profile.step_goal, linestyle="--", label="Stegmål")

    plt.title(f"Steg för {profile.name}")
    plt.xlabel("Datum")
    plt.ylabel("Antal steg")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()
