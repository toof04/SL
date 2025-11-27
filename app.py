import os
from flask import Flask, request, jsonify, render_template, send_from_directory
import pandas as pd

app = Flask(__name__, static_folder='static', template_folder='templates')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def join_safely(base_dir, *extra_bits):
    target_path = os.path.normpath(os.path.join(base_dir, *extra_bits))
    if os.path.commonpath([base_dir, target_path]) != base_dir:
        raise ValueError("bad path")
    return target_path


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/list", methods=["GET"])
def list_dir():
    sub = (request.args.get("subpath") or "").strip()
    plots_root = join_safely(ROOT_DIR, "plots")

    try:
        base_here = join_safely(plots_root, sub) if sub else plots_root
    except ValueError:
        return jsonify({"error": "invalid path"}), 400

    if not os.path.exists(base_here):
        return jsonify({"dirs": [], "files": []})

    stuff = os.listdir(base_here)
    only_dirs = sorted(
        [d for d in stuff if os.path.isdir(os.path.join(base_here, d))]
    )
    csv_like = sorted(
        [
            f
            for f in stuff
            if os.path.isfile(os.path.join(base_here, f))
            and f.lower().endswith(".csv")
        ]
    )

    return jsonify({"dirs": only_dirs, "files": csv_like})


@app.route("/api/plot/total_default", methods=["GET"])
def total_default():
    csv_path = join_safely(
        ROOT_DIR, "plots", "crime", "total_crime", "default", "default.csv"
    )

    if not os.path.exists(csv_path):
        return jsonify({"error": "default csv not found"}), 404

    frame = pd.read_csv(csv_path)

    if "State" not in frame.columns or "Total_2020_2022" not in frame.columns:
        return jsonify({"error": "unexpected columns"}), 400

    labels = frame["State"].astype(str).tolist()
    vals = frame["Total_2020_2022"].fillna(0).astype(float).tolist()
    return jsonify({"chartType": "bar", "labels": labels, "values": vals})


@app.route("/api/plot/file", methods=["GET"])
def plot_file():
    subpath = (request.args.get("subpath") or "").strip()
    fname = (request.args.get("file") or "").strip()

    if not fname:
        return jsonify({"error": "file required"}), 400

    override = (request.args.get("chart") or "").strip().lower()
    if override not in ("bar", "pie"):
        override = ""

    try:
        if subpath:
            full_dir = join_safely(ROOT_DIR, "plots", *subpath.split("/"))
        else:
            full_dir = join_safely(ROOT_DIR, "plots")
    except ValueError:
        return jsonify({"error": "invalid subpath"}), 400

    file_path = join_safely(full_dir, fname)

    if not os.path.exists(file_path):
        return jsonify({"error": "file not found"}), 404

    df_raw = pd.read_csv(file_path)
    path_bits = subpath.split("/") if subpath else []

    chart_kind = "bar"
    lbls = []
    vals = []

    if subpath.startswith("crime/"):
        chart_kind, lbls, vals = handle_crime_data(df_raw, path_bits, subpath, fname)
    elif subpath.startswith("education/"):
        chart_kind, lbls, vals = handle_education_data(df_raw, path_bits, subpath, fname)
    elif subpath.startswith("infrastructure/"):
        chart_kind, lbls, vals = handle_infrastructure_data(
            df_raw, path_bits, subpath, fname
        )
    elif subpath.startswith("employment/"):
        chart_kind, lbls, vals = handle_employment_data(df_raw, path_bits, subpath, fname)
    else:
        if df_raw.shape[1] >= 2:
            lbls = df_raw.iloc[:, 0].astype(str).tolist()
            vals = pd.to_numeric(df_raw.iloc[:, 1], errors="coerce").fillna(0).tolist()
        else:
            return jsonify({"error": "CSV does not have suitable columns"}), 400

    if override and chart_kind not in ("line", "multiline"):
        chart_kind = override

    if chart_kind == "multiline" and isinstance(vals, list) and vals and isinstance(
        vals[0], dict
    ):
        return jsonify({"chartType": "multiline", "labels": lbls, "series": vals})

    if chart_kind == "groupedbar" and isinstance(vals, list) and vals and isinstance(
        vals[0], dict
    ):
        return jsonify({"chartType": "groupedbar", "labels": lbls, "series": vals})

    if chart_kind == "stackedbar" and isinstance(vals, list) and vals and isinstance(
        vals[0], dict
    ):
        return jsonify({"chartType": "stackedbar", "labels": lbls, "series": vals})

    if not isinstance(vals, list):
        vals = []

    return jsonify({"chartType": chart_kind, "labels": lbls, "values": vals})


