"""Tester för analysis.py: filnamn, profilfiler (JSON) och loggar som CSV.

Diagramfunktionerna (plot_weight, plot_protein, plot_steps) och menyn i notebooken
testas inte här.

Funktionerna skriver och läser filer i den aktuella mappen. Varje test körs därför i en
egen tom tillfällig mapp (se work_in_temp_folder), så inga testfiler hamnar i repot.
Alla namn och värden är påhittade.
"""
import csv
import errno
import json
import os

import pytest

import analysis
from analysis import (make_safe_name, is_usable_name, make_filename, make_csv_filename,
                      describe_os_error, save_profile, load_profile, profile_file_exists,
                      export_logs_csv, import_logs_csv)
from models import DailyLog, CutProfile


@pytest.fixture(autouse=True)
def work_in_temp_folder(tmp_path, monkeypatch):
    """Kör varje test i en egen tom mapp.

    tmp_path är en ny tillfällig mapp för varje test, och monkeypatch.chdir byter
    arbetsmapp till den och ställer tillbaka den efteråt. autouse=True gör att fixturen
    gäller alla tester i filen, även ett test som glömmer be om den."""
    monkeypatch.chdir(tmp_path)


CSV_HEADER = "date,weight,calories,protein,steps,trained,waist\n"


def make_profile(name="Anna Berg", with_logs=True):
    """En profil med målvärden som skiljer sig från standardvärdena, så att de också
    måste följa med genom en sparning. Med with_logs finns två loggar: en utan
    midjemått och en med."""
    profile = CutProfile(name, 170, 35, "kvinna", 1.4, 70.0, "2026-09-01",
                         goal_weight=62.0, target_rate_percent=0.8,
                         protein_goal_per_kg=2.0, step_goal=9000, training_goal_days=4)
    if with_logs:
        profile.logs.append(DailyLog("2026-09-01", 70.0, 2000, 120, 7000, True))
        profile.logs.append(DailyLog("2026-09-02", 69.6, 1900, 110, 9000, False, 71.5))
    return profile


def profile_as_dict(profile):
    """Profilens fält som en dictionary. Två profiler går då att jämföra, och ett fel
    visar vilket fält som skiljer."""
    return {
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
    }


def logs_as_dicts(logs):
    """Samma sak för en lista med loggar."""
    result = []
    for log in logs:
        result.append({
            "date": log.date,
            "weight": log.weight,
            "calories": log.calories,
            "protein": log.protein,
            "steps": log.steps,
            "trained": log.trained,
            "waist": log.waist,
        })
    return result


def read_json(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file)


def write_text(filename, text):
    with open(filename, "w", newline="", encoding="utf-8") as file:
        file.write(text)


def write_bytes(filename, raw_bytes):
    """Skriver exakta bytes, för filer som inte är UTF-8."""
    with open(filename, "wb") as file:
        file.write(raw_bytes)


def read_bytes(filename):
    """Filens exakta innehåll, för att kontrollera att en fil inte ändrats."""
    with open(filename, "rb") as file:
        return file.read()


def read_csv_rows(filename):
    with open(filename, "r", newline="", encoding="utf-8") as file:
        return list(csv.reader(file))


# ---------------------------------------------------------------------------
# Filnamn (F4, F8)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name, expected", [
    ("Anna Berg", "annaberg"),          # versaler blir gemener, mellanslag tas bort
    ("ANNA", "anna"),
    ("anna_berg-3", "annaberg3"),       # siffror behålls, andra tecken tas bort
    ("Åsa Öberg", "saberg"),            # å, ä och ö ingår inte i a till z
    ("../../etc/passwd", "etcpasswd"),  # punkter och snedstreck tas bort
    ("", "anvandare"),                  # inget kvar: reservnamnet används
    ("!!!", "anvandare"),
    ("Åäö", "anvandare"),
])
def test_make_safe_name_keeps_only_a_to_z_and_digits(name, expected):
    assert make_safe_name(name) == expected


def test_make_safe_name_keeps_every_letter_and_digit():
    # Alfabetet och siffrorna är skrivna ut här i stället för hämtade från analysis.py,
    # så att ett tecken som försvinner därifrån upptäcks
    allowed = "abcdefghijklmnopqrstuvwxyz0123456789"
    assert make_safe_name(allowed) == allowed


def test_profile_and_csv_filenames_are_built_from_the_safe_name():
    assert make_filename("Anna Berg") == "annaberg.json"
    assert make_csv_filename("Anna Berg") == "annaberg_loggar.csv"


def test_filenames_use_the_fallback_name_when_nothing_is_left():
    assert make_filename("!!!") == "anvandare.json"
    assert make_csv_filename("!!!") == "anvandare_loggar.csv"


@pytest.mark.parametrize("name, expected", [
    ("Anna Berg", True),
    ("ANNA", True),             # versaler räknas, make_safe_name gör dem till gemener
    ("a", True),
    ("7", True),                # en siffra räcker
    ("Åsa", True),              # s och a finns kvar
    ("Anna!!!", True),
    ("anvandare", True),        # samma text som reservnamnet, men ett riktigt namn
    ("", False),
    ("   ", False),
    ("!!!", False),
    ("Åäö", False),             # inget av tecknen finns i a till z
    ("---", False),
])
def test_is_usable_name_needs_a_letter_a_to_z_or_a_digit(name, expected):
    # N1: ett namn där inget finns kvar får reservnamnet anvandare, och blir därmed samma
    # profilfil som alla andra sådana namn. Menyn frågar om namnet i stället.
    assert is_usable_name(name) is expected


@pytest.mark.parametrize("name", ["", "!!!", "Åäö"])
def test_a_name_that_is_not_usable_is_the_one_that_gets_the_fallback_filename(name):
    assert is_usable_name(name) is False
    assert make_filename(name) == "anvandare.json"


# ---------------------------------------------------------------------------
# describe_os_error: filfel på svenska (N1)
# ---------------------------------------------------------------------------
# Förut visades operativsystemets egen text, till exempel "[Errno 13] Permission denied:
# 'annaberg.json'". Koden bakom felet (errno) är densamma på alla datorer, men texten är det
# inte, så testerna bygger felen själva med en påhittad engelsk text och kontrollerar att
# den inte följer med.

