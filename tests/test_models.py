"""Tester för models.py: validering, loggfönstret, snitt, kaloriförslag och golv,
väntetid och statusöversikten i check_goals.

Körs från repots rotmapp med: python -m pytest

Så läser du ett test:
- ett test är en funktion vars namn börjar med test_
- assert kontrollerar att ett villkor är sant, annars misslyckas testet
- pytest.raises(ValueError) kontrollerar att ett fel kastas
- pytest.approx jämför decimaltal, som inte alltid är exakta i en dator
  (0.1 + 0.2 blir 0.30000000000000004)
- capsys fångar det programmet skriver ut med print()
- @pytest.mark.parametrize kör samma test med flera uppsättningar värden

De förväntade siffrorna är uträknade för hand i kommentarerna, inte kopierade från
programmets utskrift. Då kontrollerar testet koden i stället för att upprepa den.

Testerna av check_goals kontrollerar vilken gren som väljs, med data som ligger långt från
gränserna. De exakta taktsiffrorna, och allt annat som beror på hur takten räknas (F24),
ligger i test_readme_example.py.
"""
from datetime import date, timedelta

import pytest

from models import DailyLog, User, CutProfile, normalize_date

# Dag 0 i testerna. Ett fast datum långt före idag, så att inget test av misstag
# beror på dagens datum.
BASE_DATE = date(2024, 1, 1)


def day_text(day):
    """Datumet för dag nummer day, som text (ÅÅÅÅ-MM-DD). Dag 0 är 2024-01-01."""
    return (BASE_DATE + timedelta(days=day)).isoformat()


def make_log(day, weight=90.0, calories=2200, protein=150, steps=8000, trained=True,
             waist=None):
    """En logg för dag nummer day. Allt utom dagen har ett rimligt standardvärde."""
    return DailyLog(day_text(day), weight, calories, protein, steps, trained, waist)


def make_logs(weights, protein=200, steps=9000, trained=True):
    """En logg per dag från dag 0, med en vikt per logg. Övriga värden är lika för alla."""
    logs = []
    for day in range(len(weights)):
        logs.append(make_log(day, weights[day], protein=protein, steps=steps,
                             trained=trained))
    return logs


def weights_changing_by(step, start=90.0, count=14):
    """count vikter där varje dag ligger step kg från dagen före."""
    weights = []
    for i in range(count):
        # round() städar bort decimaltalens avrundningsbrus
        weights.append(round(start + step * i, 1))
    return weights


def make_user():
    return User("Testperson", 180, 30, "man", 1.5, 90.0, day_text(0))


def make_profile(sex="man", height_cm=180, age=30, activity_level=1.5, start_weight=90.0,
                 goal_weight=80.0, target_rate_percent=0.6, created_date=None,
                 protein_goal_per_kg=1.9, step_goal=8000, training_goal_days=3):
    """En profil där alla värden har ett rimligt standardvärde. Skicka in bara det som
    testet handlar om. Utan created_date skapas profilen dag 0."""
    if created_date is None:
        created_date = day_text(0)
    return CutProfile("Testperson", height_cm, age, sex, activity_level, start_weight,
                      created_date, goal_weight, target_rate_percent,
                      protein_goal_per_kg, step_goal, training_goal_days)


def make_checked_profile(weights, protein=200, steps=9000, trained=True,
                         target_rate_percent=0.6):
    """Profil med en logg per dag, skapad dag 0. Med 14 loggar är väntetiden över för
    sjudagarsperioden, så check_goals gör en riktig analys."""
    profile = make_profile(target_rate_percent=target_rate_percent)
    profile.logs.extend(make_logs(weights, protein=protein, steps=steps, trained=trained))
    return profile


# ---------------------------------------------------------------------------
# DailyLog: validering (F5, F7)
# ---------------------------------------------------------------------------

def test_daily_log_stores_its_values():
    log = DailyLog("2026-09-01", 82.5, 2200, 160, 9000, True, 88.0)
    assert log.date == "2026-09-01"
    assert log.weight == 82.5
    assert log.calories == 2200
    assert log.protein == 160
    assert log.steps == 9000
    assert log.trained is True
    assert log.waist == 88.0


def test_waist_is_none_when_not_given():
    # D2: ett saknat värde är None, aldrig 0
    log = DailyLog("2026-09-01", 82.5, 2200, 160, 9000, True)
    assert log.waist is None


@pytest.mark.parametrize("weight", [0.1, 82.5, 300])
def test_weight_inside_limits_is_accepted(weight):
    # Gränserna är över 0 och högst 300 kg
    assert make_log(0, weight=weight).weight == weight


@pytest.mark.parametrize("weight", [0, -5, 300.1])
def test_weight_outside_limits_is_rejected(weight):
    with pytest.raises(ValueError, match="Vikten"):
        make_log(0, weight=weight)


@pytest.mark.parametrize("calories", [0, 2200, 10000])
def test_calories_inside_limits_are_accepted(calories):
    # Gränserna är 0 till 10 000, och 0 är giltigt
    assert make_log(0, calories=calories).calories == calories


@pytest.mark.parametrize("calories", [-1, 10001])
def test_calories_outside_limits_are_rejected(calories):
    with pytest.raises(ValueError, match="Kalorierna"):
        make_log(0, calories=calories)


# ---------------------------------------------------------------------------
# DailyLog: nan, inf, protein, steg, träning och midjemått (F2, F7, N1)
# ---------------------------------------------------------------------------

# nan ("inte ett tal") är ett decimaltal där varje jämförelse är falsk. Ett villkor som
# "weight <= 0 or weight > 300" släppte därför igenom nan: ingen av jämförelserna slår till.
# inf och -inf klarar inte någon övre gräns, men testas här tillsammans med nan.
NOT_FINITE = [float("nan"), float("inf"), float("-inf")]

# Värden som aldrig är ett tal i ett fält som ska innehålla ett tal. De kan komma från en
# profilfil som redigerats för hand, där text och true/false kan stå var som helst. True och
# False är int i Python, så True skulle annars räknas som talet 1.
NOT_A_NUMBER = ["82.5", [82.5], True, False]


@pytest.mark.parametrize("weight", NOT_FINITE + NOT_A_NUMBER + [None])
def test_weight_that_is_not_a_usable_number_is_rejected(weight):
    with pytest.raises(ValueError, match="Vikten"):
        make_log(0, weight=weight)


@pytest.mark.parametrize("calories", NOT_FINITE + NOT_A_NUMBER + [None])
def test_calories_that_are_not_a_usable_number_are_rejected(calories):
    with pytest.raises(ValueError, match="Kalorierna"):
        make_log(0, calories=calories)


@pytest.mark.parametrize("protein", [0, 150, 150.5, 1000])
def test_protein_inside_limits_is_accepted(protein):
    # Gränserna är 0 till 1 000 gram, och 0 är giltigt
    assert make_log(0, protein=protein).protein == protein


@pytest.mark.parametrize("protein", [-1, -0.1, 1000.1] + NOT_FINITE + NOT_A_NUMBER + [None])
def test_protein_outside_limits_or_not_a_number_is_rejected(protein):
    with pytest.raises(ValueError, match="Proteinet"):
        make_log(0, protein=protein)


