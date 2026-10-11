"""Filhantering (JSON, CSV) och diagram för CutTrack.
Importeras i cuttrack.ipynb med:
from analysis import (make_filename, make_csv_filename,
                       save_profile, load_profile, profile_file_exists,
                       export_logs_csv, import_logs_csv,
                       plot_weight, plot_protein, plot_steps)"""
import errno
from datetime import datetime
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


def names_match(first, second):
    """True om två namn är samma namn, oavsett versaler och mellanslag. "Anna Berg" och
    "anna  berg" är samma, men "Anna Berg" och "Annab Erg" är det inte, fast de ger samma
    filnamn."""
    # split() utan argument delar på alla mellanslag och tar bort dem runt orden, och
    # casefold() gör om till gemener, även för bokstäver utanför a till z
    return " ".join(first.split()).casefold() == " ".join(second.split()).casefold()


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


def write_to_disk(file):
    """Tvingar ut det som skrivits till filen till disken innan den byter namn. Annars kan
    datorn hålla innehållet i minnet en stund, och ett strömavbrott strax efter namnbytet
    kan ge en tom fil. flush() tömmer först Pythons egen buffert, eftersom fsync bara skickar
    det som redan lämnat den."""
    file.flush()
    os.fsync(file.fileno())


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
            write_to_disk(file)
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

        for log_number, log_data in enumerate(data["logs"], start=1):
            try:
                log = DailyLog(
                    log_data["date"], log_data["weight"], log_data["calories"],
                    log_data["protein"], log_data["steps"], log_data["trained"],
                    log_data["waist"]
                )
            except ValueError as error:
                # En profilfil kan ha hundratals loggar. Numret och datumet säger vilken som
                # ska rättas, som radnumret i CSV-importen. Ett datum som inte är text visas
                # inte, det är ofta själva felet.
                where = f"logg {log_number}"
                if isinstance(log_data["date"], str):
                    where += f" ({log_data['date'].strip()})"
                print(f"Filen {filename} innehåller ogiltiga värden i {where}: {error}")
                return None
            profile.logs.append(log)

        # Två namn kan ge samma filnamn, till exempel Åke och Äke som båda blir ke.json. Profilen
        # laddas bara om namnet i filen är samma som det som skrevs, annars kunde den ena läsa
        # och skriva över den andras profil. Namnet i filen visas inte, det är en annan persons.
        if not names_match(profile.name, name):
            print(f"Filen {filename} hör till en annan profil, vars namn ger samma filnamn. "
                  "Skriv namnet som när profilen skapades, eller välj ett annat namn.")
            return None

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

    # Skrivs först till en temporär fil bredvid, som i save_profile, så att en export som
    # avbryts mitt i inte förstör den förra kopian. Den temporära filen får samma ändelse,
    # annaberg_loggar.csv blir annaberg_loggar.tmp.csv, så git ignorerar den om den blir kvar.
    root, extension = os.path.splitext(filename)
    temp_filename = root + ".tmp" + extension

    # newline="" krävs av csv-modulen, annars kan filen få extra tomrader på Windows
    try:
        with open(temp_filename, "w", newline="", encoding="utf-8") as file:
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
            write_to_disk(file)
        os.replace(temp_filename, filename)

        if len(profile.logs) == 1:
            print(f"1 logg exporterades till {filename}.")
        else:
            print(f"{len(profile.logs)} loggar exporterades till {filename}.")
        return True

    except OSError as error:
        print(f"Loggarna kunde inte exporteras: {describe_os_error(error)}")
        # Den halvskrivna temporära filen tas bort, som i save_profile
        try:
            os.remove(temp_filename)
        except OSError:
            pass
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
            # Varje rad sparas med sitt radnummer i filen. line_num räknar fysiska rader, även
            # tomma rader som csv-modulen hoppar över, så numret stämmer med filen.
            rows = []
            for row in reader:
                rows.append((reader.line_num, row))
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
    replaced_count = 0
    skipped_count = 0

    for line_number, row in rows:
        # try/except inne i loopen, så en trasig rad inte stoppar hela importen
        try:
            log = make_log_from_row(row)
            if log is not None:
                # Tyst, en sammanfattning skrivs efteråt i stället för en rad per logg
                replaced = profile.add_log(log, announce=False)
                imported_count = imported_count + 1
                if replaced:
                    replaced_count = replaced_count + 1
        except ValueError as error:
            print(f"Hoppade över rad {line_number} med ogiltiga värden: {error}")
            skipped_count = skipped_count + 1

    print_import_summary(filename, imported_count, replaced_count, skipped_count)
    return imported_count


def print_import_summary(filename, imported_count, replaced_count, skipped_count):
    """Sammanfattningen efter en CSV-import, med rätt böjning för en och flera."""
    if imported_count == 1:
        print(f"1 logg lästes in från {filename}.")
    else:
        print(f"{imported_count} loggar lästes in från {filename}.")

    # Importen ersätter loggar med samma datum utan att fråga, så det ska synas
    if replaced_count == 1:
        print("En av dem ersatte en befintlig logg med samma datum.")
    elif replaced_count > 1:
        print(f"{replaced_count} av dem ersatte befintliga loggar med samma datum.")

    if skipped_count == 1:
        print("1 rad hoppades över, se meddelandet ovan.")
    elif skipped_count > 1:
        print(f"{skipped_count} rader hoppades över, se meddelandena ovan.")


def seven_day_averages(dates, values):
    """Rullande sjudagarssnitt för diagrammen. dates är datum som text (ÅÅÅÅ-MM-DD) i
    stigande ordning och values ett värde per datum. Varje punkt är snittet av de värden
    vars datum ligger inom sju kalenderdagar bakåt, dagen själv medräknad. Den första
    punkten kommer sex dagar efter det första datumet, när en hel vecka har gått.
    Returnerar två listor: datumen och snitten."""
    # Kalenderdagar och inte de sju senaste loggarna, som get_logs. Med luckor i
    # loggningen hade sju loggar annars kunnat sträcka sig över flera veckor.
    days = []
    for date_text in dates:
        days.append(datetime.strptime(date_text, "%Y-%m-%d").date())

    average_dates = []
    average_values = []
    for i in range(len(days)):
        if (days[i] - days[0]).days < 6:
            continue
        total = 0
        count = 0
        for j in range(i + 1):
            if (days[i] - days[j]).days <= 6:
                total = total + values[j]
                count = count + 1
        average_dates.append(dates[i])
        average_values.append(total / count)

    return average_dates, average_values


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

    average_dates, average_weights = seven_day_averages(dates, weights)

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

    average_dates, average_proteins = seven_day_averages(dates, proteins)

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

    average_dates, average_steps = seven_day_averages(dates, steps)

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