def handle_crime_data(df_obj, bits, subpath, filename):
    chart_kind = "bar"
    lbls = []
    vals = []

    if subpath.startswith("crime/total_crime"):
        chart_kind, lbls, vals = handle_total_crime(df_obj, bits)
    elif subpath.startswith("crime/religion"):
        chart_kind, lbls, vals = handle_religion(df_obj, bits, subpath)
    elif subpath.startswith("crime/women"):
        chart_kind, lbls, vals = handle_women(df_obj, bits, filename)
    elif subpath.startswith("crime/education"):
        chart_kind, lbls, vals = handle_crime_education(df_obj, bits)
    elif subpath.startswith("crime/caste"):
        chart_kind, lbls, vals = handle_caste(df_obj, bits)
    elif subpath.startswith("crime/police"):
        chart_kind, lbls, vals = handle_police(df_obj, bits, subpath)
    elif subpath.startswith("crime/children"):
        chart_kind, lbls, vals = handle_children(df_obj, bits, subpath)
    else:
        if df_obj.shape[1] >= 2:
            lbls = df_obj.iloc[:, 0].astype(str).tolist()
            vals = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()

    if not lbls and df_obj.shape[1] >= 2:
        lbls = df_obj.iloc[:, 0].astype(str).tolist()
        vals = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()

    return chart_kind, lbls, vals


def handle_total_crime(df_obj, bits):
    if "top_10" in bits or "bottom_10" in bits:
        if df_obj.shape[1] >= 2:
            lbls = df_obj.iloc[:, 0].astype(str).tolist()
            vals = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
            return "bar", lbls, vals
    elif "time_series" in bits:
        if "Year" in df_obj.columns and "Value" in df_obj.columns:
            lbls = df_obj["Year"].astype(str).tolist()
            vals = df_obj["Value"].fillna(0).astype(float).tolist()
            return "line", lbls, vals
    else:
        if "State" in df_obj.columns and "Total_2020_2022" in df_obj.columns:
            lbls = df_obj["State"].astype(str).tolist()
            vals = df_obj["Total_2020_2022"].fillna(0).astype(float).tolist()
            return "bar", lbls, vals
        elif df_obj.shape[1] >= 2:
            lbls = df_obj.iloc[:, 0].astype(str).tolist()
            vals = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
            return "bar", lbls, vals

    return "bar", [], []


def handle_religion(df_obj, bits, subpath):
    if subpath == "crime/religion/default":
        religion_cols = ["Hindu", "Muslim", "Sikh", "Christian", "Others"]
        avail = [c for c in df_obj.columns if c in religion_cols]

        if len(avail) < 2:
            col_map = {c.lower(): c for c in df_obj.columns}
            avail = []
            for r in religion_cols:
                if r.lower() in col_map:
                    avail.append(col_map[r.lower()])

        if len(avail) >= 2:
            state_col = None
            for c in ["State/UT", "State", "State_UT"]:
                if c in df_obj.columns:
                    state_col = c
                    break

            if state_col:
                tmp = df_obj[
                    ~df_obj[state_col]
                    .astype(str)
                    .str.contains("Total", case=False, na=False)
                ].copy()
                labels = tmp[state_col].astype(str).tolist()
            else:
                tmp = df_obj[
                    ~df_obj.iloc[:, 0]
                    .astype(str)
                    .str.contains("Total", case=False, na=False)
                ].copy()
                labels = tmp.iloc[:, 0].astype(str).tolist()

            series_list = []
            for rc in avail:
                series_list.append(
                    {
                        "label": rc,
                        "data": pd.to_numeric(tmp[rc], errors="coerce")
                        .fillna(0)
                        .tolist(),
                    }
                )
            return "stackedbar", labels, series_list
        else:
            col_map = {c.lower(): c for c in df_obj.columns}
            if "religion" in col_map:
                val_col = col_map.get(
                    "% of india",
                    col_map.get("percent", col_map.get("value")),
                )
                if val_col:
                    labels = df_obj[col_map["religion"]].astype(str).tolist()
                    values = pd.to_numeric(df_obj[val_col], errors="coerce").fillna(0).tolist()
                    return "pie", labels, values

    elif "top" in bits or "bottom" in bits:
        if df_obj.shape[1] >= 2:
            labels = df_obj.iloc[:, 0].astype(str).tolist()
            values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
            return "bar", labels, values
    elif "states" in bits or "religion" in bits:
        if df_obj.shape[1] >= 2:
            labels = df_obj.iloc[:, 0].astype(str).tolist()
            values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
            chart_kind = "pie" if "states" in bits else "bar"
            return chart_kind, labels, values

    if df_obj.shape[1] >= 2:
        labels = df_obj.iloc[:, 0].astype(str).tolist()
        values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
        return "bar", labels, values

    return "bar", [], []