@pytest.mark.parametrize("steps", [0, 8000, 100000])
def test_steps_inside_limits_are_accepted(steps):
    # Gränserna är 0 till 100 000 steg
    assert make_log(0, steps=steps).steps == steps


@pytest.mark.parametrize("steps", [
    -1, 100001,
    8000.5,                   # steg är hela steg
    8000.0,                   # ett decimaltal är inte ett heltal, även om det är jämnt
    "8000", None, [8000], True, False,
] + NOT_FINITE)
def test_steps_outside_limits_or_not_a_whole_number_are_rejected(steps):
    with pytest.raises(ValueError, match="Stegen"):
        make_log(0, steps=steps)


@pytest.mark.parametrize("trained", [True, False])
def test_trained_accepts_true_and_false(trained):
    assert make_log(0, trained=trained).trained is trained


@pytest.mark.parametrize("trained", ["j", "ja", "nej", "True", "false", 1, 0, None])
def test_trained_must_be_true_or_false(trained):
    # Förut räknades "nej" i en profilfil som ja, eftersom en text som inte är tom är sann
    with pytest.raises(ValueError, match="Träning måste vara True eller False"):
        make_log(0, trained=trained)


@pytest.mark.parametrize("waist", [30, 88.5, 250])
def test_waist_inside_limits_is_accepted(waist):
    # Gränserna är 30 till 250 cm. Utan midjemått är värdet None, inte 0 (D2)
    assert make_log(0, waist=waist).waist == waist


@pytest.mark.parametrize("waist", [0, -5, 29.9, 250.1] + NOT_FINITE + NOT_A_NUMBER)
def test_waist_outside_limits_or_not_a_number_is_rejected(waist):
    with pytest.raises(ValueError, match="Midjemåttet"):
        make_log(0, waist=waist)


# ---------------------------------------------------------------------------
# Datum: normalize_date, DailyLog och startdatumet (D1)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("typed, expected", [
    ("2026-10-08", "2026-10-08"),   # redan rätt, ändras inte
    ("2026-10-8", "2026-10-08"),    # dagen utan nolla
    ("2026-9-1", "2026-09-01"),     # månad och dag utan nolla
    ("2026-1-10", "2026-01-10"),    # månaden utan nolla
    ("2024-02-29", "2024-02-29"),   # skottdag i ett skottår
])
def test_normalize_date_writes_the_date_as_year_month_day_with_zeros(typed, expected):
    assert normalize_date(typed) == expected


@pytest.mark.parametrize("typed", [
    "2026-02-30",   # februari har inte 30 dagar
    "2025-02-29",   # 2025 är inte ett skottår
    "2026-04-31",   # april har 30 dagar
    "2026-13-01",   # det finns ingen trettonde månad
    "2026-00-10",   # månad noll finns inte
    "2026-10-00",   # dag noll finns inte
    "2026-10-32",   # ingen månad har 32 dagar
])
def test_normalize_date_rejects_a_date_that_does_not_exist(typed):
    with pytest.raises(ValueError, match="ÅÅÅÅ-MM-DD"):
        normalize_date(typed)


@pytest.mark.parametrize("typed", [
    "",
    "abc",
    "inte ett datum",
    "08/10/2026",             # fel ordning och fel skiljetecken
    "2026/10/08",             # snedstreck i stället för streck
    "8 oktober 2026",
    "20261008",               # inga skiljetecken
    "26-10-08",               # tvåsiffrigt år
    "2026-10",                # dagen saknas
    "2026-10-08T12:30:00",    # klockslag efter datumet
])
def test_normalize_date_rejects_text_that_is_not_a_date_in_this_format(typed):
    with pytest.raises(ValueError, match="ÅÅÅÅ-MM-DD"):
        normalize_date(typed)


@pytest.mark.parametrize("not_text", [None, 20261008, 2026.10, ["2026-10-08"]])
def test_normalize_date_rejects_a_value_that_is_not_text(not_text):
    # En JSON-fil kan ha null eller ett tal där datumet ska stå. Det ska ge samma
    # ValueError med samma meddelande, inte ett TypeError som ingen fångar.
    with pytest.raises(ValueError, match="ÅÅÅÅ-MM-DD"):
        normalize_date(not_text)


@pytest.mark.parametrize("typed, expected", [
    (" 2026-10-08", "2026-10-08"),
    ("2026-10-08 ", "2026-10-08"),
    ("  2026-10-8  ", "2026-10-08"),    # mellanslag runt datumet och dagen utan nolla
    ("\t2026-10-08\n", "2026-10-08"),   # tabb och radslut räknas också som mellanslag
])
def test_normalize_date_ignores_spaces_around_the_date(typed, expected):
    # N1: ett mellanslag efter ett inklistrat datum är lätt att råka skriva. Förut avvisades
    # det i menyn, och CSV-inläsningen fick ta bort det själv.
    assert normalize_date(typed) == expected


@pytest.mark.parametrize("typed", ["   ", "\t", "2026- 10-08", "2026-10 -08", "2026 -10-08"])
def test_normalize_date_does_not_ignore_spaces_inside_the_date(typed):
    # Bara mellanslag runt datumet tas bort. Inuti datumet, eller när texten inte består av
    # något annat än mellanslag, är det fortfarande inget datum.
    with pytest.raises(ValueError, match="ÅÅÅÅ-MM-DD"):
        normalize_date(typed)


def test_daily_log_and_start_date_ignore_spaces_around_the_date():
    assert DailyLog(" 2026-09-01 ", 82.5, 2200, 160, 9000, True).date == "2026-09-01"
    user = User("Testperson", 180, 30, "man", 1.5, 90.0, " 2026-9-1 ")
    assert user.created_date == "2026-09-01"


@pytest.mark.parametrize("typed, expected", [
    ("2026-09-01", "2026-09-01"),
    ("2026-9-1", "2026-09-01"),
    ("2026-10-8", "2026-10-08"),
])
def test_daily_log_stores_the_date_with_zeros(typed, expected):
    # Datumet sparas alltid som ÅÅÅÅ-MM-DD med nollor, så att texten sorteras rätt
    assert DailyLog(typed, 82.5, 2200, 160, 9000, True).date == expected


@pytest.mark.parametrize("typed", ["2026-13-45", "abc", "", None, 20261008])
def test_daily_log_rejects_a_date_that_is_not_a_real_date(typed):
    with pytest.raises(ValueError, match="ÅÅÅÅ-MM-DD"):
        DailyLog(typed, 82.5, 2200, 160, 9000, True)


@pytest.mark.parametrize("typed, expected", [
    ("2026-10-01", "2026-10-01"),
    ("2026-10-1", "2026-10-01"),
])
def test_a_start_date_is_stored_with_zeros(typed, expected):
    user = User("Testperson", 180, 30, "man", 1.5, 90.0, typed)
    assert user.created_date == expected


@pytest.mark.parametrize("typed", ["2026-13-01", "abc", "", None])
def test_a_start_date_that_is_not_a_real_date_is_rejected(typed):
    with pytest.raises(ValueError, match="ÅÅÅÅ-MM-DD"):
        User("Testperson", 180, 30, "man", 1.5, 90.0, typed)