# Samma text för EACCES och EPERM. På Windows ger en fil som är öppen i ett annat program, till
# exempel en CSV-fil i Excel, också ett fel med den koden.
PERMISSION_TEXT = ("Programmet har inte tillåtelse att använda filen eller mappen, "
                   "eller så används filen av ett annat program.")


@pytest.mark.parametrize("code, expected_text", [
    (errno.EACCES, PERMISSION_TEXT),
    (errno.EPERM, PERMISSION_TEXT),
    (errno.EISDIR, "Det finns en mapp med samma namn som filen."),
    (errno.ENOTDIR, "En del av sökvägen är en fil, inte en mapp."),
    (errno.ENOENT, "Filen eller mappen finns inte."),
    (errno.ENOSPC, "Disken är full."),
    (errno.EROFS, "Disken eller mappen är skrivskyddad."),
    (errno.ENAMETOOLONG, "Filnamnet är för långt."),
])
def test_describe_os_error_gives_swedish_text_for_the_common_errors(code, expected_text):
    error = OSError(code, "Some English text from the system")

    assert describe_os_error(error) == expected_text


def test_describe_os_error_keeps_the_original_text_for_an_error_it_does_not_know():
    # Okända fel visas som de är i stället för att gömmas bakom ett påhittat meddelande
    error = OSError(errno.EIO, "Input/output error")

    assert "Input/output error" in describe_os_error(error)


def test_describe_os_error_handles_an_error_without_an_error_code():
    assert describe_os_error(OSError("Disken är full")) == "Disken är full"


# ---------------------------------------------------------------------------
# save_profile och load_profile (F3)
# ---------------------------------------------------------------------------

def test_save_profile_writes_a_file_named_after_the_user(capsys):
    assert save_profile(make_profile("Anna Berg")) is True
    assert os.path.exists("annaberg.json")
    assert "Profilen sparades i annaberg.json." in capsys.readouterr().out


def test_saved_profile_loads_back_unchanged(capsys):
    original = make_profile()
    save_profile(original)
    loaded = load_profile("Anna Berg")
    assert loaded is not None
    assert profile_as_dict(loaded) == profile_as_dict(original)
    assert logs_as_dicts(loaded.logs) == logs_as_dicts(original.logs)
    assert "Profilen för Anna Berg laddades, 2 loggar." in capsys.readouterr().out


def test_swedish_characters_survive_a_save_and_load():
    save_profile(make_profile("Åsa Öberg"))
    with open("saberg.json", "r", encoding="utf-8") as file:
        assert "Åsa Öberg" in file.read()  # sparad som läsbar text, inte som Å
    assert load_profile("Åsa Öberg").name == "Åsa Öberg"


def test_a_profile_is_found_regardless_of_how_the_name_is_typed():
    save_profile(make_profile("Anna Berg"))
    loaded = load_profile("ANNA berg")
    assert loaded is not None
    assert loaded.name == "Anna Berg"


def test_save_profile_cannot_write_outside_the_current_folder(tmp_path):
    save_profile(make_profile("../evil"))
    assert (tmp_path / "evil.json").exists()
    assert not (tmp_path.parent / "evil.json").exists()


def test_save_profile_reports_when_the_file_cannot_be_written(capsys):
    os.mkdir("annaberg.json")  # en mapp med filens namn gör att skrivningen misslyckas
    assert save_profile(make_profile()) is False
    assert "Profilen kunde inte sparas:" in capsys.readouterr().out
    assert os.listdir(".") == ["annaberg.json"]  # ingen temporär fil blev kvar


def test_save_profile_explains_a_full_disk_in_swedish(monkeypatch, capsys):
    def failing_dump(data, file, **options):
        raise OSError(errno.ENOSPC, "No space left on device")

    monkeypatch.setattr(analysis.json, "dump", failing_dump)

    assert save_profile(make_profile()) is False

    out = capsys.readouterr().out
    assert "Profilen kunde inte sparas: Disken är full." in out
    assert "No space left" not in out


def test_save_profile_explains_a_refused_rename_in_swedish(monkeypatch, capsys):
    def failing_replace(source, destination):
        raise OSError(errno.EACCES, "Permission denied")

    monkeypatch.setattr(analysis.os, "replace", failing_replace)

    assert save_profile(make_profile()) is False

    out = capsys.readouterr().out
    assert f"Profilen kunde inte sparas: {PERMISSION_TEXT}" in out
    assert "Permission denied" not in out


def test_save_profile_shows_no_python_error_text_when_a_folder_takes_the_name(capsys):
    os.mkdir("annaberg.json")

    assert save_profile(make_profile()) is False

    # "[Errno 21] Is a directory" och liknande är Pythons text, inte programmets
    assert "Errno" not in capsys.readouterr().out


# N3: sparningen skriver först till annaberg.tmp.json och byter namn när allt är skrivet,
# så att ett fel mitt i skrivningen inte förstör den profil som redan ligger på disk

def test_save_profile_leaves_no_temp_file_behind():
    save_profile(make_profile())
    assert os.listdir(".") == ["annaberg.json"]


def test_save_profile_replaces_the_old_file_with_the_new_content():
    profile = make_profile(with_logs=False)
    save_profile(profile)
    profile.logs.append(DailyLog("2026-09-03", 69.0, 1900, 110, 8000, True))

    save_profile(profile)

    assert [log["date"] for log in read_json("annaberg.json")["logs"]] == ["2026-09-03"]
    assert os.listdir(".") == ["annaberg.json"]


def test_save_profile_overwrites_a_temp_file_left_by_an_earlier_crash():
    write_text("annaberg.tmp.json", "halvskriven rest")
    assert save_profile(make_profile()) is True
    assert os.listdir(".") == ["annaberg.json"]
    assert len(load_profile("Anna Berg").logs) == 2


