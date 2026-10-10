"""Filhantering (JSON, CSV) och diagram för CutTrack.
Importeras i cuttrack.ipynb med:
from analysis import (make_filename, make_csv_filename,
                       save_profile, load_profile, profile_file_exists,
                       export_logs_csv, import_logs_csv,
                       plot_weight, plot_protein, plot_steps)"""
import errno
import json
import csv
import os
import matplotlib.pyplot as plt

from models import DailyLog, CutProfile


ALLOWED_CHARACTERS = "abcdefghijklmnopqrstuvwxyz0123456789"

# Kolumnerna i CSV-filen, i den ordning exporten skriver dem. Importen kräver att alla
# finns i rubrikraden men bryr sig inte om i vilken ordning de står.
CSV_COLUMNS = ["date", "weight", "calories", "protein", "steps", "trained", "waist"]

# Svensk text för de vanligaste filfelen, per felkod (errno). Koden är densamma på alla
# datorer, men texten som operativsystemet ger är engelsk och skiljer sig mellan datorer.
OS_ERROR_TEXTS = {
    errno.EACCES: "Programmet har inte tillåtelse att använda filen eller mappen, "
                  "eller så används filen av ett annat program.",
    errno.EPERM: "Programmet har inte tillåtelse att använda filen eller mappen, "
                 "eller så används filen av ett annat program.",
    errno.EISDIR: "Det finns en mapp med samma namn som filen.",
    errno.ENOTDIR: "En del av sökvägen är en fil, inte en mapp.",
    errno.ENOENT: "Filen eller mappen finns inte.",
    errno.ENOSPC: "Disken är full.",
    errno.EROFS: "Disken eller mappen är skrivskyddad.",
    errno.ENAMETOOLONG: "Filnamnet är för långt.",
}


def make_safe_name(name):
    """Bygger den säkra delen av ett filnamn från användarens namn.
    Behåller bara a till z och siffror, allt annat tas bort."""
    safe_name = ""
    for character in name.lower():
        if character in ALLOWED_CHARACTERS:
            safe_name = safe_name + character

    # Fallback om namnet bara bestod av tecken som togs bort
    if safe_name == "":
        safe_name = "anvandare"

    return safe_name


def is_usable_name(name):
    """True om det går att bygga ett eget filnamn av namnet, det vill säga om minst ett tecken
    a till z eller en siffra finns kvar. Ett namn där inget finns kvar får reservnamnet
    anvandare i make_safe_name, och skulle dela profilfil med alla andra sådana namn."""
    for character in name.lower():
        if character in ALLOWED_CHARACTERS:
            return True
    return False


def make_filename(name):
    """Bygger filnamnet för användarens profil, till exempel annaberg.json."""
    return make_safe_name(name) + ".json"


def make_csv_filename(name):
    """Bygger filnamnet för användarens CSV-export, till exempel annaberg_loggar.csv.
    Varje användare får ett eget namn, så att exporter från olika användare
    inte skriver över varandra."""
    return make_safe_name(name) + "_loggar.csv"