def handle_women(df_obj, bits, filename):
    low_name = filename.lower()
    if "default" in bits:
        if "State" in df_obj.columns and "Total_cases" in df_obj.columns:
            labels = df_obj["State"].astype(str).tolist()
            values = df_obj["Total_cases"].fillna(0).astype(float).tolist()
            return "bar", labels, values
    elif "states" in bits or "Crime_types" in bits or "crime_types" in [p.lower() for p in bits]:
        if df_obj.shape[1] >= 2:
            labels = df_obj.iloc[:, 0].astype(str).tolist()
            values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
            return "bar", labels, values
    elif "time_series" in bits:
        if low_name.startswith("national"):
            if "Year" in df_obj.columns and "Total_cases" in df_obj.columns:
                labels = df_obj["Year"].astype(str).tolist()
                values = df_obj["Total_cases"].fillna(0).astype(float).tolist()
                return "line", labels, values
        elif low_name.startswith("crime"):
            if df_obj.shape[1] >= 2:
                labels = df_obj.iloc[:, 0].astype(str).tolist()
                series_list = []
                for colname in df_obj.columns[1:]:
                    series_list.append(
                        {
                            "label": colname,
                            "data": pd.to_numeric(df_obj[colname], errors="coerce")
                            .fillna(0)
                            .tolist(),
                        }
                    )
                return "multiline", labels, series_list
        else:
            if "Year" in df_obj.columns and "Value" in df_obj.columns:
                labels = df_obj["Year"].astype(str).tolist()
                values = df_obj["Value"].fillna(0).astype(float).tolist()
                return "line", labels, values

    if df_obj.shape[1] >= 2:
        labels = df_obj.iloc[:, 0].astype(str).tolist()
        values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
        return "bar", labels, values

    return "bar", [], []


def handle_crime_education(df_obj, bits):
    if "education" in bits and "state" not in bits:
        if df_obj.shape[1] >= 2:
            labels = df_obj.iloc[:, 0].astype(str).tolist()
            values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
            return "bar", labels, values
    elif "state" in bits:
        if df_obj.shape[1] >= 2:
            labels = df_obj.iloc[:, 0].astype(str).tolist()
            values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
            return "pie", labels, values

    if df_obj.shape[1] >= 2:
        labels = df_obj.iloc[:, 0].astype(str).tolist()
        values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
        return "bar", labels, values

    return "bar", [], []


def handle_caste(df_obj, bits):
    if "caste_convicts_analysis" in bits:
        if "top" in bits or "bottom" in bits:
            labels = df_obj.iloc[:, 0].astype(str).tolist()
            values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
            return "bar", labels, values
        elif "caste" in bits:
            labels = df_obj.iloc[:, 0].astype(str).tolist()
            values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
            return "pie", labels, values
    elif "detenues_caste_analysis" in bits:
        if "caste" in bits:
            labels = df_obj.iloc[:, 0].astype(str).tolist()
            values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
            return "bar", labels, values
        elif "state" in bits:
            cmap = {c.lower(): c for c in df_obj.columns}
            guess_col = None
            for cand in ["total", "total_cases", "total_detenues", "total_cases_count"]:
                if cand in cmap:
                    guess_col = cmap[cand]
                    break
            if not guess_col and df_obj.shape[1] > 1:
                guess_col = df_obj.columns[-1]
            if guess_col:
                labels = df_obj.iloc[:, 0].astype(str).tolist()
                values = pd.to_numeric(df_obj[guess_col], errors="coerce").fillna(0).tolist()
                return "bar", labels, values

    if df_obj.shape[1] >= 2:
        labels = df_obj.iloc[:, 0].astype(str).tolist()
        values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
        return "bar", labels, values

    return "bar", [], []


