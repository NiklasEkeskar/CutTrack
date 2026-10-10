"""Låser vad check_goals skriver ut för README-exemplet, och kontrollerar att README visar
samma sak. Här ligger också allt annat som beror på hur vikttakten räknas (F24).

Takten är skillnaden mellan snittet för den senaste perioden och snittet för perioden före,
omräknad till kilo per vecka. Före F24 räknades den från första och sista vägningen i
perioden, och det gav fel takt (se docs/statuslogg.md). Ändras beräkningen igen ska testerna
här misslyckas, och då ändras de medvetet:

1. ändra de förväntade raderna här
2. skriv om utskrifterna under Exempel i README.md
3. kör python -m pytest, så bekräftar test_readme_shows_the_same_lines att README och
   koden säger samma sak

Testerna i test_models.py kontrollerar bara vilken gren som väljs, med data som ligger långt
från gränserna, och påverkas inte av hur takten räknas. Förväntade rader för protein,
träning och steg beror inte på takten.

Exemplet är profilen Testperson med de simulerade loggarna i data/exempel_loggar.csv.
"""
from datetime import date, timedelta
from pathlib import Path

import pytest

from analysis import import_logs_csv
from models import CutProfile, DailyLog

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_CSV = ROOT / "data" / "exempel_loggar.csv"
README = ROOT / "README.md"

# Det programmet skriver ut när analysen körs efter 14, 18 och 20 dagar. Det är samma
# rader som README visar under Exempel. Efter 18 dagar visar README bara första raden.
#
# Taktraden är uträknad för hand ur data/exempel_loggar.csv. Perioderna är sju dagar, så
# takten blir (summa före - summa senaste) / summa senaste, i procent:
#   14 dagar: dag 1 till 7 summerar 704.7, dag 8 till 14 summerar 693.2.
#             Skillnaden är (704.7 - 693.2) / 7 = 1.64 kg per vecka, 11.5 / 693.2 = 1.66 procent.
#   18 dagar: dag 5 till 11 summerar 698.4, dag 12 till 18 summerar 687.8.
#             Skillnaden är (698.4 - 687.8) / 7 = 1.51 kg per vecka, 10.6 / 687.8 = 1.54 procent.
#   20 dagar: dag 7 till 13 summerar 694.6, dag 14 till 20 summerar 686.9.
#             Skillnaden är (694.6 - 686.9) / 7 = 1.10 kg per vecka, 7.7 / 686.9 = 1.12 procent.
# Säkerhetsgränsen 1,0 procent av snittet (99.03, 98.26 och 98.13 kg) är cirka 1.0 kg.
AFTER_14_DAYS = [
    "Vikten: minskar med 1.66 procent per vecka (cirka 1.6 kg), över säkerhetsgränsen "
    "1,0 procent (cirka 1.0 kg för dig). Risk för muskelförlust.",
    "Protein: snitt 211 g mot mål 206 g. Målet nås.",
    "Träning: 5 av 5 förväntade dagar under perioden. Målet nås.",
    "Steg: snitt 10160 mot mål 10000. Målet nås.",
    "",
    "Fokusera på: vikt.",
]

AFTER_18_DAYS = [
    "Vikten: minskar med 1.54 procent per vecka (cirka 1.5 kg), över säkerhetsgränsen "
    "1,0 procent (cirka 1.0 kg för dig). Risk för muskelförlust.",
    "Protein: snitt 215 g mot mål 206 g. Målet nås.",
    "Träning: 5 av 5 förväntade dagar under perioden. Målet nås.",
    "Steg: snitt 10270 mot mål 10000. Målet nås.",
    "",
    "Fokusera på: vikt.",
]

AFTER_20_DAYS = [
    "Vikten: minskar med 1.12 procent per vecka (cirka 1.1 kg), över säkerhetsgränsen "
    "1,0 procent (cirka 1.0 kg för dig). Risk för muskelförlust.",
    "Protein: snitt 213 g mot mål 206 g. Målet nås.",
    "Träning: 5 av 5 förväntade dagar under perioden. Målet nås.",
    "Steg: snitt 9953 mot mål 10000. Under målet.",
    "",
    "Fokusera på: vikt.",
]


def make_readme_profile(log_count, created_date="2026-09-17"):
    """Profilen Testperson från README, med de första log_count loggarna ur exempelfilen.
    Utan created_date skapas profilen samma dag som den första loggen."""
    profile = CutProfile("Testperson", 189, 39, "man", 1.55, 101.5, created_date,
                         goal_weight=98.0, target_rate_percent=0.6,
                         protein_goal_per_kg=2.1, step_goal=10000, training_goal_days=5)
    import_logs_csv(profile, str(EXAMPLE_CSV))
    profile.logs = profile.logs[:log_count]
    return profile