def test_a_profile_follows_the_same_rule_for_the_start_date():
    assert make_profile(created_date="2026-9-1").created_date == "2026-09-01"
    with pytest.raises(ValueError, match="ÅÅÅÅ-MM-DD"):
        make_profile(created_date="2026-13-01")


# ---------------------------------------------------------------------------
# CutProfile: validering och standardvärden (F2, F11, F23)
# ---------------------------------------------------------------------------

def test_cut_profile_is_a_user_with_empty_logs():
    profile = make_profile()
    assert isinstance(profile, User)
    assert profile.logs == []
    assert profile.calorie_goal is None


def test_optional_goals_have_default_values():
    profile = CutProfile("Testperson", 180, 30, "man", 1.5, 90.0, "2026-09-01", 80.0, 0.6)
    assert profile.protein_goal_per_kg == 1.9
    assert profile.step_goal == 8000
    assert profile.training_goal_days == 3


@pytest.mark.parametrize("goal_weight", [90.0, 95.0, 0, -1])
def test_goal_weight_must_be_positive_and_below_start_weight(goal_weight):
    # Startvikten är 90.0, så målvikten 90.0 (lika med) avvisas också
    with pytest.raises(ValueError, match="Målvikten"):
        make_profile(start_weight=90.0, goal_weight=goal_weight)


def test_goal_weight_just_below_start_weight_is_accepted():
    assert make_profile(start_weight=90.0, goal_weight=89.9).goal_weight == 89.9


@pytest.mark.parametrize("rate", [0, -0.5, 1.01])
def test_rate_must_be_above_zero_and_at_most_one_percent(rate):
    with pytest.raises(ValueError, match="Takten"):
        make_profile(target_rate_percent=rate)


@pytest.mark.parametrize("rate", [0.1, 1.0])
def test_rate_at_the_limits_is_accepted(rate):
    assert make_profile(target_rate_percent=rate).target_rate_percent == rate


# ---------------------------------------------------------------------------
# User och CutProfile: kontroll av uppgifterna i profilen (F2, N1)
# ---------------------------------------------------------------------------
# Förut kontrollerades bara målvikten och takten. Längd 0, ålder -5 och ett namn som inte var
# text gav en profil, och nan släpptes igenom (se NOT_FINITE ovan). Kontrollen ligger i
# klasserna, så den gäller för menyn, för CSV-inläsningen och för profilfilerna.

def make_user_with(**changes):
    """En User där fälten i changes fått andra värden än standardvärdena. Ett fält som inte
    finns ger KeyError, så att ett felstavat fältnamn i ett test inte passerar tyst."""
    values = {"name": "Testperson", "height_cm": 180, "age": 30, "sex": "man",
              "activity_level": 1.5, "start_weight": 90.0, "created_date": day_text(0)}
    for field, value in changes.items():
        if field not in values:
            raise KeyError(f"Okänt fält: {field}")
        values[field] = value
    return User(**values)


@pytest.mark.parametrize("name", ["Anna Berg", "A", "x" * 50, "Åsa Öberg", "123"])
def test_a_name_that_is_text_with_content_is_accepted(name):
    # Gränsen är 1 till 50 tecken
    assert make_user_with(name=name).name == name


def test_a_name_is_stored_without_spaces_around_it():
    assert make_user_with(name="  Anna Berg  ").name == "Anna Berg"
    # Mellanslagen räknas inte mot längdgränsen
    assert make_user_with(name="  " + "x" * 50 + "  ").name == "x" * 50


@pytest.mark.parametrize("name", ["", "   ", "\t", "x" * 51, None, 5, ["Anna"], True])
def test_a_name_that_is_not_text_with_content_is_rejected(name):
    # En profilfil med "name": 5 lästes förut in utan fel och kraschade först vid sparningen
    with pytest.raises(ValueError, match="Namnet"):
        make_user_with(name=name)


def test_a_cut_profile_follows_the_same_rule_for_the_name():
    with pytest.raises(ValueError, match="Namnet"):
        CutProfile("", 180, 30, "man", 1.5, 90.0, day_text(0), 80.0, 0.6)


@pytest.mark.parametrize("height_cm", [100, 175.5, 180, 250])
def test_height_inside_limits_is_accepted(height_cm):
    # Gränserna är 100 till 250 cm
    assert make_user_with(height_cm=height_cm).height_cm == height_cm


@pytest.mark.parametrize("height_cm", [0, -180, 99.9, 250.1] + NOT_FINITE + NOT_A_NUMBER + [None])
def test_height_outside_limits_or_not_a_number_is_rejected(height_cm):
    with pytest.raises(ValueError, match="Längden"):
        make_user_with(height_cm=height_cm)


def test_the_height_message_tells_the_limits():
    # Menyn visar de här gränserna när den frågar om längden igen
    with pytest.raises(ValueError, match="mellan 100 och 250 cm"):
        make_user_with(height_cm=99)


@pytest.mark.parametrize("age", [18, 30, 100])
def test_age_inside_limits_is_accepted(age):
    # Gränserna är 18 till 100 år. Riktlinjerna som kaloriförslaget bygger på gäller vuxna
    # (se README), därför är 18 den undre gränsen.
    assert make_user_with(age=age).age == age


@pytest.mark.parametrize("age", [17, 101, 0, -5, 30.5, 30.0, "30", None, [30], True, False]
                         + NOT_FINITE)
def test_age_outside_limits_or_not_a_whole_number_is_rejected(age):
    with pytest.raises(ValueError, match="Åldern"):
        make_user_with(age=age)


def test_the_age_message_tells_the_limits_and_why():
    with pytest.raises(ValueError, match="mellan 18 och 100 år") as caught:
        make_user_with(age=17)
    assert "vuxna" in str(caught.value)


@pytest.mark.parametrize("sex", ["man", "kvinna"])
def test_man_and_kvinna_are_accepted_as_sex(sex):
    assert make_user_with(sex=sex).sex == sex


@pytest.mark.parametrize("sex", ["", "Man", "MAN", "male", "annat", " man", 3, None, True])
def test_a_sex_that_is_not_exactly_man_or_kvinna_is_rejected(sex):
    # Förut räknades allt utom "man" som kvinna, så "sex": 3 i en profilfil gav kvinnans formel
    # utan något meddelande. Menyn gör svaret till gemener innan det kommer hit.
    with pytest.raises(ValueError, match="Kön måste vara man eller kvinna"):
        make_user_with(sex=sex)


@pytest.mark.parametrize("activity_level", [1.0, 1.2, 1.55, 1.9, 2.5, 2])
def test_activity_level_inside_limits_is_accepted(activity_level):
    # Menyn ger faktorerna 1.2 till 1.9. Klassen godtar 1.0 till 2.5, för en profilfil där
    # någon har ändrat faktorn för hand.
    assert make_user_with(activity_level=activity_level).activity_level == activity_level


@pytest.mark.parametrize("activity_level",
                         [0, 0.99, 2.51, -1.5] + NOT_FINITE + NOT_A_NUMBER + [None])
def test_activity_level_outside_limits_or_not_a_number_is_rejected(activity_level):
    with pytest.raises(ValueError, match="Aktivitetsnivån"):
        make_user_with(activity_level=activity_level)


