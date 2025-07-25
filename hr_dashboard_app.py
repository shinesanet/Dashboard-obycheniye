
import streamlit as st
import pandas as pd

st.set_page_config(page_title="HR-дэшборд обучения", layout="wide")

st.title("📊 HR-дэшборд по обучению сотрудников")

# Загрузка Excel-файла
uploaded_file = st.file_uploader("Загрузите Excel-файл", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name=0, skiprows=3)

    # Удаление строк с отсутствующими ФИО
    df = df[df[df.columns[1]].notna()]

    st.subheader("Фильтры")
    col1, col2 = st.columns(2)

    with col1:
        dep_filter = st.multiselect("Выберите департамент", options=df[df.columns[3]].unique())
    with col2:
        status_filter = st.multiselect("Выберите статус прохождения", options=df[df.columns[-2]].unique())

    filtered_df = df.copy()
    if dep_filter:
        filtered_df = filtered_df[filtered_df[filtered_df.columns[3]].isin(dep_filter)]
    if status_filter:
        filtered_df = filtered_df[filtered_df[filtered_df.columns[-2]].isin(status_filter)]

    st.subheader("Общая таблица")
    st.dataframe(filtered_df, use_container_width=True)

    st.subheader("Итоги обучения")
    assigned = filtered_df[filtered_df[df.columns[6]].notna()]
    completed = filtered_df[filtered_df[df.columns[7]].notna()]
    col3, col4, col5 = st.columns(3)
    col3.metric("Назначено обучение", len(assigned))
    col4.metric("Завершили обучение", len(completed))
    try:
        avg_score = filtered_df["Среднее значение"].dropna().astype(float).mean()
        col5.metric("Средний балл", f"{avg_score:.1f}")
    except:
        col5.metric("Средний балл", "Нет данных")

    st.markdown("---")
    st.caption("Все расчёты выполняются по последним успешным попыткам. Модули с «–» не учитываются.")
