"""Tester för diagrammen i analysis.py: plot_weight, plot_protein och plot_steps.

Diagrammen ritas utan fönster. matplotlib använder backend Agg (ingen skärm), och
plt.show ersätts av en funktion som inte gör något. Efter anropet läser testerna linjerna
i figuren: deras namn i förklaringsrutan (label) och deras x- och y-värden.

Alla namn och värden är påhittade.
"""
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402  (måste komma efter matplotlib.use)
import pytest  # noqa: E402

import analysis  # noqa: E402
from analysis import plot_weight, plot_protein, plot_steps  # noqa: E402
from models import DailyLog, CutProfile  # noqa: E402


@pytest.fixture(autouse=True)
def draw_without_a_window(monkeypatch):
    """plt.show öppnar ett fönster och väntar tills det stängs. Här gör den ingenting, och
    alla figurer stängs efter testet så att nästa test börjar utan gamla figurer."""
    monkeypatch.setattr(analysis.plt, "show", lambda: None)
    yield
    plt.close("all")


def make_profile():
    """Proteinmålet blir 62.0 * 2.0 = 124 g och stegmålet 9000."""
    return CutProfile("Anna Berg", 170, 35, "kvinna", 1.4, 70.0, "2026-09-01",
                      goal_weight=62.0, target_rate_percent=0.8,
                      protein_goal_per_kg=2.0, step_goal=9000, training_goal_days=4)


def add_daily_logs(profile, first_day, values, field="weight"):
    """En logg per dag från 2026-09-<first_day>. values är vikt, protein eller steg
    beroende på field, övriga värden är lika för alla loggar."""
    for offset, value in enumerate(values):
        log_values = {"weight": 70.0, "protein": 120, "steps": 8000}
        log_values[field] = value
        day = f"2026-09-{first_day + offset:02d}"
        profile.logs.append(DailyLog(day, log_values["weight"], 2000, log_values["protein"],
                                     log_values["steps"], True))


def lines_by_label():
    """Linjerna i den senaste figuren, med förklaringsrutans namn som nyckel."""
    axes = plt.gcf().axes[0]
    result = {}
    for line in axes.get_lines():
        result[line.get_label()] = line
    return result


def x_values(line):
    return [str(value) for value in line.get_xdata()]


def y_values(line):
    return [round(float(value), 4) for value in line.get_ydata()]


# ---------------------------------------------------------------------------
# Vad diagrammen ritar
# ---------------------------------------------------------------------------

PLOTS = [
    pytest.param(plot_weight, "weight", "Loggad vikt", "Målvikt", 62.0,
                 "Viktutveckling för Anna Berg", "Vikt i kg", id="vikt"),
    pytest.param(plot_protein, "protein", "Loggat protein", "Proteinmål", 124.0,
                 "Proteinintag för Anna Berg", "Protein i gram", id="protein"),
    pytest.param(plot_steps, "steps", "Loggade steg", "Stegmål", 9000.0,
                 "Steg för Anna Berg", "Antal steg", id="steg"),
]


@pytest.mark.parametrize("plot, field, logged_label, goal_label, goal, title, y_label", PLOTS)
def test_chart_draws_the_logged_values_the_average_and_the_goal(
        plot, field, logged_label, goal_label, goal, title, y_label):
    profile = make_profile()
    add_daily_logs(profile, 1, [10, 20, 30, 40, 50, 60, 70, 80], field)

    plot(profile)

    lines = lines_by_label()
    assert set(lines) == {logged_label, "Sjudagarssnitt", goal_label}
    assert x_values(lines[logged_label]) == [f"2026-09-0{day}" for day in range(1, 9)]
    assert y_values(lines[logged_label]) == [10, 20, 30, 40, 50, 60, 70, 80]
    # Mållinjen är vågrät, samma värde i båda ändar
    assert y_values(lines[goal_label]) == [goal, goal]
    axes = plt.gcf().axes[0]
    assert axes.get_title() == title
    assert axes.get_xlabel() == "Datum"
    assert axes.get_ylabel() == y_label


@pytest.mark.parametrize("plot, field, logged_label, goal_label, goal, title, y_label", PLOTS)
def test_chart_sorts_the_logs_by_date(plot, field, logged_label, goal_label, goal, title,
                                      y_label):
    profile = make_profile()
    profile.logs.append(DailyLog("2026-09-03", 70.0, 2000, 120, 8000, True))
    profile.logs.append(DailyLog("2026-09-01", 71.0, 2000, 121, 8001, True))
    profile.logs.append(DailyLog("2026-09-02", 72.0, 2000, 122, 8002, True))

    plot(profile)

    assert x_values(lines_by_label()[logged_label]) == ["2026-09-01", "2026-09-02",
                                                        "2026-09-03"]