@pytest.mark.parametrize("start_weight", [0.1, 90.0, 300])
def test_start_weight_inside_limits_is_accepted(start_weight):
    # Samma gränser som för vikten i en logg: över 0 och högst 300 kg
    assert make_user_with(start_weight=start_weight).start_weight == start_weight


@pytest.mark.parametrize("start_weight", [0, -1, 300.1] + NOT_FINITE + NOT_A_NUMBER + [None])
def test_start_weight_outside_limits_or_not_a_number_is_rejected(start_weight):
    with pytest.raises(ValueError, match="Startvikten"):
        make_user_with(start_weight=start_weight)


def test_an_invalid_start_weight_is_reported_before_the_goal_weight_is_compared():
    # Med startvikten nan är varje jämförelse med målvikten falsk. Startvikten ska stoppas
    # först, annars skulle profilen godtas med en målvikt som inte går att jämföra.
    with pytest.raises(ValueError, match="Startvikten"):
        make_profile(start_weight=float("nan"), goal_weight=80.0)


@pytest.mark.parametrize("goal_weight", NOT_FINITE + NOT_A_NUMBER + [None])
def test_goal_weight_that_is_not_a_usable_number_is_rejected(goal_weight):
    with pytest.raises(ValueError, match="Målvikten"):
        make_profile(goal_weight=goal_weight)


@pytest.mark.parametrize("rate", NOT_FINITE + NOT_A_NUMBER + [None])
def test_rate_that_is_not_a_usable_number_is_rejected(rate):
    with pytest.raises(ValueError, match="Takten"):
        make_profile(target_rate_percent=rate)


@pytest.mark.parametrize("grams_per_kg", [0.5, 1.9, 2.2, 5])
def test_protein_goal_per_kg_inside_limits_is_accepted(grams_per_kg):
    # Över 0 och högst 5 gram per kilo. Gränsen fångar ett tangentfel som 19 i stället för 1.9
    # och är inget råd om hur mycket protein som är lagom.
    assert make_profile(protein_goal_per_kg=grams_per_kg).protein_goal_per_kg == grams_per_kg


@pytest.mark.parametrize("grams_per_kg", [0, -1.9, 5.1, 19] + NOT_FINITE + NOT_A_NUMBER + [None])
def test_protein_goal_per_kg_outside_limits_or_not_a_number_is_rejected(grams_per_kg):
    with pytest.raises(ValueError, match="Proteinmålet"):
        make_profile(protein_goal_per_kg=grams_per_kg)


@pytest.mark.parametrize("step_goal", [1, 8000, 100000])
def test_step_goal_inside_limits_is_accepted(step_goal):
    assert make_profile(step_goal=step_goal).step_goal == step_goal


@pytest.mark.parametrize("step_goal", [0, -8000, 100001, 8000.5, 8000.0, "8000", None, True, False]
                         + NOT_FINITE)
def test_step_goal_outside_limits_or_not_a_whole_number_is_rejected(step_goal):
    with pytest.raises(ValueError, match="Stegmålet"):
        make_profile(step_goal=step_goal)


@pytest.mark.parametrize("training_goal_days", [0, 3, 7])
def test_training_goal_days_inside_limits_are_accepted(training_goal_days):
    # Dagar per vecka, så 0 till 7
    assert make_profile(training_goal_days=training_goal_days).training_goal_days \
        == training_goal_days


@pytest.mark.parametrize("training_goal_days", [-1, 8, 3.5, 3.0, "3", None, True, False]
                         + NOT_FINITE)
def test_training_goal_days_outside_limits_or_not_a_whole_number_are_rejected(
        training_goal_days):
    with pytest.raises(ValueError, match="Träningsmålet"):
        make_profile(training_goal_days=training_goal_days)


def test_a_profile_with_every_value_at_its_lower_limit_is_accepted():
    profile = CutProfile("A", 100, 18, "kvinna", 1.0, 0.2, day_text(0), 0.1, 0.1,
                         protein_goal_per_kg=0.1, step_goal=1, training_goal_days=0)
    assert profile.name == "A"


def test_a_profile_with_every_value_at_its_upper_limit_is_accepted():
    profile = CutProfile("x" * 50, 250, 100, "man", 2.5, 300, day_text(0), 299.9, 1.0,
                         protein_goal_per_kg=5, step_goal=100000, training_goal_days=7)
    assert profile.age == 100


# ---------------------------------------------------------------------------
# User.add_log (F6)
# ---------------------------------------------------------------------------

def test_add_log_appends_a_new_date_and_says_so(capsys):
    user = make_user()
    user.add_log(make_log(0))
    assert len(user.logs) == 1
    assert "Loggen för 2024-01-01 lades till." in capsys.readouterr().out


def test_add_log_replaces_a_log_with_the_same_date_and_says_so(capsys):
    user = make_user()
    user.add_log(make_log(0, weight=90.0))
    capsys.readouterr()  # släng meddelandet från första loggen
    user.add_log(make_log(0, weight=89.0))
    assert len(user.logs) == 1
    assert user.logs[0].weight == 89.0
    assert "Loggen för 2024-01-01 uppdaterades." in capsys.readouterr().out


def test_add_log_treats_the_same_day_written_with_and_without_a_zero_as_one_log(capsys):
    # D1: 2026-10-8 och 2026-10-08 är samma dag. Utan omskrivningen hade det blivit två loggar.
    user = make_user()
    user.add_log(DailyLog("2026-10-8", 90.0, 2200, 150, 8000, True))
    capsys.readouterr()
    user.add_log(DailyLog("2026-10-08", 89.0, 2200, 150, 8000, True))
    assert len(user.logs) == 1
    assert user.logs[0].weight == 89.0
    assert "Loggen för 2026-10-08 uppdaterades." in capsys.readouterr().out


# ---------------------------------------------------------------------------
# User.get_logs: fönstret i kalenderdagar (D3)
# ---------------------------------------------------------------------------

def test_get_logs_is_empty_without_logs():
    assert make_user().get_logs(7) == []


def test_window_is_counted_in_calendar_days_back_from_the_latest_log():
    # Senaste loggen är dag 10. Sju dagar bakåt är dag 4 till 10: dag 4 är sex dagar
    # före och är med, dag 3 är sju dagar före och är inte med.
    user = make_user()
    user.logs.extend([make_log(3), make_log(4), make_log(10)])
    assert [log.date for log in user.get_logs(7)] == [day_text(4), day_text(10)]


def test_window_counts_days_not_number_of_logs():
    # Sex loggar med fem dagars mellanrum. De sju senaste dagarna innehåller bara två.
    user = make_user()
    user.logs.extend([make_log(0), make_log(5), make_log(10),
                      make_log(15), make_log(20), make_log(25)])
    assert len(user.get_logs(7)) == 2


def test_window_does_not_depend_on_the_order_of_the_logs():
    user = make_user()
    user.logs.extend([make_log(10), make_log(3), make_log(4)])  # senaste först
    assert len(user.get_logs(7)) == 2


