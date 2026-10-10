"""Tester för main.py: textmenyn (inmatning och utskrift) och programmets startpunkt.

Menyn frågar med input(), och input() läser från sys.stdin. I testerna byts sys.stdin mot
en textsträng med färdiga svar (se type_answers), så programmet tror att en användare
skriver och testet bestämmer exakt vad som skrivs.

Svaren syns inte i det som skrivs ut. En fråga och nästa utskrift hamnar därför på samma
rad, och testerna kontrollerar med "text in output", aldrig rad för rad.

Analysen (check_goals) och diagrammet (plot_weight) ersätts med stubbar där menyn anropar
dem. Menyn ska bara skicka vidare rätt period, och ett diagramfönster får inte öppnas
under en testkörning. Själva analysen testas i test_models.py och test_readme_example.py.

Filerna som menyn skriver (profil och CSV) hamnar i en tillfällig mapp, se
work_in_temp_folder. Alla namn och värden är påhittade.
"""
import io
import os
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

import pytest

import main
from analysis import export_logs_csv, load_profile, save_profile
from models import CutProfile, DailyLog

ROOT = Path(__file__).resolve().parent.parent
MAIN_PY = ROOT / "main.py"


@pytest.fixture(autouse=True)
def work_in_temp_folder(tmp_path, monkeypatch):
    """Kör varje test i en egen tom mapp.

    tmp_path är en ny tillfällig mapp för varje test, och monkeypatch.chdir byter
    arbetsmapp till den och ställer tillbaka den efteråt. autouse=True gör att fixturen
    gäller alla tester i filen, även ett test som glömmer be om den."""
    monkeypatch.chdir(tmp_path)


# Svaren på frågorna i create_profile, i den ordning de ställs. Aktivitetsnivå 3 är
# måttligt aktiv (faktor 1.55).
PROFILE_ANSWERS = {
    "height": "170",
    "age": "35",
    "sex": "kvinna",
    "activity": "3",
    "start_weight": "70",
    "goal_weight": "62",
    "rate": "0.8",
}

# Svaren på frågorna i log_today, i den ordning de ställs
LOG_ANSWERS = {
    "date": "2026-09-01",
    "weight": "69.6",
    "calories": "1900",
    "protein": "110",
    "steps": "9000",
    "trained": "j",
    "waist": "71.5",
}

# En ny användare: namnet, sedan profilfrågorna
NEW_USER = ["Anna Berg"] + list(PROFILE_ANSWERS.values())

# Menyval 1 (logga dagens data), sedan frågorna i log_today
LOG_ONE_DAY = ["1"] + list(LOG_ANSWERS.values())


def type_answers(monkeypatch, answers):
    """Låtsas att användaren skriver svaren i listan, ett per rad, i den ordningen.

    input() läser från sys.stdin. Byts den mot en StringIO får input() svaren därifrån
    i stället för från tangentbordet. När svaren är slut kastar input() EOFError, precis
    som när en användare trycker Ctrl+D. Ett test som frågar efter fler svar än det gett
    stoppas därför av EOFError i stället för att hänga."""
    text = ""
    for answer in answers:
        text = text + answer + "\n"
    monkeypatch.setattr(sys, "stdin", io.StringIO(text))


def answers_with(base, changes):
    """En kopia av svaren i base (en dictionary) där fälten i changes fått nya svar.

    Resultatet är en lista i samma ordning som frågorna ställs. Ett fält som inte finns i
    base ger KeyError, så att ett felstavat fältnamn i ett test inte passerar tyst."""
    result = dict(base)
    for field, answer in changes.items():
        if field not in result:
            raise KeyError(f"Okänt fält: {field}")
        result[field] = answer
    return list(result.values())


def make_profile(with_logs=False):
    """Samma profil som NEW_USER ger, men som objekt. Med with_logs finns två loggar."""
    profile = CutProfile("Anna Berg", 170, 35, "kvinna", 1.55, 70.0, "2026-09-01",
                         goal_weight=62.0, target_rate_percent=0.8)
    if with_logs:
        profile.logs.append(DailyLog("2026-09-01", 70.0, 2000, 120, 7000, True))
        profile.logs.append(DailyLog("2026-09-02", 69.6, 1900, 110, 9000, False, 71.5))
    return profile