def test_save_profile_keeps_the_old_file_when_writing_fails_halfway(monkeypatch, capsys):
    # Förut öppnades profilfilen direkt för skrivning, och det tömmer den. Ett fel mitt i
    # skrivningen (full disk, ett urdraget USB-minne) lämnade en halv fil och förstörde
    # profilen som redan var sparad.
    save_profile(make_profile())
    old_content = read_bytes("annaberg.json")
    capsys.readouterr()
    written_to = []

    def failing_dump(data, file, **options):
        written_to.append(file.name)
        file.write('{"name": "Anna Be')  # en halvskriven fil
        raise OSError("Disken är full")

    monkeypatch.setattr(analysis.json, "dump", failing_dump)
    changed_profile = make_profile()
    changed_profile.logs.append(DailyLog("2026-09-03", 69.0, 1900, 110, 8000, True))

    assert save_profile(changed_profile) is False

    assert written_to == ["annaberg.tmp.json"]
    assert read_bytes("annaberg.json") == old_content
    assert os.listdir(".") == ["annaberg.json"]  # den halvskrivna temporära filen är borttagen
    assert "Profilen kunde inte sparas: Disken är full" in capsys.readouterr().out


def test_save_profile_keeps_the_old_file_when_the_rename_fails(monkeypatch, capsys):
    save_profile(make_profile())
    old_content = read_bytes("annaberg.json")
    capsys.readouterr()

    def failing_replace(source, destination):
        raise OSError("Åtkomst nekad")

    monkeypatch.setattr(analysis.os, "replace", failing_replace)

    assert save_profile(make_profile(with_logs=False)) is False

    assert read_bytes("annaberg.json") == old_content
    assert os.listdir(".") == ["annaberg.json"]
    assert "Profilen kunde inte sparas: Åtkomst nekad" in capsys.readouterr().out


def test_save_profile_reports_it_when_the_temp_file_can_neither_be_written_nor_removed(capsys):
    save_profile(make_profile())
    old_content = read_bytes("annaberg.json")
    os.mkdir("annaberg.tmp.json")  # en mapp med temp-filens namn: går varken att skriva eller ta bort
    capsys.readouterr()

    assert save_profile(make_profile(with_logs=False)) is False

    assert read_bytes("annaberg.json") == old_content
    assert os.path.isdir("annaberg.tmp.json")
    assert "Profilen kunde inte sparas:" in capsys.readouterr().out


def test_load_profile_returns_none_when_there_is_no_file(capsys):
    assert load_profile("Finns Inte") is None
    assert "Ingen sparad profil hittades för Finns Inte." in capsys.readouterr().out


def test_profile_file_exists_tells_a_missing_file_from_one_that_cannot_be_read():
    # load_profile ger None i båda fallen. Menyn behöver skilja dem åt, för en ny profil får
    # bara skapas när filen saknas, annars skulle den skriva över den trasiga filen.
    assert profile_file_exists("Anna Berg") is False
    write_text("annaberg.json", "{ detta är inte JSON")
    assert profile_file_exists("Anna Berg") is True
    assert profile_file_exists("ANNA berg") is True  # samma filnamn oavsett hur namnet skrivs


def test_load_profile_reports_a_damaged_file(capsys):
    write_text("annaberg.json", "{ detta är inte JSON")
    assert load_profile("Anna Berg") is None
    assert "Filen annaberg.json är skadad och kunde inte läsas." in capsys.readouterr().out


def test_load_profile_reports_a_missing_field(capsys):
    save_profile(make_profile())
    data = read_json("annaberg.json")
    del data["goal_weight"]
    write_json("annaberg.json", data)
    assert load_profile("Anna Berg") is None
    assert "Filen annaberg.json saknar fältet 'goal_weight'." in capsys.readouterr().out


def test_load_profile_reports_invalid_profile_values(capsys):
    save_profile(make_profile())
    data = read_json("annaberg.json")
    data["goal_weight"] = 95.0  # över startvikten 70.0
    write_json("annaberg.json", data)
    assert load_profile("Anna Berg") is None
    assert ("Filen annaberg.json innehåller ogiltiga värden: "
            "Målvikten måste vara lägre än startvikten.") in capsys.readouterr().out


def test_load_profile_reports_invalid_log_values(capsys):
    save_profile(make_profile())
    data = read_json("annaberg.json")
    data["logs"][0]["weight"] = 0
    write_json("annaberg.json", data)
    assert load_profile("Anna Berg") is None
    assert "Filen annaberg.json innehåller ogiltiga värden: Vikten" in capsys.readouterr().out


def test_load_profile_reports_a_log_date_that_is_not_a_real_date(capsys):
    save_profile(make_profile())
    data = read_json("annaberg.json")
    data["logs"][1]["date"] = "2026-13-45"
    write_json("annaberg.json", data)
    assert load_profile("Anna Berg") is None
    assert ("Filen annaberg.json innehåller ogiltiga värden: "
            "Datumet måste skrivas som ÅÅÅÅ-MM-DD") in capsys.readouterr().out


def test_load_profile_reports_a_log_date_that_is_missing(capsys):
    # null i JSON blir None i Python
    save_profile(make_profile())
    data = read_json("annaberg.json")
    data["logs"][0]["date"] = None
    write_json("annaberg.json", data)
    assert load_profile("Anna Berg") is None
    assert "Filen annaberg.json innehåller ogiltiga värden: Datumet" in capsys.readouterr().out


def test_load_profile_reports_a_start_date_that_is_not_a_real_date(capsys):
    save_profile(make_profile())
    data = read_json("annaberg.json")
    data["created_date"] = "inte ett datum"
    write_json("annaberg.json", data)
    assert load_profile("Anna Berg") is None
    assert "Filen annaberg.json innehåller ogiltiga värden: Datumet" in capsys.readouterr().out


def test_load_profile_reads_dates_written_without_zeros_and_fixes_them():
    # En profilfil sparad före D1 kan ha datum som 2026-9-1. Den ska gå att läsa in och inte
    # bli oläsbar, och datumen skrivs om med nollor vid inläsningen.
    save_profile(make_profile())
    data = read_json("annaberg.json")
    data["created_date"] = "2026-9-1"
    data["logs"][0]["date"] = "2026-9-1"
    data["logs"][1]["date"] = "2026-9-2"
    write_json("annaberg.json", data)

    loaded = load_profile("Anna Berg")

    assert loaded is not None
    assert loaded.created_date == "2026-09-01"
    assert [log.date for log in loaded.logs] == ["2026-09-01", "2026-09-02"]


