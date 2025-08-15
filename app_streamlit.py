
import streamlit as st
import pandas as pd
import numpy as np
from report_utils import build_pdf

st.set_page_config(page_title="TrustLens Demo", layout="wide")
st.title("TrustLens – Fairness & Explainability Demo")

@st.cache_data
def load_sample():
    return pd.read_csv("data/adult_tiny.csv")

with st.sidebar:
    st.header("Data")
    use_sample = st.checkbox("Use sample dataset", True)
    if use_sample:
        df = load_sample()
    else:
        f = st.file_uploader("Upload CSV", type=["csv"])
        if f: df = pd.read_csv(f)
        else: df = load_sample()
    st.success(f"Rows: {len(df)}")
    st.caption("Protected attributes: try 'sex' and 'race'")

tab1, tab2, tab3, tab4 = st.tabs(["Preview","Audit","Explain","Export"])

with tab1:
    st.subheader("Preview")
    st.dataframe(df.head(20), use_container_width=True)

def demographic_parity_ratio(y_pred, groups):
    ratios = {}
    for g in groups.unique():
        mask = (groups == g)
        if mask.sum() > 0:
            ratios[str(g)] = y_pred[mask].mean()
    vals = [v for v in ratios.values() if pd.notnull(v)]
    di = (min(vals)/max(vals)) if len(vals)>=2 and max(vals)>0 else None
    return ratios, di

with tab2:
    st.subheader("Fairness Audit (toy)")
    target = st.selectbox("Target label", [c for c in df.columns if c in ("income","label","y")], index=0 if "income" in df.columns else 0)
    protected = st.multiselect("Protected attributes", [c for c in df.columns if df[c].dtype=='O' or df[c].nunique()<10], default=[c for c in ["sex","race"] if c in df.columns])
    rule = st.selectbox("Toy model", ["education_num >= 12","hours_per_week >= 40","majority class"])
    if st.button("Run Audit"):
        y_true = df[target].values if target in df else None
        if rule=="education_num >= 12":
            y_pred = (df.get("education_num", 0) >= 12).astype(int).values
        elif rule=="hours_per_week >= 40":
            y_pred = (df.get("hours_per_week", 0) >= 40).astype(int).values
        else:
            y_pred = np.full(len(df), int(round(df[target].mean()))) if target in df else np.zeros(len(df))
        st.write("Toy accuracy:", (y_pred==y_true).mean() if y_true is not None else "n/a")
        for p in protected:
            ratios, di = demographic_parity_ratio(pd.Series(y_pred), df[p])
            st.write(f"**{p}** positive rate:", ratios, " | disparate impact:", round(di,3) if di is not None else "n/a")
        st.session_state["audit"] = {"prot": protected, "rule": rule}

with tab3:
    st.subheader("Explainability (proxy)")
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and c!= "income"]
    if "income" in df and num_cols:
        corr = df[num_cols+[ "income"]].corr()["income"].drop("income")
        st.bar_chart(corr.fillna(0))
        st.caption("Correlation with label as global-importance proxy.")
        st.session_state["explain"] = {"corr": corr.to_dict()}
    else:
        st.warning("Need numeric features + 'income' label.")

with tab4:
    st.subheader("Export PDF")
    title = st.text_input("Title","TrustLens Demo Report")
    if st.button("Generate"):
        audit = st.session_state.get("audit",{})
        explain = st.session_state.get("explain",{})
        lines = [f"Audit rule: {audit.get('rule')}", f"Protected attrs: {audit.get('prot')}"]
        if "corr" in explain:
            top = sorted(explain["corr"].items(), key=lambda x: abs(x[1] or 0), reverse=True)[:5]
            lines.append("Top correlations:")
            for k,v in top: lines.append(f" - {k}: {round(v,3)}")
        build_pdf("trustlens_demo_report.pdf", title=title, summary="\n".join(lines))
        with open("trustlens_demo_report.pdf","rb") as fp:
            st.download_button("Download PDF", data=fp.read(), file_name="trustlens_demo_report.pdf", mime="application/pdf")