# ---------------------------------------------------------------------------
# Frågor med talsvar (ask_number, ask_period)
# ---------------------------------------------------------------------------

def test_ask_number_returns_a_float_for_a_decimal_answer(monkeypatch):
    type_answers(monkeypatch, ["82.5"])
    assert main.ask_number("Vikt: ") == 82.5


def test_ask_number_returns_a_float_even_for_a_whole_number(monkeypatch):
    type_answers(monkeypatch, ["82"])
    result = main.ask_number("Vikt: ")
    assert result == 82.0
    assert isinstance(result, float)


def test_ask_number_returns_an_int_when_is_integer_is_true(monkeypatch):
    type_answers(monkeypatch, ["175"])
    result = main.ask_number("Längd: ", True)
    assert result == 175
    assert isinstance(result, int)


@pytest.mark.parametrize("bad_answer", ["abc", "", "8 2", "82kg"])
def test_ask_number_asks_again_after_an_answer_that_is_not_a_number(
        monkeypatch, capsys, bad_answer):
    type_answers(monkeypatch, [bad_answer, "82.5"])
    assert main.ask_number("Vikt: ") == 82.5
    assert capsys.readouterr().out.count("Skriv ett tal") == 1


def test_ask_number_with_is_integer_rejects_a_decimal_answer(monkeypatch, capsys):
    type_answers(monkeypatch, ["175.5", "175"])
    assert main.ask_number("Längd: ", True) == 175
    assert "Skriv ett tal" in capsys.readouterr().out


def test_ask_number_accepts_spaces_around_the_number(monkeypatch):
    # Ett mellanslag efter en inklistrad siffra är lätt att råka skriva
    type_answers(monkeypatch, [" 82.5 "])
    assert main.ask_number("Vikt: ") == 82.5


def test_ask_number_shows_the_question(monkeypatch, capsys):
    type_answers(monkeypatch, ["82.5"])
    main.ask_number("Vikt i kg: ")
    assert "Vikt i kg: " in capsys.readouterr().out


def test_ask_number_does_not_swallow_end_of_input(monkeypatch):
    # Ctrl+D eller stängd inmatning ska nå main(), inte fastna i en fråga som aldrig slutar
    type_answers(monkeypatch, [])
    with pytest.raises(EOFError):
        main.ask_number("Vikt: ")


@pytest.mark.parametrize("answer, expected", [("7", 7), ("14", 14), ("30", 30)])
def test_ask_period_returns_each_valid_period(monkeypatch, answer, expected):
    type_answers(monkeypatch, [answer])
    result = main.ask_period()
    assert result == expected
    assert isinstance(result, int)


@pytest.mark.parametrize("bad_answer", ["0", "1", "6", "8", "13", "15", "29", "31", "60", "-7"])
def test_ask_period_asks_again_after_a_number_that_is_not_a_valid_period(
        monkeypatch, capsys, bad_answer):
    type_answers(monkeypatch, [bad_answer, "14"])
    assert main.ask_period() == 14
    assert "Välj 7, 14 eller 30." in capsys.readouterr().out


def test_ask_period_asks_again_after_text(monkeypatch, capsys):
    type_answers(monkeypatch, ["vecka", "7"])
    assert main.ask_period() == 7
    assert "Skriv ett tal" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Starttexten (F22, H2)
# ---------------------------------------------------------------------------

def test_show_welcome_shows_the_disclaimer(capsys):
    main.show_welcome()
    assert "inte medicinsk rådgivning" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# create_profile (F1, F2)
# ---------------------------------------------------------------------------

