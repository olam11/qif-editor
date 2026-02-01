import streamlit as st
import pandas as pd
import re

# -----------------------------
# 🎨 STYLE GLOBAL
# -----------------------------
st.set_page_config(
    page_title="Éditeur QIF ✨",
    page_icon="💸",
    layout="wide",
)

# -----------------------------
# 🏷️ TITRE
# -----------------------------
st.title("💸 Éditeur de fichiers QIF")
st.subheader("Importe, modifie, nettoie et exporte tes données facilement ✨")

# -----------------------------
# 📥 FONCTIONS QIF
# -----------------------------
def read_qif(file_content):
    lines = file_content.decode("utf-8").splitlines()
    records = []
    current = {}

    for line in lines:
        if line == "^":
            if current:
                records.append(current)
                current = {}
        elif line.startswith("D"):
            current["Date"] = line[1:].strip()
        elif line.startswith("T"):
            current["Amount"] = line[1:].strip()
        elif line.startswith("P"):
            current["Payee"] = line[1:].strip()
        elif line.startswith("M"):
            current["Memo"] = line[1:].strip()
        elif line.startswith("L"):
            current["Category"] = line[1:].strip()

    return pd.DataFrame(records)

def write_qif(df):
    output = "!Type:Bank\n"
    for _, row in df.iterrows():
        if pd.notna(row.get("Date")):
            output += f"D{row['Date']}\n"
        if pd.notna(row.get("Amount")):
            output += f"T{row['Amount']}\n"
        if pd.notna(row.get("Payee")):
            output += f"P{row['Payee']}\n"
        if pd.notna(row.get("Memo")):
            output += f"M{row['Memo']}\n"
        if pd.notna(row.get("Category")):
            output += f"L{row['Category']}\n"
        output += "^\n"
    return output.encode("utf-8")

# -----------------------------
# 🔍 FONCTION DE FILTRAGE AVANCÉ (INSENSIBLE À LA CASSE)
# -----------------------------
def apply_filter(df, column, operator, value):
    series = df[column].astype(str).str.lower()
    value = value.lower()

    if operator == "contient":
        return series.str.contains(value, na=False)

    elif operator == "ne contient pas":
        return ~series.str.contains(value, na=False)

    elif operator == "commence par":
        return series.str.startswith(value, na=False)

    elif operator == "finit par":
        return series.str.endswith(value, na=False)

    elif operator == "est exactement égal":
        return series == value

    elif operator == "pattern * (wildcard)":
        pattern = "^" + re.escape(value).replace("\\*", ".*") + "$"
        return series.str.match(pattern, na=False)

    return pd.Series([False] * len(df))

# -----------------------------
# 📤 UPLOAD
# -----------------------------
uploaded_file = st.file_uploader("📂 Upload un fichier .qif", type=["qif"])

if uploaded_file:
    st.success("🎉 Fichier chargé avec succès !")

    df = read_qif(uploaded_file.read())

    if "df" not in st.session_state:
        st.session_state.df = df

    st.subheader("📝 Tableau éditable")
    edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", key="editor")

    # -----------------------------
    # 🧹 NETTOYAGE AVANCÉ
    # -----------------------------
    with st.container(border=True):
            st.subheader("🧽 Nettoyage des données")

            champ = st.selectbox("🔎 Choisir le champ :", st.session_state.df.columns)

            operateur = st.selectbox(
                "🛠️ Choisir l’opérateur :",
                [
                    "contient",
                    "ne contient pas",
                    "commence par",
                    "finit par",
                    "est exactement égal",
                    # "pattern * (wildcard)"
                ]
            )

            valeur = st.text_input("✏️ Valeur à rechercher", placeholder="ex: sa ou sal*")

            if st.button("🗑️ Supprimer les lignes correspondantes"):
                mask = apply_filter(st.session_state.df, champ, operateur, valeur)
                nb = mask.sum()

                st.session_state.df = st.session_state.df[~mask]
                st.success(f"✨ {nb} ligne(s) supprimée(s) selon '{operateur}'")

                st.rerun()

    # -----------------------------
    # 📥 EXPORT
    # -----------------------------
    qif_bytes = write_qif(st.session_state.df)

    st.download_button(
        label="💾 Télécharger le fichier QIF modifié",
        data=qif_bytes,
        file_name="export.qif",
        mime="application/qif"
    )

else:
    st.info("⬆️ Import un fichier QIF pour commencer")