def handle_police(df_obj, bits, subpath):
    if subpath == "crime/police/police/default":
        cmap = {c.lower(): c for c in df_obj.columns}
        if "indicator" in cmap and (
            "all india total" in cmap or "all_india_total" in cmap
        ):
            xcol = cmap["indicator"]
            ycol = cmap.get("all india total", cmap.get("all_india_total"))
            labels = df_obj[xcol].astype(str).tolist()
            values = pd.to_numeric(df_obj[ycol], errors="coerce").fillna(0).tolist()
            return "bar", labels, values
    elif "top" in bits:
        labels = df_obj.iloc[:, 0].astype(str).tolist()
        values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
        return "bar", labels, values
    elif "percent" in bits:
        cmap = {c.lower(): c for c in df_obj.columns}
        col_guess = None
        for cand in ["percent", "% of state", "% of india", "%", "value"]:
            if cand in cmap:
                col_guess = cmap[cand]
                break
        if not col_guess and df_obj.shape[1] >= 2:
            col_guess = df_obj.columns[1]
        if col_guess:
            labels = df_obj.iloc[:, 0].astype(str).tolist()
            values = pd.to_numeric(df_obj[col_guess], errors="coerce").fillna(0).tolist()
            return "bar", labels, values

    if df_obj.shape[1] >= 2:
        labels = df_obj.iloc[:, 0].astype(str).tolist()
        values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
        return "bar", labels, values

    return "bar", [], []


def handle_children(df_obj, bits, subpath):
    if "default" in bits:
        if df_obj.shape[1] >= 2:
            labels = df_obj.iloc[:, 0].astype(str).tolist()
            values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
            return "bar", labels, values
    elif "TopStates" in bits or "TopCrime" in bits:
        if df_obj.shape[1] >= 2:
            labels = df_obj.iloc[:, 0].astype(str).tolist()
            values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
            return "bar", labels, values

    if df_obj.shape[1] >= 2:
        labels = df_obj.iloc[:, 0].astype(str).tolist()
        values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
        return "bar", labels, values

    return "bar", [], []


def handle_education_data(df_obj, bits, subpath, filename):
    chart_kind = "bar"
    lbls = []
    vals = []

    if "schools" in bits:
        if "state" in bits and "best" not in bits:
            if "Level" in df_obj.columns and df_obj.shape[1] >= 3:
                lbls = df_obj["Level"].astype(str).tolist()
                vals = (
                    pd.to_numeric(df_obj.iloc[:, 2], errors="coerce")
                    .fillna(0)
                    .tolist()
                )
                return "bar", lbls, vals
        elif "best" in bits:
            if df_obj.shape[1] >= 2:
                lbls = df_obj.iloc[:, 0].astype(str).tolist()
                vals = (
                    pd.to_numeric(df_obj.iloc[:, 1], errors="coerce")
                    .fillna(0)
                    .tolist()
                )
                return "bar", lbls, vals

    elif "logistics" in bits:
        if df_obj.shape[1] >= 2:
            lbls = df_obj.iloc[:, 0].astype(str).tolist()
            idx = 2 if "girls_toilet" in bits else 1
            if df_obj.shape[1] > idx:
                vals = (
                    pd.to_numeric(df_obj.iloc[:, idx], errors="coerce")
                    .fillna(0)
                    .tolist()
                )
            else:
                vals = (
                    pd.to_numeric(df_obj.iloc[:, 1], errors="coerce")
                    .fillna(0)
                    .tolist()
                )
            return "bar", lbls, vals

    elif "rate" in bits:
        if "dropout" in bits:
            chart_kind, lbls, vals = handle_dropout(df_obj, bits)
            return chart_kind, lbls, vals
        elif "year_of_school" in bits:
            chart_kind, lbls, vals = handle_year_of_school(df_obj, bits)
            return chart_kind, lbls, vals
        else:
            chart_kind, lbls, vals = handle_literacy_rate(df_obj, bits)
            return chart_kind, lbls, vals

    if df_obj.shape[1] >= 2:
        lbls = df_obj.iloc[:, 0].astype(str).tolist()
        vals = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
        return "bar", lbls, vals

    return chart_kind, lbls, vals