def test_create_profile_builds_a_profile_from_the_answers(monkeypatch):
    type_answers(monkeypatch, list(PROFILE_ANSWERS.values()))

    profile = main.create_profile("Anna Berg")

    assert isinstance(profile, CutProfile)
    assert profile.name == "Anna Berg"
    assert profile.height_cm == 170
    assert profile.age == 35
    assert profile.sex == "kvinna"
    assert profile.activity_level == 1.55
    assert profile.start_weight == 70.0
    assert profile.goal_weight == 62.0
    assert profile.target_rate_percent == 0.8
    assert profile.logs == []


def test_create_profile_sets_the_created_date_to_today(monkeypatch):
    type_answers(monkeypatch, list(PROFILE_ANSWERS.values()))

    # Datumet jämförs med dagen före och dagen efter anropet, så testet klarar att
    # klockan passerar midnatt precis medan det körs
    before = date.today()
    profile = main.create_profile("Anna Berg")
    after = date.today()

    created = datetime.strptime(profile.created_date, "%Y-%m-%d").date()
    assert before <= created <= after


@pytest.mark.parametrize("choice, expected_factor", [
    ("1", 1.2),      # stillasittande
    ("2", 1.375),    # lätt aktiv
    ("3", 1.55),     # måttligt aktiv
    ("4", 1.725),    # mycket aktiv
    ("5", 1.9),      # extremt aktiv
])
def test_create_profile_translates_the_activity_choice_to_a_factor(
        monkeypatch, choice, expected_factor):
    type_answers(monkeypatch, answers_with(PROFILE_ANSWERS, {"activity": choice}))
    assert main.create_profile("Anna Berg").activity_level == expected_factor


def test_create_profile_asks_again_when_the_activity_choice_is_not_1_to_5(monkeypatch, capsys):
    # 6 är ett tal utanför listan. Text och 2.5 är inte heltal. 2 godtas.
    type_answers(monkeypatch,
                 ["170", "35", "kvinna", "6", "abc", "2.5", "2", "70", "62", "0.8"])

    profile = main.create_profile("Anna Berg")

    assert profile.activity_level == 1.375
    output = capsys.readouterr().out
    assert output.count("Välj ett tal mellan 1 och 5.") == 1
    assert output.count("Skriv ett tal") == 2


@pytest.mark.parametrize("typed, expected", [
    ("man", "man"),
    ("kvinna", "kvinna"),
    ("MAN", "man"),         # versaler blir gemener
    ("Kvinna", "kvinna"),
])
def test_create_profile_accepts_man_and_kvinna_in_any_case(monkeypatch, typed, expected):
    type_answers(monkeypatch, answers_with(PROFILE_ANSWERS, {"sex": typed}))
    assert main.create_profile("Anna Berg").sex == expected


def test_create_profile_asks_again_when_the_sex_is_not_man_or_kvinna(monkeypatch, capsys):
    type_answers(monkeypatch, ["170", "35", "hund", "man", "3", "70", "62", "0.8"])

    profile = main.create_profile("Bo Ek")

    assert profile.sex == "man"
    assert "Skriv man eller kvinna." in capsys.readouterr().out


def test_create_profile_needs_whole_numbers_for_height_and_age(monkeypatch, capsys):
    type_answers(monkeypatch, ["170.5", "170", "35.5", "35", "kvinna", "3", "70", "62", "0.8"])

    profile = main.create_profile("Anna Berg")

    assert profile.height_cm == 170
    assert isinstance(profile.height_cm, int)
    assert profile.age == 35
    assert isinstance(profile.age, int)
    assert capsys.readouterr().out.count("Skriv ett tal") == 2


def test_create_profile_explains_the_rate_in_kilos_per_week(monkeypatch, capsys):
    type_answers(monkeypatch, list(PROFILE_ANSWERS.values()))

    main.create_profile("Anna Berg")

    # Handräknat: 70 kg * 0.8 / 100 = 0.56, avrundat till en decimal 0.6 kg per vecka
    assert "Det motsvarar cirka 0.6 kg per vecka vid din nuvarande vikt." in \
        capsys.readouterr().out