# N3: filer som inte går att läsa. Förut kraschade programmet med ett Python-fel för alla
# utom filen i fel teckenkodning, som gav en engelsk text. Nu ger alla ett svenskt
# meddelande och None.

@pytest.mark.parametrize("content", ["[]", '"text"', "null", "5"])
def test_load_profile_reports_a_file_that_is_not_a_profile_object(capsys, content):
    # Giltig JSON, men en lista, text, null eller ett tal i stället för ett objekt med fält
    write_text("annaberg.json", content)
    assert load_profile("Anna Berg") is None
    assert ("Filen annaberg.json har fel uppbyggnad och kunde inte läsas som en profil."
            in capsys.readouterr().out)


@pytest.mark.parametrize("bad_logs", [None, "abc", [5], [[1, 2]]])
def test_load_profile_reports_logs_with_the_wrong_structure(capsys, bad_logs):
    # En loggpost med rätt uppbyggnad men fel värden, till exempel vikten som text, hör inte
    # hit. Den får ett eget meddelande som nämner värdet, se testerna av fälten längre ned.
    save_profile(make_profile())
    data = read_json("annaberg.json")
    data["logs"] = bad_logs
    write_json("annaberg.json", data)
    assert load_profile("Anna Berg") is None
    assert "Filen annaberg.json har fel uppbyggnad" in capsys.readouterr().out


@pytest.mark.parametrize("raw_bytes", [
    pytest.param('{"name": "Åsa"}'.encode("latin-1"), id="latin-1"),  # Å som ett enda byte
    pytest.param('{"name": "Anna"}'.encode("utf-16"), id="utf-16"),   # börjar med ett BOM
])
def test_load_profile_reports_a_file_that_is_not_saved_as_utf8(capsys, raw_bytes):
    # Förut hamnade det här under "ogiltiga värden", med Pythons engelska text om kodeken
    write_bytes("annaberg.json", raw_bytes)
    assert load_profile("Anna Berg") is None
    output = capsys.readouterr().out
    assert "Filen annaberg.json är inte sparad som UTF-8 och kunde inte läsas." in output
    assert "codec" not in output


def test_load_profile_reports_a_file_that_cannot_be_opened(capsys):
    os.mkdir("annaberg.json")  # en mapp med profilfilens namn går inte att läsa som en fil
    assert load_profile("Anna Berg") is None
    assert "Filen annaberg.json kunde inte läsas:" in capsys.readouterr().out


def test_load_profile_shows_no_python_error_text_when_the_file_cannot_be_opened(capsys):
    os.mkdir("annaberg.json")

    assert load_profile("Anna Berg") is None

    assert "Errno" not in capsys.readouterr().out


# N1: fält med fel typ eller orimliga värden i profilfilen. Förut lästes de flesta in utan
# ett ord, och felet kom först där värdet användes, eller aldrig ("sex": 3 räknades som
# kvinna, "trained": "nej" som ja). Nu kontrollerar klasserna dem, och load_profile säger
# att filen innehåller ogiltiga värden och vilket värde det gäller.

PROFILE_FIELD_CASES = [
    pytest.param("name", 5, "Namnet", id="name_is_a_number"),
    pytest.param("name", "", "Namnet", id="name_is_empty"),
    pytest.param("name", None, "Namnet", id="name_is_null"),
    pytest.param("height_cm", "170", "Längden", id="height_as_text"),
    pytest.param("height_cm", 0, "Längden", id="height_is_zero"),
    pytest.param("age", -5, "Åldern", id="age_is_negative"),
    pytest.param("age", 17, "Åldern", id="age_is_under_18"),
    pytest.param("age", 35.5, "Åldern", id="age_has_decimals"),
    pytest.param("sex", 3, "Kön", id="sex_is_a_number"),
    pytest.param("sex", "Kvinna", "Kön", id="sex_has_a_capital"),
    pytest.param("activity_level", "hög", "Aktivitetsnivån", id="activity_as_text"),
    pytest.param("activity_level", 0, "Aktivitetsnivån", id="activity_is_zero"),
    pytest.param("start_weight", "70", "Startvikten", id="start_weight_as_text"),
    pytest.param("goal_weight", "62", "Målvikten", id="goal_weight_as_text"),
    pytest.param("target_rate_percent", "0.8", "Takten", id="rate_as_text"),
    pytest.param("protein_goal_per_kg", "2.0", "Proteinmålet", id="protein_goal_as_text"),
    pytest.param("protein_goal_per_kg", 19, "Proteinmålet", id="protein_goal_too_high"),
    pytest.param("step_goal", "9000", "Stegmålet", id="step_goal_as_text"),
    pytest.param("step_goal", 9000.5, "Stegmålet", id="step_goal_has_decimals"),
    pytest.param("training_goal_days", 9, "Träningsmålet", id="training_goal_too_high"),
]


@pytest.mark.parametrize("field, bad_value, expected_start", PROFILE_FIELD_CASES)
def test_load_profile_reports_a_profile_value_of_the_wrong_type_or_out_of_range(
        capsys, field, bad_value, expected_start):
    save_profile(make_profile())
    data = read_json("annaberg.json")
    data[field] = bad_value
    write_json("annaberg.json", data)

    assert load_profile("Anna Berg") is None

    assert ("Filen annaberg.json innehåller ogiltiga värden: "
            + expected_start) in capsys.readouterr().out


LOG_FIELD_CASES = [
    pytest.param("weight", "70", "Vikten", id="weight_as_text"),
    pytest.param("weight", None, "Vikten", id="weight_is_null"),
    pytest.param("calories", "2000", "Kalorierna", id="calories_as_text"),
    pytest.param("protein", -5, "Proteinet", id="protein_is_negative"),
    pytest.param("protein", "120", "Proteinet", id="protein_as_text"),
    pytest.param("steps", -100, "Stegen", id="steps_are_negative"),
    pytest.param("steps", 7000.5, "Stegen", id="steps_have_decimals"),
    pytest.param("steps", "7000", "Stegen", id="steps_as_text"),
    pytest.param("trained", "nej", "Träning", id="trained_as_text"),
    pytest.param("trained", 1, "Träning", id="trained_as_a_number"),
    pytest.param("trained", None, "Träning", id="trained_is_null"),
    pytest.param("waist", "abc", "Midjemåttet", id="waist_as_text"),
    pytest.param("waist", 5, "Midjemåttet", id="waist_is_5"),
    pytest.param("waist", 0, "Midjemåttet", id="waist_is_zero"),
]