def test_window_is_counted_from_the_latest_log_not_from_today():
    # Loggarna ligger år 2024, långt före idag, och fönstret räknas ändå från dem
    user = make_user()
    user.logs.extend([make_log(0), make_log(1)])
    assert len(user.get_logs(7)) == 2


def test_window_works_across_month_and_year_boundaries():
    # 3 januari minus 28 december är sex dagar, minus 27 december är sju dagar
    user = make_user()
    for date_text in ("2025-12-27", "2025-12-28", "2026-01-03"):
        user.logs.append(DailyLog(date_text, 90.0, 2200, 150, 8000, True))
    assert [log.date for log in user.get_logs(7)] == ["2025-12-28", "2026-01-03"]


def test_window_longer_than_the_data_returns_all_logs():
    user = make_user()
    user.logs.extend([make_log(0), make_log(1)])
    assert len(user.get_logs(30)) == 2


def test_window_can_be_moved_back_with_an_offset():
    # 14 loggar, dag 0 till 13. De sju senaste är dag 7 till 13, de sju före är dag 0 till 6.
    user = make_user()
    user.logs.extend(make_logs([90.0] * 14))
    assert [log.date for log in user.get_logs(7)] == [day_text(day) for day in range(7, 14)]
    assert [log.date for log in user.get_logs(7, 7)] == [day_text(day) for day in range(0, 7)]


def test_moved_window_is_counted_in_calendar_days_back_from_the_latest_log():
    # Senaste loggen är dag 17. Med sju dagar och förskjutning sju är fönstret dag 4 till 10.
    # Dag 10 är sju dagar före och är med, dag 11 är sex dagar före och är inte med. Dag 4 är
    # 13 dagar före och är med, dag 3 är 14 dagar före och är inte med.
    user = make_user()
    user.logs.extend([make_log(3), make_log(4), make_log(10), make_log(11), make_log(17)])
    assert [log.date for log in user.get_logs(7, 7)] == [day_text(4), day_text(10)]


def test_offset_zero_is_the_same_as_no_offset():
    user = make_user()
    user.logs.extend(make_logs([90.0] * 14))
    assert user.get_logs(7, 0) == user.get_logs(7)


def test_moved_window_is_empty_when_the_offset_is_beyond_the_data():
    user = make_user()
    user.logs.extend(make_logs([90.0] * 14))
    assert user.get_logs(7, 30) == []


def test_get_logs_with_an_offset_is_empty_without_logs():
    assert make_user().get_logs(7, 7) == []


def test_a_negative_offset_is_rejected():
    user = make_user()
    user.logs.append(make_log(0))
    with pytest.raises(ValueError):
        user.get_logs(7, -1)


# ---------------------------------------------------------------------------
# User: snitt, viktförändring och träningsdagar
# ---------------------------------------------------------------------------

def test_averages_over_the_window():
    user = make_user()
    user.logs.extend([make_log(0, weight=90.0, protein=100, steps=6000),
                      make_log(1, weight=89.0, protein=200, steps=10000)])
    assert user.average_weight(7) == pytest.approx(89.5)
    assert user.average_protein(7) == pytest.approx(150)
    assert user.average_steps(7) == pytest.approx(8000)


def test_averages_ignore_logs_outside_the_window():
    user = make_user()
    user.logs.extend([make_log(0, weight=100.0, protein=0, steps=0),  # utanför fönstret
                      make_log(20, weight=90.0, protein=100, steps=6000),
                      make_log(21, weight=88.0, protein=200, steps=10000)])
    assert user.average_weight(7) == pytest.approx(89.0)
    assert user.average_protein(7) == pytest.approx(150)
    assert user.average_steps(7) == pytest.approx(8000)


def test_averages_are_none_without_logs():
    user = make_user()
    assert user.average_weight(7) is None
    assert user.average_protein(7) is None
    assert user.average_steps(7) is None


def test_average_weight_can_be_taken_over_the_period_before():
    # Dag 7 och 8 ligger i den senaste perioden (dag 2 till 8), dag 0 och 1 i perioden före
    user = make_user()
    user.logs.extend([make_log(0, weight=90.0), make_log(1, weight=88.0),
                      make_log(7, weight=86.0), make_log(8, weight=84.0)])
    assert user.average_weight(7) == pytest.approx(85.0)  # (86 + 84) / 2
    assert user.average_weight(7, 7) == pytest.approx(89.0)  # (90 + 88) / 2
    assert user.average_weight(7, 30) is None  # inga loggar så långt bak


def test_weight_change_is_last_minus_first_so_loss_is_negative():
    user = make_user()
    user.logs.extend([make_log(0, weight=90.0), make_log(3, weight=88.5)])
    assert user.weight_change(7) == pytest.approx(-1.5)


def test_weight_change_is_positive_when_weight_goes_up():
    user = make_user()
    user.logs.extend([make_log(0, weight=90.0), make_log(3, weight=91.0)])
    assert user.weight_change(7) == pytest.approx(1.0)


def test_weight_change_picks_first_and_last_by_date_not_by_position():
    user = make_user()
    user.logs.extend([make_log(3, weight=88.5), make_log(0, weight=90.0)])
    assert user.weight_change(7) == pytest.approx(-1.5)


def test_weight_change_is_right_when_a_date_was_typed_without_a_zero():
    # D1: 2026-10-8 är före 2026-10-10, men som text kommer den efter. Vikten gick upp 5 kg
    # från den 8:e till den 10:e. Jämförd som text hade förändringen blivit -5.0.
    user = make_user()
    user.logs.extend([DailyLog("2026-10-10", 90.0, 2200, 150, 8000, True),
                      DailyLog("2026-10-8", 85.0, 2200, 150, 8000, True)])
    assert user.weight_change(7) == pytest.approx(5.0)


def test_weight_change_needs_two_logs():
    user = make_user()
    assert user.weight_change(7) is None
    user.logs.append(make_log(0))
    assert user.weight_change(7) is None


def test_training_days_counts_trained_logs():
    user = make_user()
    user.logs.extend([make_log(0, trained=True), make_log(1, trained=False),
                      make_log(2, trained=True)])
    assert user.training_days(7) == 2


def test_training_days_is_zero_not_none_without_logs():
    # Noll träningsdagar är ett giltigt svar, till skillnad från snitten
    assert make_user().training_days(7) == 0


# ---------------------------------------------------------------------------
# CutProfile: aktuell vikt, basalomsättning, energibehov och proteinmål (F9, F11)
# ---------------------------------------------------------------------------

def test_current_weight_is_start_weight_without_logs():
    assert make_profile(start_weight=90.0).current_weight() == 90.0


def test_current_weight_is_the_weight_of_the_latest_log_by_date():
    profile = make_profile()
    profile.logs.extend([make_log(5, weight=79.0), make_log(2, weight=81.0)])
    assert profile.current_weight() == 79.0


def test_current_weight_is_right_when_a_date_was_typed_without_a_zero():
    # D1: som text är 2026-10-8 senare än 2026-10-10, så vikten från den 8:e hade blivit
    # den aktuella
    profile = make_profile(created_date="2026-10-01")
    profile.logs.extend([DailyLog("2026-10-10", 90.0, 2200, 150, 8000, True),
                         DailyLog("2026-10-8", 85.0, 2200, 150, 8000, True)])
    assert profile.current_weight() == 90.0


