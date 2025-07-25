import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="HR Дашборд", layout="wide")
st.title("📊 HR-дашборд по обучению сотрудников")

uploaded_file = st.file_uploader("⬆️ Загрузите Excel-файл со сводной таблицей", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, skiprows=3)

    # Переименование нужных столбцов
    df = df.rename(columns={
        "Unnamed: 1": "ФИО",
        "Unnamed: 2": "Департамент",
        "Unnamed: 3": "Отдел",
        "Unnamed: 4": "Дата назначения",
        "Unnamed: 5": "Дата окончания",
        "Unnamed: 45": "Средний балл",
        "Unnamed: 46": "Статус обучения",
        "Unnamed: 44": "Посещение МПП"
    })

    # Приведение типов
    df["Дата назначения"] = pd.to_datetime(df["Дата назначения"], errors="coerce")
    df["Дата окончания"] = pd.to_datetime(df["Дата окончания"], errors="coerce")

    # ░░░ БОКОВАЯ ПАНЕЛЬ ░░░
    st.sidebar.header("🔍 Фильтры")
    dep_filter = st.sidebar.multiselect("Выберите департамент", df["Департамент"].dropna().unique())
    div_filter = st.sidebar.multiselect("Выберите отдел", df["Отдел"].dropna().unique())
    status_filter = st.sidebar.multiselect("Статус обучения", df["Статус обучения"].dropna().unique())

    filtered_df = df.copy()
    if dep_filter:
        filtered_df = filtered_df[filtered_df["Департамент"].isin(dep_filter)]
    if div_filter:
        filtered_df = filtered_df[filtered_df["Отдел"].isin(div_filter)]
    if status_filter:
        filtered_df = filtered_df[filtered_df["Статус обучения"].isin(status_filter)]

    st.success("✅ Данные загружены и обработаны")

    # ░░░ СВОДНАЯ СТАТИСТИКА ░░░
    st.header("📌 Общая статистика")
    col1, col2, col3 = st.columns(3)
    col1.metric("👥 Всего сотрудников", len(filtered_df))
    col2.metric("✅ Завершили обучение", filtered_df["Дата окончания"].notna().sum())
    col3.metric("📈 Средний балл", round(filtered_df["Средний балл"].mean(skipna=True), 1))

    # ░░░ КРУГОВАЯ ДИАГРАММА ПО СТАТУСАМ ░░░
    st.header("📊 Распределение по статусам обучения")
    status_counts = filtered_df["Статус обучения"].value_counts().reset_index()
    status_counts.columns = ["Статус", "Количество"]
    fig = px.pie(status_counts, values="Количество", names="Статус", title="Статусы обучения", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

    # ░░░ БАЛЛЫ ПО ОБУЧЕНИЮ ░░░
    st.header("🎯 Распределение средних баллов")
    st.bar_chart(filtered_df["Средний балл"])

    # ░░░ ТАБЛИЦА СОТРУДНИКОВ ░░░
    st.header("📋 Подробности по сотрудникам")
    st.dataframe(filtered_df[["ФИО", "Департамент", "Отдел", "Статус обучения", "Средний балл", "Дата назначения", "Дата окончания"]])

    # ░░░ МПП: ТОЛЬКО ДЛЯ КОММЕРЧЕСКОГО ДЕПАРТАМЕНТА ░░░
    st.header("🏭 Посещение МПП (только коммерческий департамент)")
    df_mpp = filtered_df[filtered_df["Департамент"].str.lower().str.contains("коммерческий", na=False)]

    if not df_mpp.empty:
        total_mpp = df_mpp["Посещение МПП"].notna().sum()
        passed_mpp = df_mpp["Посещение МПП"].str.contains("пройден", case=False, na=False).sum()
        st.metric("🧾 Назначено на МПП", total_mpp)
        st.metric("✅ Завершили МПП", passed_mpp)
        if total_mpp > 0:
            st.metric("📊 Процент завершения", f"{round(passed_mpp / total_mpp * 100, 1)}%")
    else:
        st.info("Нет данных для коммерческого департамента")

    # ░░░ ТЕСТЫ: УСПЕВАЕМОСТЬ ░░░
    st.header("🧪 Статистика по тестам")
    st.write("⚠️ Здесь может быть доработка по количеству попыток — пока рассчитывается по лучшей попытке (средний балл)")

    best = filtered_df["Средний балл"].dropna()
    st.metric("🧠 Прошли с 1 попытки (оценка ≥ 85)", (best >= 85).sum())
    st.metric("📉 Средний балл по всем", round(best.mean(), 1))

    # ░░░ ДИНАМИКА ОБУЧЕНИЯ ░░░
    st.header("📆 Динамика прохождения обучения")
    timeline = filtered_df[filtered_df["Дата окончания"].notna()]
    timeline = timeline.groupby(timeline["Дата окончания"].dt.to_period("M")).size().reset_index(name="Количество")
    timeline["Дата"] = timeline["Дата окончания"].astype(str)

    fig_line = px.line(timeline, x="Дата", y="Количество", markers=True, title="Количество завершённых обучений по месяцам")
    st.plotly_chart(fig_line, use_container_width=True)

    # ░░░ ДАТА ОБНОВЛЕНИЯ ░░░
    st.caption(f"📅 Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

else:
    st.warning("Загрузите Excel-файл для отображения дашборда.")