def handle_dropout(df_obj, bits):
    if "state_level" in bits:
        if "Gender" in df_obj.columns and df_obj.shape[1] >= 2:
            labels = df_obj["Gender"].astype(str).tolist()
            values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
            return "bar", labels, values
    elif "state_gender" in bits:
        if "Level" in df_obj.columns and df_obj.shape[1] >= 2:
            labels = df_obj["Level"].astype(str).tolist()
            values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
            return "bar", labels, values
    elif "level_gender" in bits:
        if "State" in df_obj.columns and df_obj.shape[1] >= 2:
            labels = df_obj["State"].astype(str).tolist()
            values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
            return "bar", labels, values

    if df_obj.shape[1] >= 2:
        labels = df_obj.iloc[:, 0].astype(str).tolist()
        values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
        return "bar", labels, values

    return "bar", [], []


def handle_literacy_rate(df_obj, bits):
    if "top" in bits or "bottom" in bits:
        if df_obj.shape[1] >= 2:
            labels = df_obj.columns[1:].tolist()
            series = []
            for _, row in df_obj.iterrows():
                state_name = str(row.iloc[0])
                data_vals = (
                    pd.to_numeric(row.iloc[1:], errors="coerce").fillna(0).tolist()
                )
                series.append({"label": state_name, "data": data_vals})
            return "multiline", labels, series
    elif "state_outputs" in bits:
        if "Year" in df_obj.columns and df_obj.shape[1] >= 2:
            labels = df_obj["Year"].astype(str).tolist()
            values = (
                pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
            )
            return "line", labels, values

    if df_obj.shape[1] >= 2:
        labels = df_obj.iloc[:, 0].astype(str).tolist()
        values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
        return "bar", labels, values

    return "bar", [], []


def handle_year_of_school(df_obj, bits):
    if "top" in bits or "bottom" in bits:
        if df_obj.shape[1] >= 2:
            labels = df_obj.columns[1:].tolist()
            series = []
            for _, row in df_obj.iterrows():
                state_name = str(row.iloc[0])
                data_vals = (
                    pd.to_numeric(row.iloc[1:], errors="coerce").fillna(0).tolist()
                )
                series.append({"label": state_name, "data": data_vals})
            return "multiline", labels, series
    elif "statewise_outputs" in bits:
        if df_obj.shape[1] >= 2:
            labels = df_obj.columns[1:].tolist()
            values = (
                pd.to_numeric(df_obj.iloc[0, 1:], errors="coerce").fillna(0).tolist()
            )
            return "line", labels, values

    if df_obj.shape[1] >= 2:
        labels = df_obj.iloc[:, 0].astype(str).tolist()
        values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
        return "bar", labels, values

    return "bar", [], []


def handle_infrastructure_data(df_obj, bits, subpath, filename):
    if df_obj.shape[1] >= 2:
        labels = df_obj.columns[1:].tolist()
        series = []
        for _, row in df_obj.iterrows():
            name_here = str(row.iloc[0])
            vals = pd.to_numeric(row.iloc[1:], errors="coerce").fillna(0).tolist()
            series.append({"label": name_here, "data": vals})
        return "multiline", labels, series

    return "bar", [], []


