from pathlib import Path


def test_required_project_structure_exists():
    required_paths = [
        "README.md",
        "requirements.txt",
        "scripts/run_change_point.py",
        "scripts/run_event_analysis.py",
        "dashboard/backend/app.py",
        "dashboard/frontend/src/App.jsx",
        "reports/figures",
    ]

    for required_path in required_paths:
        assert Path(required_path).exists(), (
            f"Required project path is missing: {required_path}"
        )


def test_analysis_figures_exist():
    expected_figures = [
        "reports/figures/change_point.png",
        "reports/figures/trace_plot.png",
        "reports/figures/tau_posterior.png",
        "reports/figures/mean_posterior.png",
        "reports/figures/event_impacts.png",
        "reports/figures/events_on_price_series.png",
    ]

    for figure_path in expected_figures:
        assert Path(figure_path).exists(), (
            f"Expected analytical figure is missing: {figure_path}"
        )
