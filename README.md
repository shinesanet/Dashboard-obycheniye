import streamlit as st 
import pandas as pd
import numpy as np
import plotly.express as px

# Настройки страницы
st.set_page_config(page_title="HR Дашборд", layout="wide")

st.title("📊 HR Дашборд по обучению сотрудников")

# Загрузка Excel-файла
uploaded_file = st.file_uploader("Загрузите файл Excel со сводом", type=["xlsx"])

if uploaded_file:
    # Чтение данных
    df = pd.read_excel(uploaded_file, sheet_name=0)

    # Очистка и базовая обработка
    df.columns = df.columns.str.strip()
    df = df.rename(columns={
        "FIO": "Сотрудник",
        "Отдел": "Отдел",
        "Департамент": "Департамент",
        "Статус прохождения обучения": "Статус",
        "Средний балл": "Баллы"
    })

    df["Дата окончания обучения"] = pd.to_datetime(df["Дата окончания обучения"], errors='coerce')

    # Фильтры
    with st.sidebar:
        st.header("🔎 Фильтры")
        dep_filter = st.multiselect("Выберите департамент", options=df["Департамент"].dropna().unique())
        div_filter = st.multiselect("Выберите отдел", options=df["Отдел"].dropna().unique())
        status_filter = st.multiselect("Статус обучения", options=df["Статус"].dropna().unique())

    filtered_df = df.copy()

    if dep_filter:
        filtered_df = filtered_df[filtered_df["Департамент"].isin(dep_filter)]
    if div_filter:
        filtered_df = filtered_df[filtered_df["Отдел"].isin(div_filter)]
    if status_filter:
        filtered_df = filtered_df[filtered_df["Статус"].isin(status_filter)]

    # Блок: Общая сводка
    st.subheader("📌 Общая сводка по сотрудникам")
    st.dataframe(filtered_df.style.highlight_null(null_color='red'))

    # Блок: Диаграмма по статусам
    st.subheader("📈 Распределение по статусам обучения")
    status_counts = filtered_df["Статус"].value_counts().reset_index()
    status_counts.columns = ["Статус", "Количество"]

    fig1 = px.pie(status_counts, names="Статус", values="Количество", title="Статусы обучения")
    st.plotly_chart(fig1, use_container_width=True)

    # Блок: Статистика по обучению
    st.subheader("📋 Статистика по баллам обучения")
    col1, col2, col3 = st.columns(3)
    col1.metric("Всего сотрудников", len(filtered_df))
    col2.metric("Прошли обучение", filtered_df["Дата окончания обучения"].notna().sum())
    col3.metric("Средний балл", round(filtered_df["Баллы"].mean(), 1))

    # Блок: Гистограмма баллов
    st.subheader("📊 Распределение баллов")
    fig2 = px.histogram(filtered_df, x="Баллы", nbins=20, title="Гистограмма средних баллов")
    st.plotly_chart(fig2, use_container_width=True)

    # Блок: Обновление отчета
    st.caption(f"🗓️ Дата обновления отчёта: {pd.to_datetime('today').strftime('%d.%m.%Y')}")

else:
    st.info("⬆️ Загрузите файл Excel для отображения дашборда")
