"""Tester för analysis.py: filnamn, profilfiler (JSON) och loggar som CSV.

Diagramfunktionerna (plot_weight, plot_protein, plot_steps) och menyn i notebooken
testas inte här.

Funktionerna skriver och läser filer i den aktuella mappen. Varje test körs därför i en
egen tom tillfällig mapp (se work_in_temp_folder), så inga testfiler hamnar i repot.
Alla namn och värden är påhittade.
"""
import csv
import json
import os

import pytest

from analysis import (make_safe_name, make_filename, make_csv_filename, save_profile,
                      load_profile, export_logs_csv, import_logs_csv)
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


def test_load_profile_returns_none_when_there_is_no_file(capsys):
    assert load_profile("Finns Inte") is None
    assert "Ingen sparad profil hittades för Finns Inte." in capsys.readouterr().out


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
    assert "2 loggar lästes in från trasig.csv." in out


def test_import_skips_rows_when_a_column_is_missing(capsys):
    # En äldre exportfil utan kolumnen för midjemått
    write_text("gammal.csv",
               "date,weight,calories,protein,steps,trained\n"
               "2026-09-01,90.0,2200,150,8000,True\n"
               "2026-09-02,89.5,2200,150,8000,False\n")
    profile = make_profile(with_logs=False)
    assert import_logs_csv(profile, "gammal.csv") == 0
    out = capsys.readouterr().out
    assert out.count("Hoppade över en rad som saknar kolumnen 'waist'.") == 2
    assert "0 loggar lästes in från gammal.csv." in out


def test_import_reports_when_the_file_cannot_be_read(capsys):
    os.mkdir("annaberg_loggar.csv")  # en mapp med filens namn kan inte läsas som en fil
    assert import_logs_csv(make_profile(with_logs=False)) == 0
    assert "Filen kunde inte läsas:" in capsys.readouterr().out