def check_goals_lines(profile, capsys, days=7):
    """Kör check_goals och returnerar det den skrev ut, rad för rad."""
    capsys.readouterr()  # släng det som skrevs ut innan, till exempel av inläsningen
    profile.check_goals(days)
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
    # README: veckosnittet för vikten är 99,03, 98,26 och 98,13 kg vid de tre tillfällena
    profile = make_readme_profile(log_count)
    assert profile.average_weight(7) == pytest.approx(average, abs=0.005)


# ---------------------------------------------------------------------------
# F24: takten räknas från snittet för två perioder
# ---------------------------------------------------------------------------

def daily_weights(first_weight, step, count):
    """count vikter, en per dag, där varje dag ligger step kg från dagen före."""
    weights = []
    for i in range(count):
        # round() städar bort decimaltalens avrundningsbrus
        weights.append(round(first_weight + step * i, 1))
    return weights


def make_daily_profile(weights, target_rate_percent=0.7):
    """Profil skapad 2026-09-01 med en logg per dag från och med samma dag, en vikt per
    logg. Protein, steg och träning ligger över målen, så bara vikten kan ge fokus."""
    profile = CutProfile("Testperson", 180, 30, "man", 1.5, 100.0, "2026-09-01",
                         goal_weight=80.0, target_rate_percent=target_rate_percent)
    first_day = date(2026, 9, 1)
    for i in range(len(weights)):
        date_text = (first_day + timedelta(days=i)).isoformat()
        profile.logs.append(DailyLog(date_text, weights[i], 2200, 200, 9000, True))
    return profile


@pytest.mark.parametrize("last_weight, rate", [(98.8, "1.63"), (98.4, "1.69")])
def test_f24_one_weighing_moves_the_rate_only_slightly(last_weight, rate, capsys):
    # Före F24 gav 200 gram mer eller mindre på sista vägningen 1,11 respektive 1,52 procent
    # per vecka i stället för 1,31, eftersom takten räknades från första och sista vägningen.
    # Nu ingår vägningen i ett snitt av sju, så 0,2 kg flyttar snittet 0,2 / 7 = 0,03 kg och
    # takten 0,03 procentenheter från 1,66. Sista vägningen var 98.6 kg. Summan för dag 8 till
    # 14 blir 693.2 + 0.2 = 693.4 respektive 693.2 - 0.2 = 693.0, och summan för dag 1 till 7
    # är 704.7:
    #   98.8: (704.7 - 693.4) / 693.4 = 11.3 / 693.4 = 1.63 procent
    #   98.4: (704.7 - 693.0) / 693.0 = 11.7 / 693.0 = 1.69 procent
    profile = make_readme_profile(14)
    profile.logs[-1].weight = last_weight
    first_line = check_goals_lines(profile, capsys)[0]
    assert first_line.startswith(f"Vikten: minskar med {rate} procent per vecka")


def test_f24_steady_loss_at_the_goal_pace_is_reported_as_on_target(capsys):
    # Vikten sjunker exakt 0,1 kg per dag, alltså 0,7 kg per vecka. De sju första dagarna
    # väger i snitt 89.7 kg (90.0 ned till 89.4) och de sju senaste 89.0 kg (89.3 ned till
    # 88.7). Skillnaden är 0.7 kg, och 0.7 / 89.0 = 0.79 procent av kroppsvikten. Det är över
    # målet på 0,7 procent, så raden ska säga "vid eller över ditt mål". Före F24 delade
    # koden 0,6 kg (första mot sista vägningen i fönstret, sex dagar isär) med sju dagar,
    # fick 0,67 procent och kallade det "långsammare än ditt mål".
    profile = make_daily_profile(daily_weights(90.0, -0.1, 14))

    first_line = check_goals_lines(profile, capsys)[0]

    assert first_line == (
        "Vikten: minskar med 0.79 procent per vecka (cirka 0.7 kg), vid eller över ditt mål "
        "på 0.7 procent och inom säkerhetsgränsen."
    )


@pytest.mark.parametrize("days, rate", [(7, "0.74"), (14, "0.74"), (30, "0.73")])
def test_f24_the_same_slope_gives_the_same_kilos_per_week_for_every_period(days, rate, capsys):
    # 60 dagar där vikten sjunker 0,1 kg per dag från 100.0 kg, alltså 0,7 kg per vecka. 60
    # dagar är precis nog för full analys med 30 dagars period (två perioder om 30 dagar).
    # Kilotalet ska bli 0.7 oavsett periodens längd. Procenttalet skiljer lite, eftersom det
    # räknas på snittet för den senaste perioden (dag n väger 100.0 - 0.1 * (n - 1)):
    #   7 dagar:  dag 54 till 60, snitt 94.40, 0.7 / 94.40 = 0.74 procent
    #   14 dagar: dag 47 till 60, snitt 94.75, 0.7 / 94.75 = 0.74 procent
    #   30 dagar: dag 31 till 60, snitt 95.55, 0.7 / 95.55 = 0.73 procent
    profile = make_daily_profile(daily_weights(100.0, -0.1, 60))

    first_line = check_goals_lines(profile, capsys, days)[0]

    assert first_line == (
        f"Vikten: minskar med {rate} procent per vecka (cirka 0.7 kg), vid eller över ditt mål "
        "på 0.7 procent och inom säkerhetsgränsen."
    )


