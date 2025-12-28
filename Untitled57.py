{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "authorship_tag": "ABX9TyMfdT61X1gRUak9m9dT0eyA",
      "include_colab_link": true
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github",
        "colab_type": "text"
      },
      "source": [
        "<a href=\"https://colab.research.google.com/github/LamaEmran/Data/blob/main/Untitled57.ipynb\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": 1,
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "id": "9yRYe0ixwuyD",
        "outputId": "563d1c93-d9ad-4a1e-c369-57e6704c43b3"
      },
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "⬇️ Downloading wildfire data...\n",
            "📂 Extracting...\n",
            "✅ Found: X_Wildfire.csv\n",
            "📊 Shape: (137334, 57)\n",
            "🧱 Columns: ['date', 'city', 'FIRE_FINAL_SIZE', 'FIRE_WEATHER_INDEX', 'FIRE_START_DATE', 'FIRE_OUT_DATE', 'FIRE_TYPE_CODE', 'FIRE_GENERAL_CAUSE_CODE', 'FIRE_RESPONSE_OBJ_CODE', 'FIRE_YEAR']\n",
            "💾 Saved cleaned data as 'final_dashboard_data.csv'\n"
          ]
        }
      ],
      "source": [
        "import pandas as pd\n",
        "import os\n",
        "import zipfile\n",
        "\n",
        "# 1️⃣ Download the ZIP file from GitHub\n",
        "print(\"⬇️ Downloading wildfire data...\")\n",
        "!wget -O X_Wildfire.zip https://github.com/MajdBa7r/AQI/raw/main/X_Wildfire.zip -q\n",
        "\n",
        "# 2️⃣ Unzip the file\n",
        "print(\"📂 Extracting...\")\n",
        "with zipfile.ZipFile(\"X_Wildfire.zip\", 'r') as zip_ref:\n",
        "    zip_ref.extractall(\".\")\n",
        "\n",
        "# 3️⃣ Identify the CSV inside the ZIP\n",
        "csv_files = [f for f in os.listdir(\".\") if f.endswith(\".csv\")]\n",
        "if not csv_files:\n",
        "    raise FileNotFoundError(\"❌ No CSV file found inside the ZIP!\")\n",
        "\n",
        "csv_file = csv_files[0]\n",
        "print(f\"✅ Found: {csv_file}\")\n",
        "\n",
        "# 4️⃣ Load and inspect\n",
        "df = pd.read_csv(csv_file)\n",
        "print(\"📊 Shape:\", df.shape)\n",
        "print(\"🧱 Columns:\", list(df.columns)[:10])\n",
        "\n",
        "# 5️⃣ Clean and save a consistent version\n",
        "df['date'] = pd.to_datetime(df['date'], errors='coerce')\n",
        "df = df.dropna(subset=['date'])\n",
        "df.to_csv(\"final_dashboard_data.csv\", index=False)\n",
        "print(\"💾 Saved cleaned data as 'final_dashboard_data.csv'\")\n"
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "import streamlit as st\n",
        "import pandas as pd\n",
        "import plotly.express as px\n",
        "import numpy as np\n",
        "\n",
        "# ==========================================\n",
        "# 1. APP CONFIGURATION\n",
        "# ==========================================\n",
        "st.set_page_config(\n",
        "    page_title=\"Ontario Wildfire Intelligence\",\n",
        "    page_icon=\"🔥\",\n",
        "    layout=\"wide\"\n",
        ")\n",
        "\n",
        "# ==========================================\n",
        "# 2. DATA LOADING\n",
        "# ==========================================\n",
        "@st.cache_data\n",
        "def load_data():\n",
        "    try:\n",
        "        df = pd.read_csv(\"final_dashboard_data.csv\")\n",
        "\n",
        "        if 'date' in df.columns:\n",
        "            df['date'] = pd.to_datetime(df['date'], errors='coerce')\n",
        "\n",
        "        for c in ['lat', 'lon', 'pm25', 'temperature', 'wind_speed', 'FIRE_FINAL_SIZE']:\n",
        "            if c in df.columns:\n",
        "                df[c] = pd.to_numeric(df[c], errors='coerce')\n",
        "\n",
        "        return df.dropna(subset=['date'])\n",
        "    except Exception as e:\n",
        "        st.error(f\"Data loading error: {e}\")\n",
        "        return pd.DataFrame()\n",
        "\n",
        "df = load_data()\n",
        "\n",
        "# ==========================================\n",
        "# 3. SIDEBAR FILTERS\n",
        "# ==========================================\n",
        "st.sidebar.header(\"🔍 Filters\")\n",
        "\n",
        "if df.empty:\n",
        "    st.warning(\"No data available\")\n",
        "    st.stop()\n",
        "\n",
        "min_date = df['date'].min().date()\n",
        "max_date = df['date'].max().date()\n",
        "\n",
        "date_range = st.sidebar.date_input(\n",
        "    \"Date Range\",\n",
        "    (min_date, max_date),\n",
        "    min_value=min_date,\n",
        "    max_value=max_date\n",
        ")\n",
        "\n",
        "if 'city' in df.columns:\n",
        "    cities = sorted(df['city'].dropna().unique())\n",
        "    selected_cities = st.sidebar.multiselect(\n",
        "        \"Regions\",\n",
        "        cities,\n",
        "        default=cities[:3] if len(cities) >= 3 else cities\n",
        "    )\n",
        "else:\n",
        "    selected_cities = []\n",
        "\n",
        "mask = (\n",
        "    (df['date'] >= pd.to_datetime(date_range[0])) &\n",
        "    (df['date'] <= pd.to_datetime(date_range[1]))\n",
        ")\n",
        "\n",
        "if selected_cities:\n",
        "    mask &= df['city'].isin(selected_cities)\n",
        "\n",
        "filtered_df = df[mask]\n",
        "\n",
        "fire_days = (\n",
        "    filtered_df[filtered_df['FIRE_FINAL_SIZE'] > 0]\n",
        "    if 'FIRE_FINAL_SIZE' in filtered_df.columns\n",
        "    else pd.DataFrame()\n",
        ")\n",
        "\n",
        "# ==========================================\n",
        "# 4. DASHBOARD\n",
        "# ==========================================\n",
        "st.title(\"🔥 Ontario Wildfire Intelligence Dashboard\")\n",
        "\n",
        "# --- KPIs ---\n",
        "col1, col2, col3, col4 = st.columns(4)\n",
        "\n",
        "with col1:\n",
        "    if 'pm25' in filtered_df.columns:\n",
        "        st.metric(\"Avg PM2.5\", f\"{filtered_df['pm25'].mean():.1f}\")\n",
        "    else:\n",
        "        st.metric(\"Avg PM2.5\", \"N/A\")\n",
        "\n",
        "with col2:\n",
        "    if 'pm25' in filtered_df.columns:\n",
        "        st.metric(\"Peak PM2.5\", f\"{filtered_df['pm25'].max():.1f}\")\n",
        "    else:\n",
        "        st.metric(\"Peak PM2.5\", \"N/A\")\n",
        "\n",
        "with col3:\n",
        "    st.metric(\"Active Fire Days\", len(fire_days))\n",
        "\n",
        "with col4:\n",
        "    if 'temperature' in filtered_df.columns:\n",
        "        st.metric(\"Avg Temp\", f\"{filtered_df['temperature'].mean():.1f} °C\")\n",
        "    else:\n",
        "        st.metric(\"Avg Temp\", \"N/A\")\n",
        "\n",
        "# --- TIME SERIES ---\n",
        "st.subheader(\"📈 PM2.5 Over Time\")\n",
        "\n",
        "if 'pm25' in filtered_df.columns:\n",
        "    daily = filtered_df.groupby('date')['pm25'].mean().reset_index()\n",
        "    fig = px.area(daily, x='date', y='pm25')\n",
        "    st.plotly_chart(fig, use_container_width=True)\n",
        "\n",
        "# --- MAP ---\n",
        "st.subheader(\"🗺️ Pollution Map\")\n",
        "\n",
        "if {'lat', 'lon', 'pm25'}.issubset(filtered_df.columns):\n",
        "    map_df = filtered_df.dropna(subset=['lat', 'lon'])\n",
        "    if not map_df.empty:\n",
        "        fig = px.scatter_mapbox(\n",
        "            map_df,\n",
        "            lat='lat',\n",
        "            lon='lon',\n",
        "            size='pm25',\n",
        "            color='pm25',\n",
        "            zoom=4,\n",
        "            mapbox_style=\"carto-darkmatter\"\n",
        "        )\n",
        "        st.plotly_chart(fig, use_container_width=True)\n",
        "\n",
        "# --- FIRE ANALYSIS ---\n",
        "st.subheader(\"🔥 Fire Size Distribution\")\n",
        "\n",
        "if not fire_days.empty and 'FIRE_GENERAL_CAUSE_CODE' in fire_days.columns:\n",
        "    fig = px.violin(\n",
        "        fire_days,\n",
        "        y='FIRE_FINAL_SIZE',\n",
        "        x='FIRE_GENERAL_CAUSE_CODE',\n",
        "        box=True,\n",
        "        log_y=True\n",
        "    )\n",
        "    st.plotly_chart(fig, use_container_width=True)\n",
        "\n",
        "# --- RAW DATA ---\n",
        "with st.expander(\"🔍 Raw Data\"):\n",
        "    st.dataframe(filtered_df.sort_values('date', ascending=False))\n"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "id": "WDMsBGTOwwNm",
        "outputId": "03b3ed7b-f726-4906-e83b-7f61c0bf9e53"
      },
      "execution_count": 14,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stderr",
          "text": [
            "2025-12-28 07:22:14.327 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:14.329 WARNING streamlit.runtime.caching.cache_data_api: No runtime found, using MemoryCacheStorageManager\n",
            "2025-12-28 07:22:14.332 WARNING streamlit.runtime.caching.cache_data_api: No runtime found, using MemoryCacheStorageManager\n",
            "2025-12-28 07:22:14.333 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:14.508 \n",
            "  \u001b[33m\u001b[1mWarning:\u001b[0m to view this Streamlit app on a browser, run it with the following\n",
            "  command:\n",
            "\n",
            "    streamlit run /usr/local/lib/python3.12/dist-packages/colab_kernel_launcher.py [ARGUMENTS]\n",
            "2025-12-28 07:22:14.509 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:14.510 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:14.511 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:15.013 Thread 'Thread-3': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:15.014 Thread 'Thread-3': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:15.015 Thread 'Thread-3': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.202 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.203 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.204 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.208 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.210 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.213 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.217 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.218 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.219 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.221 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.223 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.224 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.229 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.230 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.231 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.233 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.235 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.236 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.248 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.249 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.250 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.251 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.252 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.253 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.255 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.256 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.258 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.259 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.260 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.262 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.264 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.265 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.268 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.269 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.271 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.273 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.274 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.275 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.276 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.278 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.281 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.384 Please replace `use_container_width` with `width`.\n",
            "\n",
            "`use_container_width` will be removed after 2025-12-31.\n",
            "\n",
            "For `use_container_width=True`, use `width='stretch'`. For `use_container_width=False`, use `width='content'`.\n",
            "2025-12-28 07:22:16.404 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.405 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.406 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.407 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.409 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.410 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.411 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.412 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.464 Please replace `use_container_width` with `width`.\n",
            "\n",
            "`use_container_width` will be removed after 2025-12-31.\n",
            "\n",
            "For `use_container_width=True`, use `width='stretch'`. For `use_container_width=False`, use `width='content'`.\n",
            "2025-12-28 07:22:16.472 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.473 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.475 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.477 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.479 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.480 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.481 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.482 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.516 Please replace `use_container_width` with `width`.\n",
            "\n",
            "`use_container_width` will be removed after 2025-12-31.\n",
            "\n",
            "For `use_container_width=True`, use `width='stretch'`. For `use_container_width=False`, use `width='content'`.\n",
            "2025-12-28 07:22:16.518 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.520 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.521 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.522 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.524 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.525 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.599 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.599 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-12-28 07:22:16.602 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n"
          ]
        }
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "!pip install streamlit -q"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "id": "f_tpLHVCw_Iw",
        "outputId": "5a491d6f-088a-4925-bc47-6820461f8959"
      },
      "execution_count": 4,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "\u001b[2K   \u001b[90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\u001b[0m \u001b[32m9.0/9.0 MB\u001b[0m \u001b[31m65.0 MB/s\u001b[0m eta \u001b[36m0:00:00\u001b[0m\n",
            "\u001b[2K   \u001b[90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\u001b[0m \u001b[32m6.9/6.9 MB\u001b[0m \u001b[31m116.7 MB/s\u001b[0m eta \u001b[36m0:00:00\u001b[0m\n",
            "\u001b[?25h"
          ]
        }
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "!pip install -q streamlit joblib plotly pandas\n",
        "!npm install -g localtunnel"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "id": "y2AOla0lxHpp",
        "outputId": "8f1ca6a9-bb41-4229-9259-2a51554f730a"
      },
      "execution_count": 5,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "\u001b[1G\u001b[0K⠙\u001b[1G\u001b[0K⠹\u001b[1G\u001b[0K⠸\u001b[1G\u001b[0K⠼\u001b[1G\u001b[0K⠴\u001b[1G\u001b[0K⠦\u001b[1G\u001b[0K⠧\u001b[1G\u001b[0K⠇\u001b[1G\u001b[0K⠏\u001b[1G\u001b[0K⠋\u001b[1G\u001b[0K⠙\u001b[1G\u001b[0K⠹\u001b[1G\u001b[0K⠸\u001b[1G\u001b[0K⠼\u001b[1G\u001b[0K⠴\u001b[1G\u001b[0K⠦\u001b[1G\u001b[0K⠧\u001b[1G\u001b[0K⠇\u001b[1G\u001b[0K⠏\u001b[1G\u001b[0K⠋\u001b[1G\u001b[0K⠙\u001b[1G\u001b[0K⠹\u001b[1G\u001b[0K\n",
            "added 22 packages in 2s\n",
            "\u001b[1G\u001b[0K⠹\u001b[1G\u001b[0K\n",
            "\u001b[1G\u001b[0K⠹\u001b[1G\u001b[0K3 packages are looking for funding\n",
            "\u001b[1G\u001b[0K⠹\u001b[1G\u001b[0K  run `npm fund` for details\n",
            "\u001b[1G\u001b[0K⠹\u001b[1G\u001b[0K"
          ]
        }
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "# 1. Install pyngrok\n",
        "!pip install -q pyngrok streamlit plotly pandas\n",
        "\n",
        "# 2. Authenticate (REPLACE 'YOUR_TOKEN_HERE' WITH YOUR ACTUAL TOKEN)\n",
        "from pyngrok import ngrok\n",
        "ngrok.set_auth_token(\"YOUR_TOKEN_HERE\")\n",
        "\n",
        "# 3. Kill any old tunnels to prevent errors\n",
        "ngrok.kill()\n",
        "\n",
        "# 4. Start the tunnel\n",
        "public_url = ngrok.connect(8501)\n",
        "print(f\"🚀 Dashboard is live at: {public_url}\")\n",
        "\n",
        "# 5. Run the app\n",
        "!streamlit run app.py"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/",
          "height": 532
        },
        "id": "GP9iHZk00TOv",
        "outputId": "4e4cd0d8-059b-4e10-a948-f762db0653a6"
      },
      "execution_count": 12,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": []
        },
        {
          "output_type": "stream",
          "name": "stderr",
          "text": [
            "ERROR:pyngrok.process.ngrok:t=2025-12-28T07:17:05+0000 lvl=eror msg=\"failed to reconnect session\" obj=tunnels.session err=\"authentication failed: The authtoken you specified does not look like a proper ngrok authtoken.\\nYour authtoken: YOUR_TOKEN_HERE\\nInstructions to install your authtoken are on your ngrok dashboard:\\nhttps://dashboard.ngrok.com/get-started/your-authtoken\\r\\n\\r\\nERR_NGROK_105\\r\\n\"\n",
            "ERROR:pyngrok.process.ngrok:t=2025-12-28T07:17:05+0000 lvl=eror msg=\"session closing\" obj=tunnels.session err=\"authentication failed: The authtoken you specified does not look like a proper ngrok authtoken.\\nYour authtoken: YOUR_TOKEN_HERE\\nInstructions to install your authtoken are on your ngrok dashboard:\\nhttps://dashboard.ngrok.com/get-started/your-authtoken\\r\\n\\r\\nERR_NGROK_105\\r\\n\"\n",
            "ERROR:pyngrok.process.ngrok:t=2025-12-28T07:17:05+0000 lvl=eror msg=\"terminating with error\" obj=app err=\"authentication failed: The authtoken you specified does not look like a proper ngrok authtoken.\\nYour authtoken: YOUR_TOKEN_HERE\\nInstructions to install your authtoken are on your ngrok dashboard:\\nhttps://dashboard.ngrok.com/get-started/your-authtoken\\r\\n\\r\\nERR_NGROK_105\\r\\n\"\n"
          ]
        },
        {
          "output_type": "error",
          "ename": "PyngrokNgrokError",
          "evalue": "The ngrok process errored on start: authentication failed: The authtoken you specified does not look like a proper ngrok authtoken.\\nYour authtoken: YOUR_TOKEN_HERE\\nInstructions to install your authtoken are on your ngrok dashboard:\\nhttps://dashboard.ngrok.com/get-started/your-authtoken\\r\\n\\r\\nERR_NGROK_105\\r\\n.",
          "traceback": [
            "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
            "\u001b[0;31mPyngrokNgrokError\u001b[0m                         Traceback (most recent call last)",
            "\u001b[0;32m/tmp/ipython-input-2421634464.py\u001b[0m in \u001b[0;36m<cell line: 0>\u001b[0;34m()\u001b[0m\n\u001b[1;32m     10\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m     11\u001b[0m \u001b[0;31m# 4. Start the tunnel\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m---> 12\u001b[0;31m \u001b[0mpublic_url\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mngrok\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mconnect\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0;36m8501\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m     13\u001b[0m \u001b[0mprint\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0;34mf\"🚀 Dashboard is live at: {public_url}\"\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m     14\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n",
            "\u001b[0;32m/usr/local/lib/python3.12/dist-packages/pyngrok/ngrok.py\u001b[0m in \u001b[0;36mconnect\u001b[0;34m(addr, proto, name, pyngrok_config, **options)\u001b[0m\n\u001b[1;32m    333\u001b[0m     \u001b[0mlogger\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0minfo\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0;34mf\"Opening tunnel named: {name}\"\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    334\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m--> 335\u001b[0;31m     \u001b[0mapi_url\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mget_ngrok_process\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mpyngrok_config\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mapi_url\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m    336\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    337\u001b[0m     \u001b[0mlogger\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mdebug\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0;34mf\"Creating tunnel with options: {options}\"\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n",
            "\u001b[0;32m/usr/local/lib/python3.12/dist-packages/pyngrok/ngrok.py\u001b[0m in \u001b[0;36mget_ngrok_process\u001b[0;34m(pyngrok_config)\u001b[0m\n\u001b[1;32m    200\u001b[0m     \u001b[0minstall_ngrok\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mpyngrok_config\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    201\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m--> 202\u001b[0;31m     \u001b[0;32mreturn\u001b[0m \u001b[0mprocess\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mget_process\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mpyngrok_config\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m    203\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    204\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n",
            "\u001b[0;32m/usr/local/lib/python3.12/dist-packages/pyngrok/process.py\u001b[0m in \u001b[0;36mget_process\u001b[0;34m(pyngrok_config)\u001b[0m\n\u001b[1;32m    269\u001b[0m         \u001b[0;32mreturn\u001b[0m \u001b[0m_current_processes\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0mpyngrok_config\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mngrok_path\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    270\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m--> 271\u001b[0;31m     \u001b[0;32mreturn\u001b[0m \u001b[0m_start_process\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mpyngrok_config\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m    272\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    273\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n",
            "\u001b[0;32m/usr/local/lib/python3.12/dist-packages/pyngrok/process.py\u001b[0m in \u001b[0;36m_start_process\u001b[0;34m(pyngrok_config)\u001b[0m\n\u001b[1;32m    445\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    446\u001b[0m         \u001b[0;32mif\u001b[0m \u001b[0mngrok_process\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mstartup_error\u001b[0m \u001b[0;32mis\u001b[0m \u001b[0;32mnot\u001b[0m \u001b[0;32mNone\u001b[0m\u001b[0;34m:\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m--> 447\u001b[0;31m             raise PyngrokNgrokError(f\"The ngrok process errored on start: {ngrok_process.startup_error}.\",\n\u001b[0m\u001b[1;32m    448\u001b[0m                                     \u001b[0mngrok_process\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mlogs\u001b[0m\u001b[0;34m,\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    449\u001b[0m                                     ngrok_process.startup_error)\n",
            "\u001b[0;31mPyngrokNgrokError\u001b[0m: The ngrok process errored on start: authentication failed: The authtoken you specified does not look like a proper ngrok authtoken.\\nYour authtoken: YOUR_TOKEN_HERE\\nInstructions to install your authtoken are on your ngrok dashboard:\\nhttps://dashboard.ngrok.com/get-started/your-authtoken\\r\\n\\r\\nERR_NGROK_105\\r\\n."
          ]
        }
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "!streamlit run app.py & npx localtunnel --port 8501\n"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "id": "DNeGvqXuw44o",
        "outputId": "80a277f7-32ad-4636-f3c2-d82336c46c18"
      },
      "execution_count": null,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "\u001b[1G\u001b[0K⠙\n",
            "Collecting usage statistics. To deactivate, set browser.gatherUsageStats to false.\n",
            "\u001b[0m\n",
            "\u001b[1G\u001b[0K⠹\u001b[1G\u001b[0K⠸\u001b[1G\u001b[0K⠼\u001b[1G\u001b[0K⠴\u001b[1G\u001b[0K⠦\u001b[1G\u001b[0K⠧\u001b[1G\u001b[0K⠇\u001b[1G\u001b[0K⠏\u001b[1G\u001b[0K⠋\u001b[1G\u001b[0K⠙\u001b[1G\u001b[0K⠹\u001b[1G\u001b[0K⠸\u001b[1G\u001b[0K⠼\u001b[1G\u001b[0K⠴\u001b[1G\u001b[0K⠦\u001b[1G\u001b[0K⠧\u001b[1G\u001b[0K⠇\u001b[1G\u001b[0K⠏\u001b[1G\u001b[0K⠋\u001b[1G\u001b[0K⠙\u001b[1G\u001b[0K⠹\u001b[1G\u001b[0K⠸\u001b[1G\u001b[0K\u001b[0m\n",
            "\u001b[34m\u001b[1m  You can now view your Streamlit app in your browser.\u001b[0m\n",
            "\u001b[0m\n",
            "\u001b[34m  Local URL: \u001b[0m\u001b[1mhttp://localhost:8501\u001b[0m\n",
            "\u001b[34m  Network URL: \u001b[0m\u001b[1mhttp://172.28.0.12:8501\u001b[0m\n",
            "\u001b[34m  External URL: \u001b[0m\u001b[1mhttp://35.229.139.57:8501\u001b[0m\n",
            "\u001b[0m\n",
            "your url is: https://loud-adults-see.loca.lt\n",
            "2025-12-28 07:23:01.586 Please replace `use_container_width` with `width`.\n",
            "\n",
            "`use_container_width` will be removed after 2025-12-31.\n",
            "\n",
            "For `use_container_width=True`, use `width='stretch'`. For `use_container_width=False`, use `width='content'`.\n",
            "2025-12-28 07:23:01.655 Please replace `use_container_width` with `width`.\n",
            "\n",
            "`use_container_width` will be removed after 2025-12-31.\n",
            "\n",
            "For `use_container_width=True`, use `width='stretch'`. For `use_container_width=False`, use `width='content'`.\n",
            "2025-12-28 07:23:01.712 Please replace `use_container_width` with `width`.\n",
            "\n",
            "`use_container_width` will be removed after 2025-12-31.\n",
            "\n",
            "For `use_container_width=True`, use `width='stretch'`. For `use_container_width=False`, use `width='content'`.\n",
            "2025-12-28 07:23:01.719 Please replace `use_container_width` with `width`.\n",
            "\n",
            "`use_container_width` will be removed after 2025-12-31.\n",
            "\n",
            "For `use_container_width=True`, use `width='stretch'`. For `use_container_width=False`, use `width='content'`.\n"
          ]
        }
      ]
    },
    {
      "cell_type": "code",
      "source": [],
      "metadata": {
        "id": "Wtt3UjvKw9qy"
      },
      "execution_count": null,
      "outputs": []
    }
  ]
}
