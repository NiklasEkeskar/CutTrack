"""Låser vad check_goals skriver ut i dag, och kontrollerar att README visar samma sak.

Det här är tester som låser dagens beteende (på engelska characterization tests): de
beskriver vad programmet gör, inte vad det borde göra. Vikttakten räknas från första och
sista vägningen, och det är en känd brist (F24, se docs/statuslogg.md). När F24 rättas i
Steg 1 ska testerna som hör till takten misslyckas, och då ändras de medvetet:

1. ändra de förväntade raderna här
2. skriv om utskrifterna under Exempel i README.md
3. kör python -m pytest, så bekräftar test_readme_shows_the_same_lines att README och
   koden säger samma sak

Allt som beror på hur takten räknas ligger i den här filen. Övriga tester ska klara bytet.
Förväntade rader för protein, träning och steg ändras inte av F24.

Exemplet är profilen Testperson med de simulerade loggarna i data/exempel_loggar.csv.
"""
from pathlib import Path

import pytest

from analysis import import_logs_csv
from models import CutProfile, DailyLog

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_CSV = ROOT / "data" / "exempel_loggar.csv"
README = ROOT / "README.md"

# Det programmet skriver ut när analysen körs efter 14, 18 och 20 dagar. Det är samma
# rader som README visar under Exempel. Efter 18 dagar visar README bara första raden.
AFTER_14_DAYS = [
    "Vikten: minskar med 1.31 procent per vecka (cirka 1.3 kg), över säkerhetsgränsen "
    "1,0 procent (cirka 1.0 kg för dig). Risk för muskelförlust.",
    "Protein: snitt 211 g mot mål 206 g. Målet nås.",
    "Träning: 5 av 5 förväntade dagar under perioden. Målet nås.",
    "Steg: snitt 10160 mot mål 10000. Målet nås.",
    "",
    "Fokusera på: vikt.",
]

AFTER_18_DAYS = [
    "Vikten: minskar med 0.41 procent per vecka (cirka 0.4 kg), långsammare än ditt mål "
    "på 0.6 procent (cirka 0.6 kg för dig).",
    "Protein: snitt 215 g mot mål 206 g. Målet nås.",
    "Träning: 5 av 5 förväntade dagar under perioden. Målet nås.",
    "Steg: snitt 10270 mot mål 10000. Målet nås.",
    "",
    "Fokusera på: vikt.",
]

AFTER_20_DAYS = [
    "Vikten: minskar med 0.61 procent per vecka (cirka 0.6 kg), vid eller över ditt mål "
    "på 0.6 procent och inom säkerhetsgränsen.",
    "Protein: snitt 213 g mot mål 206 g. Målet nås.",
    "Träning: 5 av 5 förväntade dagar under perioden. Målet nås.",
    "Steg: snitt 9953 mot mål 10000. Under målet.",
    "",
    "Fokusera på: steg.",
]


def make_readme_profile(log_count):
    """Profilen Testperson från README, med de första log_count loggarna ur exempelfilen."""
    profile = CutProfile("Testperson", 189, 39, "man", 1.55, 101.5, "2026-09-17",
                         goal_weight=98.0, target_rate_percent=0.6,
                         protein_goal_per_kg=2.1, step_goal=10000, training_goal_days=5)
    import_logs_csv(profile, str(EXAMPLE_CSV))
    profile.logs = profile.logs[:log_count]
    return profile


def check_goals_lines(profile, capsys):
    """Kör check_goals och returnerar det den skrev ut, rad för rad."""
    capsys.readouterr()  # släng det som skrevs ut innan, till exempel av inläsningen
    profile.check_goals()
    return capsys.readouterr().out.splitlines()


# ---------------------------------------------------------------------------
# README-exemplet
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("log_count, expected_lines", [
    (14, AFTER_14_DAYS),
    (18, AFTER_18_DAYS),
    (20, AFTER_20_DAYS),
], ids=["efter-14-dagar", "efter-18-dagar", "efter-20-dagar"])
def test_check_goals_prints_what_the_readme_shows(log_count, expected_lines, capsys):
    profile = make_readme_profile(log_count)
    assert check_goals_lines(profile, capsys) == expected_lines