def test_bmr_for_a_man_follows_mifflin_st_jeor():
    # 10 * 80 + 6.25 * 180 - 5 * 30 + 5 = 800 + 1125 - 150 + 5 = 1780
    profile = make_profile(sex="man", height_cm=180, age=30,
                           start_weight=80.0, goal_weight=70.0)
    assert profile.calculate_bmr() == pytest.approx(1780)


def test_bmr_for_a_woman_ends_with_minus_161():
    # 800 + 1125 - 150 - 161 = 1614
    profile = make_profile(sex="kvinna", height_cm=180, age=30,
                           start_weight=80.0, goal_weight=70.0)
    assert profile.calculate_bmr() == pytest.approx(1614)


def test_bmr_uses_current_weight_not_start_weight():
    # 10 * 78 + 1125 - 150 + 5 = 1760
    profile = make_profile(sex="man", height_cm=180, age=30,
                           start_weight=80.0, goal_weight=70.0)
    profile.logs.append(make_log(0, weight=78.0))
    assert profile.calculate_bmr() == pytest.approx(1760)


def test_tdee_is_bmr_times_activity_level():
    # 1780 * 1.5 = 2670
    profile = make_profile(sex="man", height_cm=180, age=30, activity_level=1.5,
                           start_weight=80.0, goal_weight=70.0)
    assert profile.calculate_tdee() == pytest.approx(2670)


def test_protein_goal_is_goal_weight_times_grams_per_kg():
    assert make_profile(goal_weight=80.0).protein_goal() == pytest.approx(152.0)  # 80 * 1.9
    assert make_profile(goal_weight=80.0,
                        protein_goal_per_kg=2.1).protein_goal() == pytest.approx(168.0)


# ---------------------------------------------------------------------------
# CutProfile.suggest_calorie_goal: förslag och golv (F9, F10, H1, H4)
# ---------------------------------------------------------------------------

def test_calorie_suggestion_when_the_floor_is_not_reached(capsys):
    # Man, 183 cm, 39 år, aktivitet 1.55, 90 kg, takt 0.7 procent per vecka.
    # BMR  = 900 + 1143.75 - 195 + 5 = 1853.75
    # TDEE = 1853.75 * 1.55 = 2873.3125
    # Underskott = 90 * 0.7 / 100 = 0.63 kg per vecka, 0.63 * 7700 / 7 = 693 kcal per dag
    # Förslag = 2873.3125 - 693 = 2180.3125, avrundat 2180. Golvet är 1853.75 och slår inte i.
    profile = CutProfile("Testperson", 183, 39, "man", 1.55, 90.0, "2026-09-01",
                         goal_weight=82.0, target_rate_percent=0.7)
    assert profile.suggest_calorie_goal() == 2180
    assert profile.calorie_goal == 2180
    assert capsys.readouterr().out == ""  # inget justerades, alltså inget att förklara


def test_calorie_suggestion_uses_current_weight(capsys):
    # Samma person, men senaste loggen är 85 kg.
    # BMR  = 850 + 1143.75 - 195 + 5 = 1803.75
    # TDEE = 1803.75 * 1.55 = 2795.8125
    # Underskott = 85 * 0.7 / 100 * 7700 / 7 = 654.5
    # Förslag = 2795.8125 - 654.5 = 2141.3125, avrundat 2141
    profile = CutProfile("Testperson", 183, 39, "man", 1.55, 90.0, "2026-09-01",
                         goal_weight=82.0, target_rate_percent=0.7)
    profile.logs.append(make_log(0, weight=85.0))
    assert profile.suggest_calorie_goal() == 2141


def test_floor_is_bmr_when_bmr_is_above_the_fixed_floor(capsys):
    # Kvinna, 155 cm, 30 år, aktivitet 1.2, 55 kg, takt 1.0 procent per vecka.
    # BMR  = 550 + 968.75 - 150 - 161 = 1207.75, över det fasta golvet 1200
    # TDEE = 1207.75 * 1.2 = 1449.3
    # Förslag = 1449.3 - 0.55 * 1100 = 844.3, under golvet, alltså blir det 1208
    # Faktiskt underskott = 1449.3 - 1207.75 = 241.55 kcal per dag
    # = 241.55 * 7 / 7700 = 0.2196 kg per vecka = 0.40 procent av 55 kg
    profile = CutProfile("Testperson", 155, 30, "kvinna", 1.2, 55.0, "2026-09-01",
                         goal_weight=50.0, target_rate_percent=1.0)
    assert profile.suggest_calorie_goal() == 1208
    assert capsys.readouterr().out.splitlines() == [
        "Kaloriförslaget hamnade under ditt golv och har justerats upp.",
        "Golvet är 1208 kcal, det högsta av din basalomsättning (1208) och den fasta "
        "gränsen (1200).",
        "Takten blir därför 0.4 procent per vecka i stället för 1.0.",
        "Vill du gå ner snabbare är vägen dit att röra dig mer, inte att äta mindre.",
    ]


def test_suggestion_exactly_at_the_floor_is_not_adjusted(capsys):
    # Man, 180 cm, 46 år, aktivitet 1.5, 75 kg, takt 1.0 procent per vecka.
    # BMR  = 750 + 1125 - 230 + 5 = 1650, över det fasta golvet 1500, så golvet är 1650
    # TDEE = 1650 * 1.5 = 2475
    # Underskott = 75 * 1.0 / 100 = 0.75 kg per vecka, 0.75 * 7700 / 7 = 825 kcal per dag
    # Förslag = 2475 - 825 = 1650, exakt på golvet. Förslaget är inte under golvet, så
    # inget justeras och inget skrivs ut.
    profile = CutProfile("Testperson", 180, 46, "man", 1.5, 75.0, "2026-09-01",
                         goal_weight=70.0, target_rate_percent=1.0)
    assert profile.suggest_calorie_goal() == 1650
    assert capsys.readouterr().out == ""


def test_floor_for_a_woman_is_1200_when_bmr_is_lower_and_no_deficit_is_possible(capsys):
    # Kvinna, 150 cm, 65 år, aktivitet 1.2, 48 kg, takt 1.0 procent per vecka.
    # BMR  = 480 + 937.5 - 325 - 161 = 931.5, under det fasta golvet 1200
    # TDEE = 931.5 * 1.2 = 1117.8, alltså under golvet: inget underskott går att skapa
    profile = CutProfile("Testperson", 150, 65, "kvinna", 1.2, 48.0, "2026-09-01",
                         goal_weight=45.0, target_rate_percent=1.0)
    assert profile.suggest_calorie_goal() == 1200
    assert capsys.readouterr().out.splitlines() == [
        "Kaloriförslaget hamnade under ditt golv och har justerats upp.",
        "Golvet är 1200 kcal, det högsta av din basalomsättning (932) och den fasta "
        "gränsen (1200).",
        "Med ditt golv går det inte att skapa något underskott genom maten.",
        "Vägen framåt är att röra dig mer, inte att äta mindre.",
    ]