@pytest.mark.parametrize("field, bad_value, expected_start", LOG_FIELD_CASES)
def test_load_profile_reports_a_log_value_of_the_wrong_type_or_out_of_range(
        capsys, field, bad_value, expected_start):
    save_profile(make_profile())
    data = read_json("annaberg.json")
    data["logs"][1][field] = bad_value
    write_json("annaberg.json", data)

    assert load_profile("Anna Berg") is None

    assert ("Filen annaberg.json innehåller ogiltiga värden: "
            + expected_start) in capsys.readouterr().out


@pytest.mark.parametrize("bad_number", [float("nan"), float("inf"), float("-inf")])
def test_load_profile_rejects_nan_and_infinity_in_a_file(capsys, bad_number):
    # Pythons json-modul skriver och läser NaN och Infinity, fast de inte är giltig JSON. En
    # profil som sparats med ett sådant värde ska inte laddas.
    save_profile(make_profile())
    data = read_json("annaberg.json")
    data["logs"][0]["weight"] = bad_number
    write_json("annaberg.json", data)

    assert load_profile("Anna Berg") is None

    assert ("Filen annaberg.json innehåller ogiltiga värden: Vikten"
            in capsys.readouterr().out)


def test_load_profile_rejects_nan_as_the_start_weight(capsys):
    save_profile(make_profile())
    data = read_json("annaberg.json")
    data["start_weight"] = float("nan")
    write_json("annaberg.json", data)

    assert load_profile("Anna Berg") is None

    assert ("Filen annaberg.json innehåller ogiltiga värden: Startvikten"
            in capsys.readouterr().out)


def test_load_profile_reads_a_date_with_spaces_around_it():
    # Ett mellanslag som kommit med när någon redigerade filen för hand ska inte göra
    # profilen oläsbar
    save_profile(make_profile())
    data = read_json("annaberg.json")
    data["logs"][0]["date"] = " 2026-09-01 "
    write_json("annaberg.json", data)

    loaded = load_profile("Anna Berg")

    assert loaded is not None
    assert loaded.logs[0].date == "2026-09-01"


# ---------------------------------------------------------------------------
# export_logs_csv (F8)
# ---------------------------------------------------------------------------

def test_export_without_filename_uses_the_users_own_file(capsys):
    assert export_logs_csv(make_profile("Anna Berg")) is True
    assert os.path.exists("annaberg_loggar.csv")
    assert "2 loggar exporterades till annaberg_loggar.csv." in capsys.readouterr().out


def test_export_writes_a_header_and_one_row_per_log():
    export_logs_csv(make_profile())
    assert read_csv_rows("annaberg_loggar.csv") == [
        ["date", "weight", "calories", "protein", "steps", "trained", "waist"],
        ["2026-09-01", "70.0", "2000", "120", "7000", "True", ""],  # saknad midja: tom cell
        ["2026-09-02", "69.6", "1900", "110", "9000", "False", "71.5"],
    ]


def test_export_says_logg_in_the_singular_for_one_log(capsys):
    profile = make_profile(with_logs=False)
    profile.logs.append(DailyLog("2026-09-01", 70.0, 2000, 120, 7000, True))
    export_logs_csv(profile)
    assert "1 logg exporterades till annaberg_loggar.csv." in capsys.readouterr().out


def test_export_with_a_filename_uses_that_file():
    export_logs_csv(make_profile(), "min_export.csv")
    assert os.path.exists("min_export.csv")
    assert not os.path.exists("annaberg_loggar.csv")


def test_two_users_get_separate_export_files():
    export_logs_csv(make_profile("Anna Berg"))
    export_logs_csv(make_profile("Bo Ek"))
    assert os.path.exists("annaberg_loggar.csv")
    assert os.path.exists("boek_loggar.csv")


def test_export_without_logs_returns_false_and_writes_nothing(capsys):
    assert export_logs_csv(make_profile(with_logs=False)) is False
    assert not os.path.exists("annaberg_loggar.csv")
    assert "Det finns inga loggar att exportera." in capsys.readouterr().out


def test_export_reports_when_the_file_cannot_be_written(capsys):
    os.mkdir("annaberg_loggar.csv")
    assert export_logs_csv(make_profile()) is False
    assert "Loggarna kunde inte exporteras:" in capsys.readouterr().out


def test_export_shows_no_python_error_text_when_the_file_cannot_be_written(capsys):
    os.mkdir("annaberg_loggar.csv")

    assert export_logs_csv(make_profile()) is False

    assert "Errno" not in capsys.readouterr().out


# ---------------------------------------------------------------------------
# import_logs_csv (F8)
# ---------------------------------------------------------------------------

def test_import_without_filename_reads_what_the_export_wrote():
    original = make_profile()
    export_logs_csv(original)
    fresh = make_profile(with_logs=False)
    assert import_logs_csv(fresh) == 2
    assert logs_as_dicts(fresh.logs) == logs_as_dicts(original.logs)


def test_import_converts_each_column_to_the_right_type():
    # Allt i en CSV-fil är text. Kalorier och protein kan ha decimaler, steg är heltal.
    write_text("data.csv", CSV_HEADER
               + "2026-09-01,90.0,2200,150,8000,True,\n"
               + "2026-09-02,89.5,2150.5,150.5,8000,False,88.5\n")
    profile = make_profile(with_logs=False)
    import_logs_csv(profile, "data.csv")

    first, second = profile.logs
    assert first.trained is True
    assert first.waist is None  # en tom cell är ett saknat värde
    assert second.weight == 89.5
    assert second.calories == 2150.5
    assert second.protein == 150.5
    assert second.steps == 8000
    assert second.trained is False
    assert second.waist == 88.5


def test_importing_the_same_file_twice_does_not_duplicate_logs(capsys):
    export_logs_csv(make_profile())
    fresh = make_profile(with_logs=False)
    import_logs_csv(fresh)
    capsys.readouterr()
    import_logs_csv(fresh)
    assert len(fresh.logs) == 2
    assert "uppdaterades" in capsys.readouterr().out