def test_readme_shows_the_same_lines():
    # README ska visa det programmet skriver ut. Raderna som saknas listas i felmeddelandet.
    readme_text = README.read_text(encoding="utf-8")
    shown_in_readme = AFTER_14_DAYS + AFTER_18_DAYS[:1] + AFTER_20_DAYS
    missing = []
    for line in shown_in_readme:
        if line != "" and line not in readme_text:
            missing.append(line)
    assert missing == []


def test_example_file_has_the_twenty_logs_the_readme_describes():
    profile = make_readme_profile(20)
    assert len(profile.logs) == 20
    assert profile.logs[0].date == "2026-09-17"
    assert profile.logs[-1].date == "2026-10-06"


def test_calorie_suggestion_matches_the_readme_text(capsys):
    # README: "Programmets kaloriförslag för samma profil blev 2409 kcal per dag"
    # Aktuell vikt är 98.0 kg.
    # BMR  = 980 + 6.25 * 189 - 5 * 39 + 5 = 1971.25
    # TDEE = 1971.25 * 1.55 = 3055.4375
    # Underskott = 98 * 0.6 / 100 = 0.588 kg per vecka, 0.588 * 7700 / 7 = 646.8 kcal per dag
    # Förslag = 3055.4375 - 646.8 = 2408.6375, avrundat 2409
    profile = make_readme_profile(20)
    assert profile.suggest_calorie_goal() == 2409


def test_waist_measurements_match_the_readme_text():
    # README: "Midjemåttet loggades tre gånger och sjönk från 90,0 till 88,2 cm"
    profile = make_readme_profile(20)
    waists = []
    for log in profile.logs:
        if log.waist is not None:
            waists.append(log.waist)
    assert waists == [90.0, 89.0, 88.2]


@pytest.mark.parametrize("log_count, average", [(14, 99.03), (18, 98.26), (20, 98.13)])
def test_weekly_weight_averages_match_the_readme_text(log_count, average):
    # README: veckosnittet sjunker hela tiden (99,03, 98,26 och 98,13 kg)
    profile = make_readme_profile(log_count)
    assert profile.average_weight(7) == pytest.approx(average, abs=0.005)


# ---------------------------------------------------------------------------
# F24: tester som låser dagens takträkning och ändras medvetet i Steg 1
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("last_weight, rate", [(98.8, "1.11"), (98.4, "1.52")])
def test_f24_one_weighing_moves_the_rate(last_weight, rate, capsys):
    # README, Begränsningar: 200 gram mer eller mindre på sista vägningen ger 1,11
    # respektive 1,52 procent per vecka i stället för 1,31. Sista vägningen var 98.6 kg.
    profile = make_readme_profile(14)
    profile.logs[-1].weight = last_weight
    first_line = check_goals_lines(profile, capsys)[0]
    assert first_line.startswith(f"Vikten: minskar med {rate} procent per vecka")


def test_f24_steady_loss_at_the_goal_pace_is_reported_as_too_slow(capsys):
    # Vikten sjunker exakt 0,1 kg per dag, alltså 0,7 kg per vecka eller cirka 0,79 procent
    # av 89 kg. Det är över målet på 0,7 procent (0,62 kg), så raden borde säga "vid eller
    # över ditt mål". Men koden delar skillnaden mellan första och sista vägningen i
    # fönstret (0,6 kg på sex dagar) med sju dagar och får 0,6 / 89 = 0,67 procent, som
    # den kallar "långsammare än ditt mål". Det är F24. När F24 är rättad ska raden i
    # stället säga "vid eller över ditt mål".
    profile = CutProfile("Testperson", 180, 30, "man", 1.5, 90.0, "2026-09-01",
                         goal_weight=80.0, target_rate_percent=0.7)
    weights = [90.0, 89.9, 89.8, 89.7, 89.6, 89.5, 89.4,   # dag 1 till 7
               89.3, 89.2, 89.1, 89.0, 88.9, 88.8, 88.7]   # dag 8 till 14, fönstret
    for day in range(len(weights)):
        date_text = f"2026-09-{day + 1:02d}"
        profile.logs.append(DailyLog(date_text, weights[day], 2200, 200, 9000, True))

    first_line = check_goals_lines(profile, capsys)[0]

    assert first_line == (
        "Vikten: minskar med 0.67 procent per vecka (cirka 0.6 kg), långsammare än ditt mål "
        "på 0.7 procent (cirka 0.6 kg för dig)."
    )