def test_floor_for_a_man_is_1500_when_bmr_is_lower(capsys):
    # Man, 170 cm, 60 år, aktivitet 1.3, 70 kg, takt 1.0 procent per vecka.
    # BMR  = 700 + 1062.5 - 300 + 5 = 1467.5, under det fasta golvet 1500
    # TDEE = 1467.5 * 1.3 = 1907.75
    # Förslag = 1907.75 - 0.7 * 1100 = 1137.75, under golvet, alltså blir det 1500
    # Faktiskt underskott = 1907.75 - 1500 = 407.75 kcal per dag
    # = 407.75 * 7 / 7700 = 0.3707 kg per vecka = 0.53 procent av 70 kg
    profile = CutProfile("Testperson", 170, 60, "man", 1.3, 70.0, "2026-09-01",
                         goal_weight=65.0, target_rate_percent=1.0)
    assert profile.suggest_calorie_goal() == 1500
    assert capsys.readouterr().out.splitlines() == [
        "Kaloriförslaget hamnade under ditt golv och har justerats upp.",
        "Golvet är 1500 kcal, det högsta av din basalomsättning (1468) och den fasta "
        "gränsen (1500).",
        "Takten blir därför 0.53 procent per vecka i stället för 1.0.",
        "Vill du gå ner snabbare är vägen dit att röra dig mer, inte att äta mindre.",
    ]


def test_no_deficit_message_when_the_energy_need_equals_the_floor(capsys):
    # Aktivitet 1.0 gör TDEE lika med BMR (1780, över det fasta golvet), så förslaget
    # hamnar under golvet och skillnaden mellan TDEE och golvet är exakt noll
    profile = CutProfile("Testperson", 180, 30, "man", 1.0, 80.0, "2026-09-01",
                         goal_weight=70.0, target_rate_percent=0.6)
    assert profile.suggest_calorie_goal() == 1780
    out = capsys.readouterr().out
    assert "Med ditt golv går det inte att skapa något underskott genom maten." in out


# ---------------------------------------------------------------------------
# CutProfile.days_since_start och waiting_message (F14)
# ---------------------------------------------------------------------------

def profile_with_days_since_start(total_days):
    """Profil skapad dag 0 med en enda logg, så att days_since_start blir total_days."""
    profile = make_profile()
    profile.logs.append(make_log(total_days - 1))
    return profile


def test_days_since_start_is_zero_without_logs():
    assert make_profile().days_since_start() == 0


@pytest.mark.parametrize("total_days", [1, 14, 60])
def test_days_since_start_counts_the_creation_day_as_day_one(total_days):
    assert profile_with_days_since_start(total_days).days_since_start() == total_days


def test_days_since_start_counts_to_the_latest_log_by_date():
    profile = make_profile()
    profile.logs.extend([make_log(9), make_log(2)])  # senaste datumet först
    assert profile.days_since_start() == 10


def test_days_since_start_counts_from_the_start_date_when_the_first_log_comes_later():
    # Profilen skapades dag 0 och första vägningen kom dag 7. Dagarna räknas från startdatumet,
    # så veckan utan loggar räknas med: dag 0 till 13 är 14 dagar.
    profile = make_profile()
    profile.logs.extend([make_log(7), make_log(13)])
    assert profile.days_since_start() == 14


@pytest.mark.parametrize("created_day, log_days, expected", [
    (20, range(0, 14), 14),
    (1, [0], 1),
    (10, range(5, 15), 10),
], ids=["alla-loggar-fore-start", "en-logg-en-dag-fore-start", "loggar-pa-bada-sidor-om-start"])
def test_days_since_start_counts_from_the_earliest_log_when_logs_are_older_than_the_profile(
        created_day, log_days, expected):
    # Så ser det ut när äldre data läses in i en ny profil: menyn ger en ny profil dagens datum
    # som startdatum. Räknat från startdatumet vore svaren -6, 0 och 5. Räknat från den
    # tidigaste loggen till den senaste, med båda dagarna:
    #   dag 0 till 13:   13 - 0 + 1 = 14
    #   dag 0 till 0:     0 - 0 + 1 = 1
    #   dag 5 till 14:   14 - 5 + 1 = 10
    profile = make_profile(created_date=day_text(created_day))
    for day in log_days:
        profile.logs.append(make_log(day))
    assert profile.days_since_start() == expected


def test_days_since_start_finds_the_earliest_log_whatever_the_order_of_the_list():
    # Den tidigaste loggen ligger i mitten av listan. Räknat från startdatumet (dag 12) vore
    # svaret -2, räknat från den första loggen i listan (dag 9) vore det 1. Rätt är dag 0 till
    # 9, alltså 10 dagar.
    profile = make_profile(created_date=day_text(12))
    profile.logs.extend([make_log(9), make_log(0), make_log(5)])
    assert profile.days_since_start() == 10


def test_days_since_start_compares_dates_as_dates_not_as_text():
    # Som text är "2024-01-8" senare än "2024-01-10", eftersom 8 är större än 1. Som datum är
    # den tidigare, så senaste loggen är den 10 januari och 1 till 10 januari är 10 dagar.
    # DailyLog skriver sedan D1 om 2024-01-8 till 2024-01-08, så texten kan inte längre se ut
    # så när loggen skapas. Datumet sätts därför efter att loggen har skapats, för att pröva
    # att days_since_start själv räknar med datum och inte litar på hur texten ser ut.
    profile = make_profile()
    profile.logs.append(DailyLog("2024-01-10", 90.0, 2200, 150, 8000, True))
    eighth = DailyLog("2024-01-08", 90.0, 2200, 150, 8000, True)
    eighth.date = "2024-01-8"
    profile.logs.append(eighth)
    assert profile.days_since_start() == 10


def test_waiting_message_before_one_period_shows_the_days_left():
    message = profile_with_days_since_start(3).waiting_message(7)
    assert "3 dagars data" in message
    # 7 - 3 = 4. Texten före siffran ingår, så att ett minustecken framför fångas.
    assert message.endswith("vore bara brus. 4 dagar kvar tills ett 7-dagarssnitt visas.")


def test_waiting_message_between_one_and_two_periods_shows_the_days_left():
    message = profile_with_days_since_start(10).waiting_message(7)
    assert message.endswith("säkert än. 4 dagar kvar tills full analys är möjlig.")  # 14 - 10


def test_waiting_message_defaults_to_a_seven_day_period():
    profile = profile_with_days_since_start(3)
    assert profile.waiting_message() == profile.waiting_message(7)


@pytest.mark.parametrize("days", [7, 14, 30])
def test_average_is_shown_after_one_period(days):
    before = profile_with_days_since_start(days - 1).waiting_message(days)
    after = profile_with_days_since_start(days).waiting_message(days)
    assert "visas" in before  # väntar på ett första snitt
    assert "full analys" in after  # snittet kan visas, takten kan inte bedömas än


@pytest.mark.parametrize("days, first_full_day", [(7, 14), (14, 28), (30, 60)])
def test_full_analysis_starts_after_two_periods(days, first_full_day):
    # README: full analys från dag 14, 28 respektive 60
    assert profile_with_days_since_start(first_full_day - 1).waiting_message(days) is not None
    assert profile_with_days_since_start(first_full_day).waiting_message(days) is None