def test_create_profile_asks_for_weights_and_rate_again_when_the_goal_is_not_lower(
        monkeypatch, capsys):
    # Första försöket: målvikten 75 är inte lägre än startvikten 70. Det andra försöket
    # (startvikt, målvikt, takt) gäller. Längd, ålder, kön och aktivitet frågas inte om.
    answers = answers_with(PROFILE_ANSWERS, {"goal_weight": "75"}) + ["80", "70", "0.5"]
    type_answers(monkeypatch, answers)

    profile = main.create_profile("Anna Berg")

    assert profile.height_cm == 170
    assert profile.start_weight == 80.0
    assert profile.goal_weight == 70.0
    assert profile.target_rate_percent == 0.5
    output = capsys.readouterr().out
    assert "Det gick inte: Målvikten måste vara lägre än startvikten." in output
    assert "Försök igen." in output


@pytest.mark.parametrize("bad_rate", ["0", "1.5", "-0.5"])
def test_create_profile_asks_again_when_the_rate_is_outside_0_to_1(
        monkeypatch, capsys, bad_rate):
    answers = answers_with(PROFILE_ANSWERS, {"rate": bad_rate}) + ["70", "62", "0.8"]
    type_answers(monkeypatch, answers)

    profile = main.create_profile("Anna Berg")

    assert profile.target_rate_percent == 0.8
    assert "Det gick inte: Takten måste ligga mellan 0 och 1,0 procent" in \
        capsys.readouterr().out


# ---------------------------------------------------------------------------
# log_today (F5, F6, F7, D2)
# ---------------------------------------------------------------------------

def test_log_today_adds_a_log_with_the_typed_values(monkeypatch, capsys):
    profile = make_profile()
    type_answers(monkeypatch, list(LOG_ANSWERS.values()))

    main.log_today(profile)

    assert len(profile.logs) == 1
    log = profile.logs[0]
    assert log.date == "2026-09-01"
    assert log.weight == 69.6
    assert log.calories == 1900
    assert log.protein == 110
    assert log.steps == 9000
    assert isinstance(log.steps, int)
    assert log.trained is True
    assert log.waist == 71.5
    assert "Loggen för 2026-09-01 lades till." in capsys.readouterr().out


def test_log_today_saves_a_missing_waist_as_none_not_zero(monkeypatch):
    profile = make_profile()
    type_answers(monkeypatch, answers_with(LOG_ANSWERS, {"waist": ""}))

    main.log_today(profile)

    assert profile.logs[0].waist is None


def test_log_today_accepts_decimals_for_weight_calories_and_protein(monkeypatch):
    profile = make_profile()
    answers = answers_with(LOG_ANSWERS,
                           {"weight": "69.5", "calories": "1900.5", "protein": "110.5"})
    type_answers(monkeypatch, answers)

    main.log_today(profile)

    log = profile.logs[0]
    assert log.weight == 69.5
    assert log.calories == 1900.5
    assert log.protein == 110.5


@pytest.mark.parametrize("typed, expected", [
    ("j", True),
    ("J", True),
    ("n", False),
    ("N", False),
])
def test_log_today_reads_j_and_n_for_training(monkeypatch, typed, expected):
    profile = make_profile()
    type_answers(monkeypatch, answers_with(LOG_ANSWERS, {"trained": typed}))

    main.log_today(profile)

    assert profile.logs[0].trained is expected


@pytest.mark.parametrize("field, bad_answer", [
    ("date", "inte ett datum"),
    ("date", "2026-13-45"),
    ("weight", "abc"),
    ("calories", "abc"),
    ("protein", "abc"),
    ("steps", "abc"),
    ("steps", "9000.5"),        # steg ska vara ett heltal
    ("waist", "abc"),
])
def test_log_today_saves_nothing_when_a_value_is_not_valid(
        monkeypatch, capsys, field, bad_answer):
    profile = make_profile()
    type_answers(monkeypatch, answers_with(LOG_ANSWERS, {field: bad_answer}))

    main.log_today(profile)

    assert profile.logs == []
    assert "Loggen sparades inte." in capsys.readouterr().out