@pytest.mark.parametrize("plot", [plot_weight, plot_protein, plot_steps])
def test_chart_needs_at_least_two_logs(plot, capsys):
    profile = make_profile()
    add_daily_logs(profile, 1, [70.0])

    plot(profile)

    assert "Det behövs minst två loggar för att rita ett diagram." in capsys.readouterr().out
    assert plt.get_fignums() == []  # ingen figur skapades


@pytest.mark.parametrize("plot, field, logged_label, goal_label, goal, title, y_label", PLOTS)
def test_chart_draws_no_average_before_seven_days(plot, field, logged_label, goal_label,
                                                  goal, title, y_label):
    profile = make_profile()
    add_daily_logs(profile, 1, [10, 20, 30, 40, 50, 60], field)

    plot(profile)

    assert "Sjudagarssnitt" not in lines_by_label()


@pytest.mark.parametrize("plot, field, logged_label, goal_label, goal, title, y_label", PLOTS)
def test_chart_uses_the_chosen_period(plot, field, logged_label, goal_label, goal, title,
                                      y_label):
    # 40 dagars loggar, 1 september till 10 oktober. Perioden 7 dagar ger bara de sju
    # senaste, 4 till 10 oktober.
    profile = make_profile()
    add_daily_logs(profile, 1, [70] * 30, field)
    for day in range(1, 11):
        profile.logs.append(DailyLog(f"2026-10-{day:02d}", 70.0, 2000, 120, 8000, True))

    plot(profile, 7)

    dates = x_values(lines_by_label()[logged_label])
    assert dates == [f"2026-10-{day:02d}" for day in range(4, 11)]


def test_chart_period_is_30_days_by_default():
    profile = make_profile()
    add_daily_logs(profile, 1, [70.0] * 30)
    for day in range(1, 11):
        profile.logs.append(DailyLog(f"2026-10-{day:02d}", 70.0, 2000, 120, 8000, True))

    plot_weight(profile)

    dates = x_values(lines_by_label()["Loggad vikt"])
    assert len(dates) == 30
    assert dates[0] == "2026-09-11"


# ---------------------------------------------------------------------------
# Sjudagarssnittet räknas i kalenderdagar, som alla andra snitt i programmet (D3)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("plot, field, logged_label, goal_label, goal, title, y_label", PLOTS)
def test_seven_day_average_with_a_log_every_day(plot, field, logged_label, goal_label,
                                                goal, title, y_label):
    # En logg per dag i åtta dagar. Dag 7: snitt av 10 till 70 = 40. Dag 8: 20 till 80 = 50.
    profile = make_profile()
    add_daily_logs(profile, 1, [10, 20, 30, 40, 50, 60, 70, 80], field)

    plot(profile)

    average = lines_by_label()["Sjudagarssnitt"]
    assert x_values(average) == ["2026-09-07", "2026-09-08"]
    assert y_values(average) == [40, 50]


@pytest.mark.parametrize("plot, field, logged_label, goal_label, goal, title, y_label", PLOTS)
def test_seven_day_average_counts_calendar_days_not_logs(plot, field, logged_label,
                                                         goal_label, goal, title, y_label):
    # Loggar varannan dag: 1, 3, 5, ... 17 september. Ett snitt över sju kalenderdagar
    # innehåller då tre eller fyra loggar, inte sju. Förut räknades de sju senaste
    # loggarna, alltså tretton dagar, och kallades ändå sjudagarssnitt.
    profile = make_profile()
    values = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    for index, value in enumerate(values):
        log_values = {"weight": 70.0, "protein": 120, "steps": 8000}
        log_values[field] = value
        day = f"2026-09-{1 + 2 * index:02d}"
        profile.logs.append(DailyLog(day, log_values["weight"], 2000, log_values["protein"],
                                     log_values["steps"], True))

    plot(profile)

    average = lines_by_label()["Sjudagarssnitt"]
    # Första punkten är 7 september, den första loggen minst sex dagar efter den första
    # loggen. Fönstret 1 till 7 september har 10, 20, 30 och 40: snitt 25.
    # 9 september: 3 till 9 september, 20 till 50: snitt 35. Och så vidare.
    assert x_values(average) == ["2026-09-07", "2026-09-09", "2026-09-11", "2026-09-13",
                                 "2026-09-15", "2026-09-17"]
    assert y_values(average) == [25, 35, 45, 55, 65, 75]


def test_seven_day_average_skips_a_gap_without_logs_in_the_window():
    # Dag 1 till 7, sedan ett uppehåll till dag 20. Dag 20:s fönster (14 till 20) har bara
    # dag 20, så snittet är dess eget värde. Förut blandades dag 2 till 7 in.
    profile = make_profile()
    add_daily_logs(profile, 1, [70, 70, 70, 70, 70, 70, 70])
    profile.logs.append(DailyLog("2026-09-20", 63.0, 2000, 120, 8000, True))

    plot_weight(profile)

    average = lines_by_label()["Sjudagarssnitt"]
    assert x_values(average) == ["2026-09-07", "2026-09-20"]
    assert y_values(average) == [70, 63]
