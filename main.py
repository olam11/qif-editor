import streamlit as st
import pandas as pd

# -----------------------------
# 🎨 STYLE GLOBAL
# -----------------------------
st.set_page_config(
    page_title="Éditeur QIF ✨",
    page_icon="💸",
    layout="centered"
)

# CSS personnalisé
# st.markdown("""
# <style>
#     .main {
#         background-color: #f7f9fc;
#     }
#     .stButton>button {
#         background-color: #4CAF50 !important;
#         color: white !important;
#         border-radius: 8px !important;
#         padding: 0.6rem 1.2rem !important;
#         font-size: 1rem !important;
#     }
#     .stDownloadButton>button {
#         background-color: #0066cc !important;
#         color: white !important;
#         border-radius: 8px !important;
#         padding: 0.6rem 1.2rem !important;
#         font-size: 1rem !important;
#     }
#     .title {
#         text-align: center;
#         font-size: 2.4rem;
#         color: #333;
#         margin-bottom: 1rem;
#     }
#     .subtitle {
#         text-align: center;
#         font-size: 1.3rem;
#         color: #555;
#         margin-bottom: 2rem;
#     }
# </style>
# """, unsafe_allow_html=True)

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
            current["Date"] = line[1:]
        elif line.startswith("T"):
            current["Amount"] = line[1:]
        elif line.startswith("P"):
            current["Payee"] = line[1:]
        elif line.startswith("M"):
            current["Memo"] = line[1:]
        elif line.startswith("L"):
            current["Category"] = line[1:]

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
    # 🧹 SUPPRESSION DES LIGNES
    # -----------------------------
    st.subheader("🧽 Nettoyage des données")

    champ = st.selectbox("🔎 Choisir le champ :", st.session_state.df.columns)
    valeur = st.text_input("✏️ Texte à rechercher (insensible à la casse)", placeholder="ex: author")

    if st.button("🗑️ Supprimer les lignes correspondantes"):
        mask = st.session_state.df[champ].astype(str).str.contains(valeur, case=False, na=False)
        nb = mask.sum()

        st.session_state.df = st.session_state.df[~mask]
        st.success(f"✨ {nb} ligne(s) supprimée(s) contenant '{valeur}' dans '{champ}'")

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