@pytest.mark.parametrize("field, bad_answer, expected_message", [
    ("weight", "0", "Vikten måste vara ett rimligt tal"),
    ("weight", "301", "Vikten måste vara ett rimligt tal"),
    ("calories", "-1", "Kalorierna måste vara ett rimligt tal"),
    ("calories", "10001", "Kalorierna måste vara ett rimligt tal"),
])
def test_log_today_shows_why_a_value_out_of_range_was_rejected(
        monkeypatch, capsys, field, bad_answer, expected_message):
    profile = make_profile()
    type_answers(monkeypatch, answers_with(LOG_ANSWERS, {field: bad_answer}))

    main.log_today(profile)

    assert profile.logs == []
    output = capsys.readouterr().out
    assert "Loggen sparades inte." in output
    assert expected_message in output


def test_log_today_replaces_a_log_for_the_same_date(monkeypatch, capsys):
    profile = make_profile()
    type_answers(monkeypatch, list(LOG_ANSWERS.values()))
    main.log_today(profile)

    type_answers(monkeypatch, answers_with(LOG_ANSWERS, {"weight": "69.2"}))
    main.log_today(profile)

    assert len(profile.logs) == 1
    assert profile.logs[0].weight == 69.2
    output = capsys.readouterr().out
    assert "lades till" in output
    assert "uppdaterades" in output


@pytest.mark.parametrize("typed, expected", [
    ("2026-9-1", "2026-09-01"),
    ("2026-09-1", "2026-09-01"),
    ("2026-10-8", "2026-10-08"),
])
def test_log_today_saves_the_date_with_zeros(monkeypatch, capsys, typed, expected):
    # D1: programmet skriver om datumet och visar det omskrivna datumet i meddelandet
    profile = make_profile()
    type_answers(monkeypatch, answers_with(LOG_ANSWERS, {"date": typed}))

    main.log_today(profile)

    assert profile.logs[0].date == expected
    assert f"Loggen för {expected} lades till." in capsys.readouterr().out


def test_log_today_replaces_a_log_when_the_same_date_is_typed_without_a_zero(
        monkeypatch, capsys):
    profile = make_profile()
    type_answers(monkeypatch, answers_with(LOG_ANSWERS, {"date": "2026-09-01"}))
    main.log_today(profile)

    type_answers(monkeypatch, answers_with(LOG_ANSWERS, {"date": "2026-9-1", "weight": "69.2"}))
    main.log_today(profile)

    assert len(profile.logs) == 1
    assert profile.logs[0].weight == 69.2
    assert "Loggen för 2026-09-01 uppdaterades." in capsys.readouterr().out


@pytest.mark.parametrize("bad_date", ["inte ett datum", "2026-13-45", "2026-02-30", ""])
def test_log_today_explains_in_swedish_what_is_wrong_with_the_date(
        monkeypatch, capsys, bad_date):
    # N1: tidigare visades Pythons engelska text, till exempel
    # "time data 'abc' does not match format '%Y-%m-%d'"
    profile = make_profile()
    type_answers(monkeypatch, answers_with(LOG_ANSWERS, {"date": bad_date}))

    main.log_today(profile)

    output = capsys.readouterr().out
    assert "Datumet måste skrivas som ÅÅÅÅ-MM-DD, till exempel 2026-10-08." in output
    assert "does not match" not in output
    assert profile.logs == []


def test_log_today_checks_the_date_before_it_asks_for_anything_else(monkeypatch):
    # Ett fel datum ska stoppa direkt, inte först efter att användaren har skrivit in vikt,
    # kalorier och resten
    profile = make_profile()
    type_answers(monkeypatch, answers_with(LOG_ANSWERS, {"date": "abc"}))

    main.log_today(profile)

    assert sys.stdin.read() != ""  # svaren på de andra frågorna är inte lästa


# ---------------------------------------------------------------------------
# run_menu (F21)
# ---------------------------------------------------------------------------

