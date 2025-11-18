# analyze_market_fit.py
import re
import pandas as pd

def _parse_comp_series(series: pd.Series) -> pd.Series:
    def parse_one(x):
        if pd.isna(x):
            return None
        s = str(x).strip()
        if s.lower() in {"unknown", "competitive", "n/a", "na", ""}:
            return None
        s = re.sub(r"[^\d\-\.\s]", "", s)  # quita moneda y comas
        nums = re.findall(r"\d+(?:\.\d+)?", s)
        if not nums:
            return None
        vals = [float(n) for n in nums]
        return sum(vals) / len(vals)

    return series.apply(parse_one)

def analyze_market_fit(sheet_data: list[dict], cv_summary: str | None = None) -> dict:
    """
    sheet_data: lista de dicts con al menos 'Comp' (o 'Salary') y 'FitScore' (o 'Fit').
    """
    df = pd.DataFrame(sheet_data)

    # columnas tolerantes
    comp_col = "Comp" if "Comp" in df.columns else ("Salary" if "Salary" in df.columns else None)
    fit_col  = "FitScore" if "FitScore" in df.columns else ("Fit" if "Fit" in df.columns else None)

    if comp_col:
        df["Comp_clean"] = _parse_comp_series(df[comp_col])
    else:
        df["Comp_clean"] = None

    if fit_col:
        # fuerza numérico si es posible
        df["Fit_clean"] = pd.to_numeric(df[fit_col], errors="coerce")
    else:
        df["Fit_clean"] = None

    max_salary = float(df["Comp_clean"].max()) if df["Comp_clean"].notna().any() else None
    min_salary = float(df["Comp_clean"].min()) if df["Comp_clean"].notna().any() else None
    avg_salary = float(df["Comp_clean"].mean()) if df["Comp_clean"].notna().any() else None
    avg_fit    = float(df["Fit_clean"].mean()) if df["Fit_clean"].notna().any() else None

    return {
        "max_salary": round(max_salary, 2) if max_salary is not None else None,
        "min_salary": round(min_salary, 2) if min_salary is not None else None,
        "avg_salary": round(avg_salary, 2) if avg_salary is not None else None,
        "avg_fit": round(avg_fit, 2) if avg_fit is not None else None
    }