def test_f24_rising_weight_reports_the_gain_per_week(capsys):
    # Vikten stiger 0,2 kg per dag. De sju första dagarna väger i snitt 90.6 kg (90.0 upp till
    # 91.2) och de sju senaste 92.0 kg (91.4 upp till 92.6): 1.4 kg mer än veckan före. Före
    # F24 blev det 1.2 kg, skillnaden mellan första och sista vägningen i fönstret.
    profile = make_daily_profile(daily_weights(90.0, 0.2, 14))

    lines = check_goals_lines(profile, capsys)

    assert lines[0] == "Vikten: ökar med 1.4 kg per vecka i snitt. Underskottet räcker inte."
    assert lines[-1] == "Fokusera på: vikt."


@pytest.mark.parametrize("latest_weight", [90.0, 89.99, 90.01],
                         ids=["exakt-lika", "0.01-ner", "0.01-upp"])
def test_f24_unchanged_weight_gets_its_own_text(latest_weight, capsys):
    # Perioden före väger 90.0 kg. Är den senaste perioden lika, eller skiljer den mindre än
    # 0,05 kg, avrundas kilotalet till 0.0 och vikten räknas som oförändrad. Före F24 skrev
    # koden "minskar med -0.0 procent per vecka" när skillnaden var exakt noll.
    weights = [90.0] * 7 + [latest_weight] * 7
    profile = make_daily_profile(weights)

    lines = check_goals_lines(profile, capsys)

    assert lines[0] == "Vikten: oförändrad jämfört med perioden före. Underskottet räcker inte."
    assert lines[-1] == "Fokusera på: vikt."


def test_f24_a_tenth_of_a_kilo_per_week_is_a_slow_loss_not_unchanged(capsys):
    # Perioden före väger 90.0 kg och den senaste 89.9 kg: 0.1 kg per vecka, 0.1 / 89.9 = 0.11
    # procent. Kilotalet avrundas till 0.1 och räknas därför som en nedgång, inte som
    # oförändrat. Målet på 0,6 procent av 89.9 kg är 0.54 kg, avrundat 0.5.
    weights = [90.0] * 7 + [89.9] * 7
    profile = make_daily_profile(weights, target_rate_percent=0.6)

    first_line = check_goals_lines(profile, capsys)[0]

    assert first_line == (
        "Vikten: minskar med 0.11 procent per vecka (cirka 0.1 kg), långsammare än ditt mål "
        "på 0.6 procent (cirka 0.5 kg för dig)."
    )


def test_f24_without_logs_in_the_previous_period_the_rate_is_not_assessed(capsys):
    # Profilen skapades 2026-09-01 och sista loggen är 2026-09-14, så 14 dagar har gått och
    # väntetiden är över. Men loggarna börjar först 2026-09-08. Perioden före (1 till 7
    # september) saknar vägningar, så det finns inget att jämföra den senaste perioden med.
    profile = make_daily_profile(daily_weights(90.0, -0.1, 14))
    profile.logs = profile.logs[7:]

    lines = check_goals_lines(profile, capsys)

    assert lines[0] == "Vikten: för lite data för att bedöma takten."
    assert lines[-1] == "Allt ligger inom mål just nu. Fortsätt som du gör."


# ---------------------------------------------------------------------------
# Exempelfilen i en ny profil (dagar sedan start)
# ---------------------------------------------------------------------------

def test_a_profile_created_after_the_example_logs_gets_the_same_analysis(capsys):
    # Så läser en ny användare in exempelfilen: menyn ger en ny profil dagens datum som
    # startdatum, och exempelloggarna är från 2026-09-17 till 2026-10-06. Före rättningen av
    # days_since_start räknades dagarna från startdatumet 2026-10-10 och blev -4 + 1 = -3, så
    # analysen ersattes av en väntetext. Nu räknas de från den tidigaste loggen, 20 dagar
    # (17 september till 6 oktober), och analysen är densamma som för profilen i README.
    profile = make_readme_profile(20, created_date="2026-10-10")
    assert profile.days_since_start() == 20
    assert check_goals_lines(profile, capsys) == AFTER_20_DAYS