def test_run_menu_shows_the_disclaimer_before_asking_for_the_name(monkeypatch, capsys):
    # Inga svar: inmatningen tar slut vid första frågan
    type_answers(monkeypatch, [])
    with pytest.raises(EOFError):
        main.run_menu()

    output = capsys.readouterr().out
    assert output.index("inte medicinsk rådgivning") < output.index("Vad heter du?")


def test_run_menu_shows_all_six_choices(monkeypatch, capsys):
    type_answers(monkeypatch, NEW_USER + ["6"])

    main.run_menu()

    output = capsys.readouterr().out
    for choice_text in ["1  Logga dagens data", "2  Visa analys", "3  Visa viktdiagram",
                        "4  Visa kaloriförslag", "5  Läs in loggar från CSV",
                        "6  Spara och avsluta"]:
        assert choice_text in output


def test_run_menu_creates_a_profile_for_a_new_user_and_saves_it_on_exit(
        monkeypatch, capsys, tmp_path):
    type_answers(monkeypatch, NEW_USER + LOG_ONE_DAY + ["6"])

    main.run_menu()

    # Handräknat för Anna (kvinna, 35 år, 170 cm, 70 kg, faktor 1.55, takt 0.8):
    #   basalomsättning  10 * 70 + 6.25 * 170 - 5 * 35 - 161 = 1426.5
    #   energibehov      1426.5 * 1.55 = 2211.075
    #   underskott       70 * 0.8 / 100 * 7700 / 7 = 616
    #   förslag          2211.075 - 616 = 1595.075, alltså 1595 (golvet 1426.5 slår inte i)
    #   proteinmål       62 * 1.9 = 117.8, alltså 118
    output = capsys.readouterr().out
    assert "Profil skapad för Anna Berg." in output
    assert "Ditt kaloriförslag: 1595 kcal per dag." in output
    assert "Ditt proteinmål: 118 gram per dag." in output
    assert "Hej då." in output

    # Menyval 6 sparar profilen (JSON) och loggarna (CSV) i den aktuella mappen
    assert (tmp_path / "annaberg.json").exists()
    assert (tmp_path / "annaberg_loggar.csv").exists()
    saved = load_profile("Anna Berg")
    assert saved.goal_weight == 62.0
    assert len(saved.logs) == 1
    assert saved.logs[0].date == "2026-09-01"
    assert saved.logs[0].weight == 69.6


def test_run_menu_loads_a_saved_profile_instead_of_asking_the_profile_questions(
        monkeypatch, capsys):
    save_profile(make_profile(with_logs=True))
    capsys.readouterr()                     # kastar bort utskriften från sparningen ovan
    type_answers(monkeypatch, ["Anna Berg", "6"])

    main.run_menu()

    output = capsys.readouterr().out
    assert "Profilen för Anna Berg laddades, 2 loggar." in output
    assert "Längd i cm" not in output
    assert "Profil skapad" not in output
    # Att spara igen vid avslut ska inte tappa de gamla loggarna
    assert len(load_profile("Anna Berg").logs) == 2


def test_run_menu_asks_again_after_a_menu_choice_that_does_not_exist(monkeypatch, capsys):
    type_answers(monkeypatch, NEW_USER + ["9", "abc", "", "6"])

    main.run_menu()

    output = capsys.readouterr().out
    assert output.count("Välj ett tal mellan 1 och 6.") == 3
    assert "Hej då." in output


def test_run_menu_choice_4_recalculates_the_suggestion_from_the_latest_weight(
        monkeypatch, capsys):
    # Profilen skapas på 70 kg (förslag 1595, se testet för en ny användare). Loggen sänker
    # vikten till 69.6 kg, så menyval 4 ska ge ett nytt förslag.
    # Handräknat för 69.6 kg:
    #   basalomsättning  10 * 69.6 + 6.25 * 170 - 5 * 35 - 161 = 1422.5
    #   energibehov      1422.5 * 1.55 = 2204.875
    #   underskott       69.6 * 0.8 / 100 * 7700 / 7 = 612.48
    #   förslag          2204.875 - 612.48 = 1592.395, alltså 1592
    # Proteinmålet räknas på målvikten och är oförändrat 118 gram.
    type_answers(monkeypatch, NEW_USER + LOG_ONE_DAY + ["4", "6"])

    main.run_menu()

    output = capsys.readouterr().out
    assert "Kaloriförslag: 1592 kcal per dag." in output
    assert "Proteinmål: 118 gram per dag." in output