def describe_os_error(error):
    """Svensk text för ett OSError, i stället för operativsystemets engelska text. Ett fel som
    inte finns i OS_ERROR_TEXTS, eller som saknar felkod, visas med sin ursprungliga text."""
    text = OS_ERROR_TEXTS.get(error.errno)
    if text is None:
        return str(error)
    return text


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

    # Skrivs först till en temporär fil, och den får bytas mot den riktiga profilfilen först
    # när allt är skrivet. Ett fel mitt i skrivningen lämnar då den gamla profilfilen orörd,
    # i stället för en halv fil. Punkten i namnet gör att det aldrig kan bli en annan
    # användares profilfil, eftersom make_safe_name tar bort punkter.
    temp_filename = make_safe_name(profile.name) + ".tmp.json"

    # OSError fångar problem med själva skrivningen, till exempel att disken
    # är full eller att mappen saknar skrivrättigheter
    try:
        with open(temp_filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        # os.replace byter ut den gamla filen mot den nya i ett enda steg, och ersätter en
        # fil som redan finns på alla datorer (os.rename kastar FileExistsError på Windows)
        os.replace(temp_filename, filename)
        print(f"Profilen sparades i {filename}.")
        return True
    except OSError as error:
        print(f"Profilen kunde inte sparas: {describe_os_error(error)}")
        # Den halvskrivna temporära filen tas bort. Går inte det heller blir den kvar och
        # skrivs över vid nästa sparning.
        try:
            os.remove(temp_filename)
        except OSError:
            pass
        return False


def profile_file_exists(name):
    """Säger om det finns en profilfil för namnet, oavsett om den går att läsa. load_profile
    ger None både när filen saknas och när den inte går att läsa. Menyn behöver skilja dem
    åt, eftersom en ny profil bara får skapas när filen saknas, annars skriver den över
    den trasiga filen."""
    return os.path.exists(make_filename(name))


def load_profile(name):
    """Läser en profil från JSON. Returnerar None om filen saknas eller inte går att läsa."""
    filename = make_filename(name)

    # Att filen saknas är inte ett fel, det är normalt för en ny användare
    if not profile_file_exists(name):
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

    # Flera skilda except-block, inte ett gemensamt, eftersom felen betyder olika
    # saker och kräver olika åtgärder av användaren. JSONDecodeError och UnicodeDecodeError
    # är båda sorters ValueError, så de måste stå före ValueError, annars når de aldrig fram.
    except json.JSONDecodeError:
        # Filen finns men innehållet är inte giltig JSON, t.ex. redigerad för hand
        print(f"Filen {filename} är skadad och kunde inte läsas.")
        return None
    except UnicodeDecodeError:
        # Filen är sparad i en annan teckenkodning än UTF-8, t.ex. av ett annat program
        print(f"Filen {filename} är inte sparad som UTF-8 och kunde inte läsas.")
        return None
    except KeyError as error:
        # Giltig JSON men saknar ett fält koden förväntar sig, t.ex. en äldre filversion
        print(f"Filen {filename} saknar fältet {error}.")
        return None
    except TypeError:
        # Giltig JSON men fel form, till exempel en lista i stället för ett objekt, eller
        # null där en lista med loggar skulle stå
        print(f"Filen {filename} har fel uppbyggnad och kunde inte läsas som en profil.")
        return None
    except ValueError as error:
        # Fälten finns men värdena är orimliga, DailyLog eller CutProfile vägrar dem
        print(f"Filen {filename} innehåller ogiltiga värden: {error}")
        return None
    except OSError as error:
        # Filen finns men går inte att öppna eller läsa, till exempel en mapp med profilfilens
        # namn eller en fil utan läsrättigheter
        print(f"Filen {filename} kunde inte läsas: {describe_os_error(error)}")
        return None


def export_logs_csv(profile, filename=None):
    """Sparar alla loggar som CSV. Utan filnamn används användarens eget
    standardnamn, till exempel annaberg_loggar.csv."""
    # None betyder att inget filnamn angavs. Standardnamnet byggs här i stället
    # för i parametern, eftersom det beror på vilken användare som exporteras
    if filename is None:
        filename = make_csv_filename(profile.name)

    if len(profile.logs) == 0:
        print("Det finns inga loggar att exportera.")
        return False

    # newline="" krävs av csv-modulen, annars kan filen få extra tomrader på Windows
    try:
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(CSV_COLUMNS)

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
        print(f"Loggarna kunde inte exporteras: {describe_os_error(error)}")
        return False


def parse_number(text, label, is_integer=False):
    """Gör om texten i en CSV-cell till ett tal. Kastar ValueError med svensk text som nämner
    kolumnen och vad som stod i cellen, i stället för Pythons engelska felmeddelande."""
    # Allt som läses från CSV är text, även talen, därför float() och int()
    try:
        if is_integer:
            return int(text)
        return float(text)
    except ValueError:
        if is_integer:
            number_kind = "ett heltal"
        else:
            number_kind = "ett tal"
        raise ValueError(f"{label} måste vara {number_kind}, men raden har '{text}'.")


def parse_trained(text):
    """Gör om texten i kolumnen för träning till True eller False. Versaler och mellanslag
    spelar ingen roll, men inget annat än true och false godtas. Då blir en felstavning
    ett meddelande i stället för ett tyst nej."""
    cleaned_text = text.strip().lower()
    if cleaned_text == "true":
        return True
    if cleaned_text == "false":
        return False
    raise ValueError(f"Träning måste vara True eller False, men raden har '{text}'.")


def is_empty_row(row):
    """True om alla celler i raden är tomma, till exempel en rad som bara är ,,,,,,"""
    for cell in row.values():
        if cell.strip() != "":
            return False
    return True


def make_log_from_row(row):
    """Bygger en DailyLog från en rad i CSV-filen, en dictionary från csv.DictReader.
    Kastar ValueError med svensk text om raden inte går att läsa. Returnerar None för en
    rad där alla celler är tomma."""
    # DictReader fyller på med None när en rad har färre celler än rubrikraden, och samlar
    # de överskjutande cellerna i en lista under nyckeln None. Båda betyder att cellerna kan
    # ha hamnat under fel kolumn, till exempel av en decimalkomma, så raden används inte alls.
    if None in row:
        raise ValueError("Raden har fler värden än rubrikraden. "
                         "Ett decimaltecken som komma kan orsaka det.")
    if None in row.values():
        raise ValueError("Raden har färre värden än rubrikraden.")

    if is_empty_row(row):
        return None

    # Kolumnerna kontrolleras i samma ordning som i filen. Datumet kontrolleras av DailyLog.
    weight = parse_number(row["weight"], "Vikt")
    calories = parse_number(row["calories"], "Kalorier")
    protein = parse_number(row["protein"], "Protein")
    steps = parse_number(row["steps"], "Steg", True)
    trained = parse_trained(row["trained"])

    waist_text = row["waist"].strip()
    if waist_text == "":
        waist = None
    else:
        waist = parse_number(waist_text, "Midjemått")

    # Mellanslag runt datumet tas bort av normalize_date
    return DailyLog(row["date"], weight, calories, protein, steps, trained, waist)


def import_logs_csv(profile, filename=None):
    """Läser in loggar från en CSV-fil och lägger till dem på profilen.
    Utan filnamn läses användarens eget standardnamn, samma som exporten använder.
    Går det fel på hela filen läses ingenting in. En rad med ogiltiga värden hoppas över,
    resten läses in. Returnerar antalet inlästa loggar."""
    if filename is None:
        filename = make_csv_filename(profile.name)

    if not os.path.exists(filename):
        print(f"Filen {filename} hittades inte.")
        return 0

    # Hela filen läses innan någon rad används. Går något fel vid läsningen, till exempel att
    # filen inte är UTF-8 långt ner, har ingen logg hunnit läggas till, så profilen är orörd.
    try:
        # utf-8-sig läser vanlig UTF-8 och hoppar över en BOM om filen börjar med en
        with open(filename, "r", newline="", encoding="utf-8-sig") as file:
            # DictReader läser varje rad som en dictionary, med kolumnnamnen från
            # första raden som nycklar, så ordningen på kolumnerna spelar ingen roll
            reader = csv.DictReader(file)
            column_names = reader.fieldnames
            rows = list(reader)
    except UnicodeDecodeError:
        print(f"Filen {filename} är inte sparad som UTF-8 och kunde inte läsas. "
              "Spara om den som UTF-8 och försök igen.")
        return 0
    except csv.Error:
        print(f"Filen {filename} kunde inte tolkas som en CSV-fil.")
        return 0
    except OSError as error:
        print(f"Filen kunde inte läsas: {describe_os_error(error)}")
        return 0

    # En tom fil ger None som kolumnnamn, och en fil som börjar med en tom rad ger en tom lista
    if column_names is None or len(column_names) == 0:
        print(f"Filen {filename} är tom eller saknar rubrikrad.")
        return 0

    # Med semikolon mellan kolumnerna ser csv-modulen hela rubrikraden som ett enda namn
    if ";" in column_names[0]:
        print(f"Filen {filename} verkar ha semikolon mellan kolumnerna. "
              "CutTrack läser komma mellan kolumnerna och punkt som decimaltecken.")
        return 0

    missing_columns = []
    for column_name in CSV_COLUMNS:
        if column_name not in column_names:
            missing_columns.append(column_name)

    if len(missing_columns) > 0:
        print(f"Filen {filename} saknar kolumnerna: {', '.join(missing_columns)}. "
              f"Förväntade kolumner: {', '.join(CSV_COLUMNS)}.")
        return 0

    imported_count = 0

    for row in rows:
        # try/except inne i loopen, så en trasig rad inte stoppar hela importen
        try:
            log = make_log_from_row(row)
            if log is not None:
                profile.add_log(log)
                imported_count = imported_count + 1
        except ValueError as error:
            print(f"Hoppade över en rad med ogiltiga värden: {error}")

    print(f"{imported_count} loggar lästes in från {filename}.")
    return imported_count


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