def test_import_reports_a_missing_file(capsys):
    assert import_logs_csv(make_profile(with_logs=False), "finns_inte.csv") == 0
    assert "Filen finns_inte.csv hittades inte." in capsys.readouterr().out


def test_import_without_filename_reports_the_users_missing_file(capsys):
    assert import_logs_csv(make_profile(with_logs=False)) == 0
    assert "Filen annaberg_loggar.csv hittades inte." in capsys.readouterr().out


def test_import_skips_broken_rows_and_reads_the_rest(capsys):
    write_text("trasig.csv", CSV_HEADER
               + "2026-09-01,90.0,2200,150,8000,True,\n"        # bra rad
               + "2026-09-02,abc,2200,150,8000,True,\n"          # vikten är inte ett tal
               + "2026-09-03,0,2200,150,8000,True,\n"            # vikten 0 avvisas
               + "2026-09-04,89.5,99999,150,8000,True,\n"        # kalorierna är orimliga
               + "2026-09-05,89.0,2200,150,12.5,True,\n"         # steg ska vara ett heltal
               + "2026-09-06,88.5,2200,150,8000,False,87.0\n")   # bra rad
    profile = make_profile(with_logs=False)

    assert import_logs_csv(profile, "trasig.csv") == 2

    assert [log.date for log in profile.logs] == ["2026-09-01", "2026-09-06"]
    out = capsys.readouterr().out
    assert out.count("Hoppade över en rad med ogiltiga värden") == 4
    assert "Vikten måste vara ett rimligt tal" in out
    assert "Kalorierna måste vara ett rimligt tal" in out
    assert "Vikt måste vara ett tal, men raden har 'abc'." in out
    assert "Steg måste vara ett heltal, men raden har '12.5'." in out
    assert "2 loggar lästes in från trasig.csv." in out


def test_import_reads_dates_written_without_zeros_and_fixes_them():
    write_text("data.csv", CSV_HEADER
               + "2026-9-1,90.0,2200,150,8000,True,\n"
               + "2026-9-2,89.5,2200,150,8000,False,\n")
    profile = make_profile(with_logs=False)
    assert import_logs_csv(profile, "data.csv") == 2
    assert [log.date for log in profile.logs] == ["2026-09-01", "2026-09-02"]


def test_import_skips_rows_with_a_date_that_is_not_a_real_date(capsys):
    write_text("datum.csv", CSV_HEADER
               + "2026-09-01,90.0,2200,150,8000,True,\n"       # bra rad
               + "2026-13-45,89.5,2200,150,8000,True,\n"       # månad 13 finns inte
               + "inte ett datum,89.0,2200,150,8000,True,\n"   # inget datum alls
               + ",88.5,2200,150,8000,True,\n"                 # datumet saknas
               + "2026-09-05,88.0,2200,150,8000,False,\n")     # bra rad
    profile = make_profile(with_logs=False)

    assert import_logs_csv(profile, "datum.csv") == 2

    assert [log.date for log in profile.logs] == ["2026-09-01", "2026-09-05"]
    out = capsys.readouterr().out
    assert out.count("Hoppade över en rad med ogiltiga värden: "
                     "Datumet måste skrivas som ÅÅÅÅ-MM-DD") == 3
    assert "2 loggar lästes in från datum.csv." in out


# ---------------------------------------------------------------------------
# import_logs_csv, trasiga filer och rader (N3)
#
# Två nivåer. Går det fel på hela filen (fel teckenkodning, ingen rubrikrad, fel
# avgränsare, saknade kolumner) skrivs ett meddelande och ingenting läses in. Går det fel på
# en rad hoppas just den raden över, med ett meddelande, och resten läses in.
# ---------------------------------------------------------------------------

FIRST_ROW = "2026-09-01,90.0,2200,150,8000,True,\n"
SECOND_ROW = "2026-09-02,89.5,2200,150,8000,False,88.5\n"
THIRD_ROW = "2026-09-03,89.0,2200,150,8000,True,\n"


def import_text(text):
    """Skriver texten till data.csv, läser in den i en ny tom profil och returnerar profilen
    och antalet inlästa loggar."""
    write_text("data.csv", text)
    profile = make_profile(with_logs=False)
    imported_count = import_logs_csv(profile, "data.csv")
    return profile, imported_count


def test_import_reads_a_file_that_starts_with_a_bom():
    # En BOM är tre dolda bytes först i en UTF-8-fil. Utan särskild hantering blir den
    # första kolumnens namn "\ufeffdate" i stället för "date", och ingen rad går att läsa.
    profile, imported_count = import_text("\ufeff" + CSV_HEADER + FIRST_ROW + SECOND_ROW)

    with open("data.csv", "rb") as file:
        assert file.read(3) == b"\xef\xbb\xbf"  # filen börjar verkligen med en BOM
    assert imported_count == 2
    assert [log.date for log in profile.logs] == ["2026-09-01", "2026-09-02"]


@pytest.mark.parametrize("line_ending", ["\n", "\r\n", "\r"], ids=["lf", "crlf", "cr"])
def test_import_reads_every_kind_of_line_ending(line_ending):
    text = (CSV_HEADER + FIRST_ROW + SECOND_ROW).replace("\n", line_ending)
    profile, imported_count = import_text(text)
    assert imported_count == 2


@pytest.mark.parametrize("raw_bytes", [
    pytest.param((CSV_HEADER + FIRST_ROW).encode("utf-16"), id="utf16"),
    pytest.param((CSV_HEADER + FIRST_ROW + SECOND_ROW.replace("88.5", "ä")).encode("latin-1"),
                 id="latin1"),
])
def test_import_reports_a_file_that_is_not_utf8(raw_bytes, capsys):
    write_bytes("data.csv", raw_bytes)
    profile = make_profile(with_logs=False)

    assert import_logs_csv(profile, "data.csv") == 0

    assert profile.logs == []
    out = capsys.readouterr().out
    assert "Filen data.csv är inte sparad som UTF-8 och kunde inte läsas." in out