def test_run_menu_choice_2_runs_the_analysis_for_the_chosen_period(monkeypatch):
    periods = []

    def fake_check_goals(self, days=7):
        periods.append(days)

    monkeypatch.setattr(CutProfile, "check_goals", fake_check_goals)
    type_answers(monkeypatch, NEW_USER + ["2", "14", "6"])

    main.run_menu()

    assert periods == [14]


def test_run_menu_choice_2_asks_again_until_the_period_is_valid(monkeypatch, capsys):
    periods = []

    def fake_check_goals(self, days=7):
        periods.append(days)

    monkeypatch.setattr(CutProfile, "check_goals", fake_check_goals)
    type_answers(monkeypatch, NEW_USER + ["2", "10", "30", "6"])

    main.run_menu()

    assert periods == [30]
    assert "Välj 7, 14 eller 30." in capsys.readouterr().out


def test_run_menu_choice_3_draws_the_weight_chart_for_the_chosen_period(monkeypatch):
    calls = []

    def fake_plot_weight(profile, days=30):
        calls.append((profile.name, days))

    monkeypatch.setattr(main, "plot_weight", fake_plot_weight)
    type_answers(monkeypatch, NEW_USER + ["3", "7", "6"])

    main.run_menu()

    assert calls == [("Anna Berg", 7)]


def test_run_menu_choice_5_reads_the_default_file_when_the_filename_is_left_empty(
        monkeypatch, capsys):
    export_logs_csv(make_profile(with_logs=True))     # skapar annaberg_loggar.csv
    capsys.readouterr()
    type_answers(monkeypatch, NEW_USER + ["5", "", "6"])

    main.run_menu()

    output = capsys.readouterr().out
    assert "Filnamn (tomt för annaberg_loggar.csv): " in output
    assert "2 loggar lästes in från annaberg_loggar.csv." in output
    assert len(load_profile("Anna Berg").logs) == 2


def test_run_menu_choice_5_reads_the_file_the_user_names(monkeypatch, capsys):
    export_logs_csv(make_profile(with_logs=True), "mina_data.csv")
    capsys.readouterr()
    type_answers(monkeypatch, NEW_USER + ["5", "mina_data.csv", "6"])

    main.run_menu()

    assert "2 loggar lästes in från mina_data.csv." in capsys.readouterr().out


def test_run_menu_choice_5_reports_a_missing_file_and_keeps_going(monkeypatch, capsys):
    type_answers(monkeypatch, NEW_USER + ["5", "saknas.csv", "6"])

    main.run_menu()

    output = capsys.readouterr().out
    assert "Filen saknas.csv hittades inte." in output
    assert "Hej då." in output


def test_run_menu_the_example_file_gives_a_new_user_an_analysis(monkeypatch, capsys):
    # Den här vägen kan en ny användare gå för att prova programmet utan egna loggar: val 5 med
    # exempelfilen, sedan val 2. Menyn ger en ny profil dagens datum som startdatum, och
    # exempelloggarna (2026-09-17 till 2026-10-06) är äldre än så. Före rättningen av
    # days_since_start blev dagarna negativa och analysen ersattes av en väntetext med
    # "-3 dagars data" (reproducerat 2026-10-10). Här körs den riktiga analysen, ingen stubb.
    example_file = str(ROOT / "data" / "exempel_loggar.csv")
    type_answers(monkeypatch, NEW_USER + ["5", example_file, "2", "7", "6"])

    main.run_menu()

    output = capsys.readouterr().out
    assert "20 loggar lästes in från" in output
    assert "Vikten: minskar med" in output
    assert "Fokusera på:" in output
    assert "vore bara brus" not in output