def test_logs_older_than_the_profile_count_towards_the_waiting_time():
    # Fjorton dagars loggar (dag 0 till 13), men profilen skapades först dag 30. Dagarna
    # räknas från den tidigaste loggen, så två perioder finns och väntetexten uteblir.
    # Räknat från startdatumet vore dagarna 13 - 30 + 1 = -16.
    profile = make_profile(created_date=day_text(30))
    for day in range(14):
        profile.logs.append(make_log(day))
    assert profile.waiting_message(7) is None


def test_waiting_message_for_logs_older_than_the_profile_shows_no_negative_days():
    # Tre dagars loggar (dag 0 till 2) i en profil skapad dag 30. Dagarna är 3 och det är
    # 7 - 3 = 4 kvar. Räknat från startdatumet vore de -27 och 34 kvar. Texten före siffran
    # ingår, så att ett minustecken framför fångas.
    profile = make_profile(created_date=day_text(30))
    for day in range(3):
        profile.logs.append(make_log(day))
    message = profile.waiting_message(7)
    assert "på 3 dagars data" in message
    assert message.endswith("vore bara brus. 4 dagar kvar tills ett 7-dagarssnitt visas.")


# ---------------------------------------------------------------------------
# CutProfile.check_goals: vilken gren väljs, och i vilken ordning (F12, F13, F17)
# ---------------------------------------------------------------------------

def test_check_goals_during_the_waiting_period_prints_only_the_waiting_message(capsys):
    profile = make_profile()
    profile.logs.append(make_log(3))  # dag 4 sedan start, mindre än en period
    profile.check_goals()
    assert capsys.readouterr().out == profile.waiting_message() + "\n"


def test_check_goals_with_one_log_in_the_window_says_too_little_data(capsys):
    # Profilen skapades långt före loggen, så väntetiden är över, men fönstret har bara en logg
    profile = make_profile(created_date=day_text(-100))
    profile.logs.append(make_log(0))
    profile.check_goals()
    assert "Vikten: för lite data för att bedöma takten." in capsys.readouterr().out


def test_rising_weight_is_flagged_and_gets_focus_before_everything_else(capsys):
    # Protein, steg och träning ligger under målet, men vikten har företräde
    profile = make_checked_profile(weights_changing_by(0.2), protein=100, steps=1000,
                                   trained=False)
    profile.check_goals()
    lines = capsys.readouterr().out.splitlines()
    assert lines[0].startswith("Vikten: ökar med ")
    assert lines[0].endswith("Underskottet räcker inte.")
    assert lines[-1] == "Fokusera på: vikt."


def test_loss_above_the_safety_limit_is_flagged(capsys):
    # En kilo per dag är långt över 1,0 procent per vecka
    profile = make_checked_profile(weights_changing_by(-1.0, start=100.0))
    profile.check_goals()
    lines = capsys.readouterr().out.splitlines()
    assert "över säkerhetsgränsen 1,0 procent" in lines[0]
    assert lines[0].endswith("Risk för muskelförlust.")
    assert lines[-1] == "Fokusera på: vikt."


def test_loss_slower_than_the_goal_is_flagged(capsys):
    # Perioden före väger 90.0 kg och den senaste 89.9 kg: 0,1 kg per vecka, alltså 0,11
    # procent, långt under målet på 0,6 procent
    weights = weights_changing_by(0.0)  # 14 dagar på 90.0 kg ...
    for day in range(7, 14):
        weights[day] = 89.9  # ... men den senaste veckan 100 gram lägre
    profile = make_checked_profile(weights)
    profile.check_goals()
    lines = capsys.readouterr().out.splitlines()
    assert "långsammare än ditt mål på 0.6 procent" in lines[0]
    assert lines[-1] == "Fokusera på: vikt."


def test_loss_at_the_goal_pace_is_reported_as_on_target(capsys):
    # 0,1 kg per dag är 0,7 kg per vecka, över målet på 0,6 procent och under taket 1,0
    profile = make_checked_profile(weights_changing_by(-0.1))
    profile.check_goals()
    lines = capsys.readouterr().out.splitlines()
    assert lines[0].startswith("Vikten: minskar med ")
    assert lines[0].endswith("vid eller över ditt mål på 0.6 procent och inom säkerhetsgränsen.")


@pytest.mark.parametrize("protein, steps, trained, last_line", [
    (100, 1000, False, "Fokusera på: protein."),  # protein kommer före träning och steg
    (200, 1000, False, "Fokusera på: träning."),  # träning kommer före steg
    (200, 1000, True, "Fokusera på: steg."),
    (200, 9000, True, "Allt ligger inom mål just nu. Fortsätt som du gör."),
])
def test_focus_goes_to_the_first_area_below_target(protein, steps, trained, last_line, capsys):
    # Vikten ligger i mål, så ordningen avgörs av protein, träning, steg
    profile = make_checked_profile(weights_changing_by(-0.1), protein=protein,
                                   steps=steps, trained=trained)
    profile.check_goals()
    lines = capsys.readouterr().out.splitlines()
    assert lines[-2] == ""  # en tom rad före sista raden
    assert lines[-1] == last_line


@pytest.mark.parametrize("protein, ending", [(151, "Under målet."), (152, "Målet nås.")])
def test_protein_line_compares_the_average_with_the_goal(protein, ending, capsys):
    # Proteinmålet är 80 * 1.9 = 152 g. Lika med målet räknas som nått.
    profile = make_checked_profile(weights_changing_by(-0.1), protein=protein)
    profile.check_goals()
    assert f"Protein: snitt {protein} g mot mål 152 g. {ending}" in capsys.readouterr().out


@pytest.mark.parametrize("steps, ending", [(7999, "Under målet."), (8000, "Målet nås.")])
def test_steps_line_compares_the_average_with_the_goal(steps, ending, capsys):
    profile = make_checked_profile(weights_changing_by(-0.1), steps=steps)
    profile.check_goals()
    assert f"Steg: snitt {steps} mot mål 8000. {ending}" in capsys.readouterr().out


@pytest.mark.parametrize("trained_days, ending", [(2, "Under målet."), (3, "Målet nås.")])
def test_training_line_compares_trained_days_with_the_goal(trained_days, ending, capsys):
    # Målet är tre dagar på en sjudagarsperiod. Fönstret är dag 7 till 13.
    profile = make_checked_profile(weights_changing_by(-0.1), trained=False)
    for log in profile.logs[7:7 + trained_days]:
        log.trained = True
    profile.check_goals()
    expected = f"Träning: {trained_days} av 3 förväntade dagar under perioden. {ending}"
    assert expected in capsys.readouterr().out


@pytest.mark.parametrize("days, expected_days", [(7, 3), (14, 6), (30, 13)])
def test_training_goal_is_scaled_to_the_period(days, expected_days, capsys):
    # Målet är tre dagar per vecka: 3 * 14 / 7 = 6 och 3 * 30 / 7 = 12.86, avrundat 13
    profile = make_profile(created_date=day_text(-100), training_goal_days=3)
    profile.logs.append(make_log(0, trained=True))
    profile.check_goals(days)
    expected = f"Träning: 1 av {expected_days} förväntade dagar under perioden. Under målet."
    assert expected in capsys.readouterr().out