def test_a_file_that_turns_out_not_to_be_utf8_late_imports_nothing():
    # Python läser filen i bitar om cirka 8 kB. Här är de första 300 raderna bra och felet
    # kommer efter den första biten. Ingen rad får ha lästs in då, annars är filen halvt
    # inläst och användaren vet inte vilka rader som saknas.
    rows = ""
    for number in range(300):
        rows = rows + f"2025-{number // 28 + 1:02d}-{number % 28 + 1:02d},90.0,2200,150,8000,True,\n"
    raw_text = CSV_HEADER + rows + SECOND_ROW.replace("88.5", "ä")
    write_bytes("data.csv", raw_text.encode("latin-1"))
    profile = make_profile(with_logs=False)

    assert import_logs_csv(profile, "data.csv") == 0
    assert profile.logs == []


def test_import_reports_a_file_that_cannot_be_read_as_csv(capsys):
    # csv-modulen vägrar fält som är längre än 131072 tecken och kastar csv.Error. En fil
    # som inte alls är en loggfil kan ha en sådan rad.
    profile, imported_count = import_text(
        CSV_HEADER + FIRST_ROW + "x" * 200000 + ",90.0,2200,150,8000,True,\n")

    assert imported_count == 0
    assert profile.logs == []
    assert "Filen data.csv kunde inte tolkas som en CSV-fil." in capsys.readouterr().out


@pytest.mark.parametrize("text", ["", "\n", "\n\n"],
                         ids=["empty", "one_blank_line", "two_blank_lines"])
def test_import_reports_a_file_without_a_header(text, capsys):
    profile, imported_count = import_text(text)

    assert imported_count == 0
    assert "Filen data.csv är tom eller saknar rubrikrad." in capsys.readouterr().out


def test_import_of_a_file_with_only_a_header_reads_zero_logs(capsys):
    profile, imported_count = import_text(CSV_HEADER)

    assert imported_count == 0
    assert "0 loggar lästes in från data.csv." in capsys.readouterr().out


def test_import_reports_a_file_that_uses_semicolons(capsys):
    # Semikolon mellan kolumnerna och decimalkomma. csv-modulen läser rubrikraden som en enda
    # kolumn, och utan särskild hantering ger varje rad ett eget meddelande.
    profile, imported_count = import_text(
        "date;weight;calories;protein;steps;trained;waist\n"
        "2026-09-01;90,5;2200;150;8000;True;\n"
        "2026-09-02;89,5;2200;150;8000;False;88,5\n")

    assert imported_count == 0
    assert profile.logs == []
    out = capsys.readouterr().out
    assert "Filen data.csv verkar ha semikolon mellan kolumnerna." in out
    assert "saknar kolumnerna" not in out  # ett enda meddelande, inte ett till om kolumnerna
    assert "Hoppade över" not in out


def test_import_reports_a_missing_column_once_and_reads_nothing(capsys):
    # En äldre exportfil utan kolumnen för midjemått. Ett meddelande för hela filen,
    # inte ett per rad.
    profile, imported_count = import_text(
        "date,weight,calories,protein,steps,trained\n"
        "2026-09-01,90.0,2200,150,8000,True\n"
        "2026-09-02,89.5,2200,150,8000,False\n")

    assert imported_count == 0
    assert profile.logs == []
    out = capsys.readouterr().out
    assert ("Filen data.csv saknar kolumnerna: waist. "
            "Förväntade kolumner: date, weight, calories, protein, steps, trained, waist.") in out
    assert "Hoppade över" not in out


def test_import_lists_every_missing_column_in_the_expected_order(capsys):
    profile, imported_count = import_text("calories,date,weight\n2200,2026-09-01,90.0\n")

    assert imported_count == 0
    assert "Filen data.csv saknar kolumnerna: protein, steps, trained, waist." in capsys.readouterr().out


def test_import_accepts_columns_in_any_order_and_ignores_extra_columns():
    profile, imported_count = import_text(
        "note,waist,trained,steps,protein,calories,weight,date\n"
        "bra dag,88.5,True,8000,150,2200,90.0,2026-09-01\n")

    assert imported_count == 1
    assert logs_as_dicts(profile.logs) == [{
        "date": "2026-09-01", "weight": 90.0, "calories": 2200.0, "protein": 150.0,
        "steps": 8000, "trained": True, "waist": 88.5}]


@pytest.mark.parametrize("bad_row, expected_message", [
    pytest.param("2026-09-02,89.5,2200\n",
                 "Raden har färre värden än rubrikraden.", id="three_values"),
    pytest.param("2026-09-02,89.5,2200,150,8000,False\n",
                 "Raden har färre värden än rubrikraden.", id="last_cell_missing"),
    pytest.param("2026-09-02,89.5,2200,150,8000,False,88,5\n",
                 "Raden har fler värden än rubrikraden. "
                 "Ett decimaltecken som komma kan orsaka det.", id="decimal_comma_in_last_cell"),
])
def test_import_skips_rows_with_the_wrong_number_of_values(bad_row, expected_message, capsys):
    # Sista fallet: 88,5 skrivet med decimalkomma delas i två celler. Utan kontroll läses
    # 88 in som midjemått och 5 försvinner, utan något meddelande.
    profile, imported_count = import_text(CSV_HEADER + FIRST_ROW + bad_row + THIRD_ROW)

    assert imported_count == 2
    assert [log.date for log in profile.logs] == ["2026-09-01", "2026-09-03"]
    out = capsys.readouterr().out
    assert f"Hoppade över en rad med ogiltiga värden: {expected_message}" in out
    assert "2 loggar lästes in från data.csv." in out


def test_import_ignores_rows_where_every_cell_is_empty(capsys):
    # Rader som bara består av kommatecken kan komma från ett kalkylprogram. De är inte
    # fel, så ingen ska få ett meddelande om dem.
    profile, imported_count = import_text(
        CSV_HEADER + FIRST_ROW + ",,,,,,\n" + "\n" + " , ,,,,,\n" + SECOND_ROW + ",,,,,,\n")

    assert imported_count == 2
    out = capsys.readouterr().out
    assert "Hoppade över" not in out
    assert "2 loggar lästes in från data.csv." in out