# ---------------------------------------------------------------------------
# main (startpunkten): Ctrl+C och Ctrl+D (N3, N5)
# ---------------------------------------------------------------------------

def test_main_function_runs_the_menu(monkeypatch, capsys):
    calls = []

    def fake_run_menu():
        calls.append("run_menu")

    monkeypatch.setattr(main, "run_menu", fake_run_menu)

    main.main()

    assert calls == ["run_menu"]
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("interruption", [KeyboardInterrupt, EOFError])
def test_main_function_ends_quietly_when_the_user_interrupts(
        monkeypatch, capsys, interruption):
    def interrupted_menu():
        raise interruption()

    monkeypatch.setattr(main, "run_menu", interrupted_menu)

    # KeyboardInterrupt som släpps ut ur ett test avbryter hela pytest-körningen. Därför
    # fångas det här och blir ett vanligt testfel med en förklaring.
    try:
        main.main()
    except interruption:
        pytest.fail(f"{interruption.__name__} ska fångas i main(), men kom ut ur funktionen")

    output = capsys.readouterr().out
    assert "Avbrutet." in output
    assert "inte sparat" in output


def test_main_function_does_not_hide_other_errors(monkeypatch):
    def broken_menu():
        raise RuntimeError("fel i menyn")

    monkeypatch.setattr(main, "run_menu", broken_menu)

    with pytest.raises(RuntimeError):
        main.main()


def test_main_function_handles_end_of_input_in_the_real_menu(monkeypatch, capsys):
    # Ingen stubb här: inmatningen tar slut mitt bland profilfrågorna, som vid Ctrl+D
    type_answers(monkeypatch, ["Anna Berg", "170"])

    main.main()

    assert "Avbrutet." in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Kontraktet mot notebooken (N7)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", [
    "show_welcome", "ask_number", "ask_period", "create_profile", "log_today", "run_menu",
])
def test_notebook_imports_exist_in_main(name):
    # cuttrack.ipynb gör: from main import (show_welcome, ask_number, ask_period,
    # create_profile, log_today, run_menu). Byter en funktion namn går notebooken sönder.
    assert callable(getattr(main, name))


# ---------------------------------------------------------------------------
# Startpunkten som eget program: python main.py (N5)
# ---------------------------------------------------------------------------

def run_python(arguments, stdin_text, cwd):
    """Kör Python som ett eget program, som från terminalen, och returnerar resultatet.

    Utf-8 anges för både in- och utdata, så att å, ä och ö tolkas lika på alla datorer.
    MPLBACKEND=Agg gör att matplotlib aldrig försöker öppna ett fönster. timeout stoppar
    ett program som skulle fastna och vänta på inmatning."""
    environment = dict(os.environ)
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["MPLBACKEND"] = "Agg"
    return subprocess.run(
        [sys.executable] + arguments,
        input=stdin_text, capture_output=True, text=True, encoding="utf-8",
        cwd=cwd, env=environment, timeout=60,
    )


def test_python_main_py_starts_the_program_and_exits_normally(tmp_path):
    typed = "\n".join(NEW_USER + ["6"]) + "\n"

    result = run_python([str(MAIN_PY)], typed, tmp_path)

    assert result.returncode == 0
    assert "Profil skapad för Anna Berg." in result.stdout
    assert "Hej då." in result.stdout
    assert "Traceback" not in result.stderr
    assert (tmp_path / "annaberg.json").exists()


def test_python_main_py_ends_without_a_traceback_when_the_input_is_closed(tmp_path):
    result = run_python([str(MAIN_PY)], "", tmp_path)

    assert result.returncode == 0
    assert "Avbrutet." in result.stdout
    assert "Traceback" not in result.stderr


def test_importing_main_does_not_start_the_menu():
    # Notebooken importerar main. Utan skyddet if __name__ == "__main__" hade menyn startat
    # redan vid importen. Här får importen tom inmatning: startar menyn skrivs något ut.
    result = run_python(["-c", "import main"], "", ROOT)

    assert result.returncode == 0
    assert result.stdout == ""