def handle_employment_data(df_obj, bits, subpath, filename):
    chart_kind = "bar"
    labels = []
    values = []

    if "jobseeker" in bits:
        if "default" in bits or "top" in bits or "bottom" in bits:
            if "State" in df_obj.columns and "Percentage" in df_obj.columns:
                labels = df_obj["State"].astype(str).tolist()
                values = (
                    pd.to_numeric(df_obj["Percentage"], errors="coerce")
                    .fillna(0)
                    .tolist()
                )
                return "bar", labels, values
            elif df_obj.shape[1] >= 2:
                labels = df_obj.iloc[:, 0].astype(str).tolist()
                values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
                return "bar", labels, values
        elif "statewise" in bits:
            if "Grand Total" in df_obj.columns and "Mobilised Vacancies" in df_obj.columns:
                if "State" in df_obj.columns:
                    labels = df_obj["State"].astype(str).tolist()
                else:
                    labels = df_obj.iloc[:, 0].astype(str).tolist()

                series = []
                series.append(
                    {
                        "label": "Grand Total",
                        "data": pd.to_numeric(
                            df_obj["Grand Total"], errors="coerce"
                        ).fillna(0).tolist(),
                    }
                )
                series.append(
                    {
                        "label": "Mobilised Vacancies",
                        "data": pd.to_numeric(
                            df_obj["Mobilised Vacancies"], errors="coerce"
                        ).fillna(0).tolist(),
                    }
                )
                return "groupedbar", labels, series
            elif df_obj.shape[1] >= 3:
                labels = df_obj.iloc[:, 0].astype(str).tolist()
                series = []
                series.append(
                    {
                        "label": df_obj.columns[1],
                        "data": pd.to_numeric(df_obj.iloc[:, 1], errors="coerce")
                        .fillna(0)
                        .tolist(),
                    }
                )
                series.append(
                    {
                        "label": df_obj.columns[2],
                        "data": pd.to_numeric(df_obj.iloc[:, 2], errors="coerce")
                        .fillna(0)
                        .tolist(),
                    }
                )
                return "groupedbar", labels, series
            elif df_obj.shape[1] >= 2:
                labels = df_obj.iloc[:, 0].astype(str).tolist()
                values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
                return "bar", labels, values

    elif "registered_statewise" in bits:
        if "State_Name" in df_obj.columns and "Registration_count" in df_obj.columns:
            labels = df_obj["State_Name"].astype(str).tolist()
            values = (
                pd.to_numeric(df_obj["Registration_count"], errors="coerce")
                .fillna(0)
                .tolist()
            )
            return "bar", labels, values
        elif df_obj.shape[1] >= 2:
            labels = df_obj.iloc[:, 0].astype(str).tolist()
            values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
            return "bar", labels, values

    elif "occupation" in bits:
        if df_obj.shape[1] >= 2:
            labels = df_obj.iloc[:, 0].astype(str).tolist()
            values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
            return "bar", labels, values

    elif "agegender" in bits:
        if "age" in bits:
            if df_obj.shape[1] >= 2:
                labels = df_obj.iloc[:, 0].astype(str).tolist()
                values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
                return "bar", labels, values
        elif "gender" in bits or "gender_reg" in bits:
            if df_obj.shape[1] >= 4:
                labels = df_obj.iloc[:, 1].astype(str).tolist()
                values = pd.to_numeric(df_obj.iloc[:, 3], errors="coerce").fillna(0).tolist()
                return "pie", labels, values
            elif df_obj.shape[1] >= 2:
                labels = df_obj.iloc[:, 0].astype(str).tolist()
                values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
                return "pie", labels, values

    if df_obj.shape[1] >= 2:
        labels = df_obj.iloc[:, 0].astype(str).tolist()
        values = pd.to_numeric(df_obj.iloc[:, 1], errors="coerce").fillna(0).tolist()
        return "bar", labels, values

    return chart_kind, labels, values


@app.route("/api/csv/data", methods=["GET"])
def get_csv_data():
    subpath = (request.args.get("subpath") or "").strip()
    fname = (request.args.get("file") or "").strip()

    if not fname:
        return jsonify({"error": "file required"}), 400

    try:
        if subpath:
            base_dir = join_safely(ROOT_DIR, "plots", *subpath.split("/"))
        else:
            base_dir = join_safely(ROOT_DIR, "plots")
    except ValueError:
        return jsonify({"error": "invalid subpath"}), 400

    csv_path = join_safely(base_dir, fname)
    if not os.path.exists(csv_path):
        return jsonify({"error": "file not found"}), 404

    try:
        df_obj = pd.read_csv(csv_path)
        rows = df_obj.to_dict("records")
        for row in rows:
            for k, v in list(row.items()):
                if pd.isna(v):
                    row[k] = ""
                else:
                    row[k] = str(v)
        return jsonify({"columns": df_obj.columns.tolist(), "data": rows})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)


if __name__ == "__main__":
    app.run(debug=True)