@pytest.mark.parametrize("cell, expected", [
    ("True", True), ("true", True), ("TRUE", True), (" True ", True),
    ("False", False), ("false", False), ("FALSE", False), (" False ", False),
])
def test_import_reads_true_and_false_in_any_case(cell, expected):
    # Förut räknades allt utom exakt "True" som nej, så "TRUE" blev ett tyst nej.
    profile, imported_count = import_text(CSV_HEADER + f"2026-09-01,90.0,2200,150,8000,{cell},\n")

    assert imported_count == 1
    assert profile.logs[0].trained is expected


@pytest.mark.parametrize("cell", ["ja", "nej", "1", "0", "yes", "SANT", "FALSKT", "Truee", ""],
                         ids=["ja", "nej", "1", "0", "yes", "sant", "falskt", "truee", "empty"])
def test_import_skips_a_row_where_training_is_not_true_or_false(cell, capsys):
    # Andra stavningar än True och False gissas inte på. Raden hoppas över med ett
    # meddelande i stället för att tyst bli ett nej.
    profile, imported_count = import_text(
        CSV_HEADER + FIRST_ROW + f"2026-09-02,89.5,2200,150,8000,{cell},\n" + THIRD_ROW)

    assert imported_count == 2
    assert [log.date for log in profile.logs] == ["2026-09-01", "2026-09-03"]
    assert ("Hoppade över en rad med ogiltiga värden: "
            f"Träning måste vara True eller False, men raden har '{cell}'.") in capsys.readouterr().out


@pytest.mark.parametrize("bad_row, expected_message", [
    pytest.param("2026-09-02,abc,2200,150,8000,True,\n",
                 "Vikt måste vara ett tal, men raden har 'abc'.", id="weight"),
    pytest.param('2026-09-02,"89,5",2200,150,8000,True,\n',
                 "Vikt måste vara ett tal, men raden har '89,5'.", id="weight_with_decimal_comma"),
    pytest.param("2026-09-02,89.5,2 200,150,8000,True,\n",
                 "Kalorier måste vara ett tal, men raden har '2 200'.", id="calories"),
    pytest.param("2026-09-02,89.5,2200,,8000,True,\n",
                 "Protein måste vara ett tal, men raden har ''.", id="protein_empty"),
    pytest.param("2026-09-02,89.5,2200,150,12.5,True,\n",
                 "Steg måste vara ett heltal, men raden har '12.5'.", id="steps"),
    pytest.param("2026-09-02,89.5,2200,150,8000,True,x\n",
                 "Midjemått måste vara ett tal, men raden har 'x'.", id="waist"),
])
def test_import_says_which_value_is_not_a_number(bad_row, expected_message, capsys):
    # Meddelandet nämner kolumnen och det som stod i cellen, på svenska. Förut visades
    # Pythons egen engelska text, till exempel "could not convert string to float".
    profile, imported_count = import_text(CSV_HEADER + FIRST_ROW + bad_row + THIRD_ROW)

    assert imported_count == 2
    assert [log.date for log in profile.logs] == ["2026-09-01", "2026-09-03"]
    assert f"Hoppade över en rad med ogiltiga värden: {expected_message}" in capsys.readouterr().out


@pytest.mark.parametrize("bad_row, expected_message", [
    pytest.param("2026-09-02,nan,2200,150,8000,True,\n",
                 "Vikten måste vara ett rimligt tal i kilogram", id="weight_nan"),
    pytest.param("2026-09-02,inf,2200,150,8000,True,\n",
                 "Vikten måste vara ett rimligt tal i kilogram", id="weight_inf"),
    pytest.param("2026-09-02,89.5,nan,150,8000,True,\n",
                 "Kalorierna måste vara ett rimligt tal", id="calories_nan"),
    pytest.param("2026-09-02,89.5,2200,-5,8000,True,\n",
                 "Proteinet måste vara ett rimligt tal i gram", id="protein_negative"),
    pytest.param("2026-09-02,89.5,2200,5000,8000,True,\n",
                 "Proteinet måste vara ett rimligt tal i gram", id="protein_too_high"),
    pytest.param("2026-09-02,89.5,2200,150,-100,True,\n",
                 "Stegen måste vara ett heltal", id="steps_negative"),
    pytest.param("2026-09-02,89.5,2200,150,800000,True,\n",
                 "Stegen måste vara ett heltal", id="steps_too_high"),
    pytest.param("2026-09-02,89.5,2200,150,8000,True,5\n",
                 "Midjemåttet måste vara ett rimligt tal i centimeter", id="waist_is_5"),
    pytest.param("2026-09-02,89.5,2200,150,8000,True,nan\n",
                 "Midjemåttet måste vara ett rimligt tal i centimeter", id="waist_nan"),
])
def test_import_skips_rows_with_values_outside_the_limits(bad_row, expected_message, capsys):
    # Gränserna i DailyLog gäller för CSV-filer också. Förut släpptes nan, negativt protein
    # och negativa steg igenom.
    profile, imported_count = import_text(CSV_HEADER + FIRST_ROW + bad_row + THIRD_ROW)

    assert imported_count == 2
    assert [log.date for log in profile.logs] == ["2026-09-01", "2026-09-03"]
    assert f"Hoppade över en rad med ogiltiga värden: {expected_message}" in capsys.readouterr().out


def test_import_trims_spaces_around_the_values():
    profile, imported_count = import_text(
        CSV_HEADER
        + "2026-09-01 , 90.0 , 2200 , 150 , 8000 , True , 88.5 \n"
        + "2026-09-02,89.5,2200,150,8000,False,   \n")

    assert imported_count == 2
    assert profile.logs[0].date == "2026-09-01"
    assert profile.logs[0].trained is True
    assert profile.logs[0].waist == 88.5
    assert profile.logs[1].waist is None  # en cell med bara mellanslag är ett saknat värde


def test_import_reports_when_the_file_cannot_be_read(capsys):
    os.mkdir("annaberg_loggar.csv")  # en mapp med filens namn kan inte läsas som en fil
    assert import_logs_csv(make_profile(with_logs=False)) == 0
    assert "Filen kunde inte läsas:" in capsys.readouterr().out


def test_import_shows_no_python_error_text_when_the_file_cannot_be_read(capsys):
    os.mkdir("annaberg_loggar.csv")

    assert import_logs_csv(make_profile(with_logs=False)) == 0

    assert "Errno" not in capsys.readouterr().out
