
import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv("combined_df.csv")

# Preprocessing
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Month"] = df["Date"].dt.month
df["Year"] = df["Date"].dt.year
df["Start_Hour"] = pd.to_datetime(df["Start_Time"], errors="coerce").dt.hour

st.set_page_config(layout="wide")
st.title("Bird Species EDA Dashboard")

# Sidebar Filters
st.sidebar.title("Filters")
habitat = st.sidebar.multiselect("Habitat Type", df["Habitat_Type"].unique(), default=df["Habitat_Type"].unique())
year = st.sidebar.multiselect("Year", sorted(df["Year"].unique()), default=sorted(df["Year"].unique()))
month = st.sidebar.multiselect("Month", sorted(df["Month"].dropna().unique()), default=sorted(df["Month"].dropna().unique()))
observer = st.sidebar.multiselect("Observer", df["Observer"].unique())
species = st.sidebar.multiselect("Species (Common Name)", df["Common_Name"].unique())
admin_unit = st.sidebar.multiselect("Admin Unit", df["Admin_Unit_Code"].unique())
visit = st.sidebar.multiselect("Visit Number", sorted(df["Visit"].unique()))

# Apply filters
filtered_df = df[
    (df["Habitat_Type"].isin(habitat)) &
    (df["Year"].isin(year)) &
    (df["Month"].isin(month))
]

if observer:
    filtered_df = filtered_df[filtered_df["Observer"].isin(observer)]
if species:
    filtered_df = filtered_df[filtered_df["Common_Name"].isin(species)]
if admin_unit:
    filtered_df = filtered_df[filtered_df["Admin_Unit_Code"].isin(admin_unit)]
if visit:
    filtered_df = filtered_df[filtered_df["Visit"].isin(visit)]

# 1. Species Richness by Habitat
st.subheader("Species Richness by Habitat")
species_richness = filtered_df.groupby("Habitat_Type")["Common_Name"].nunique().reset_index()
fig1 = px.bar(species_richness, x="Habitat_Type", y="Common_Name", labels={"Common_Name": "Unique Species"})
st.plotly_chart(fig1, use_container_width=True)

# 2. Top Observed Species
st.subheader("Top 10 Observed Species")
top_species = filtered_df["Common_Name"].value_counts().nlargest(10).reset_index()
top_species.columns = ["Common_Name", "Observations"]
fig2 = px.bar(top_species, x="Observations", y="Common_Name", orientation='h')
st.plotly_chart(fig2, use_container_width=True)

# 3. Temperature Bin by Habitat
st.subheader("Temperature Bin vs Observations by Habitat")
temp_bin = filtered_df.groupby(["Temp_Bin", "Habitat_Type"]).size().reset_index(name="Count")
fig3 = px.bar(temp_bin, x="Temp_Bin", y="Count", color="Habitat_Type", barmode="group")
st.plotly_chart(fig3, use_container_width=True)

# 4. Humidity Bin by Habitat
st.subheader("Humidity Bin vs Observations by Habitat")
humidity_bin = filtered_df.groupby(["Humidity_Bin", "Habitat_Type"]).size().reset_index(name="Count")
fig4 = px.bar(humidity_bin, x="Humidity_Bin", y="Count", color="Habitat_Type", barmode="group")
st.plotly_chart(fig4, use_container_width=True)

# 5. Seasonal Observation Counts
st.subheader("Seasonal Observation Counts")
filtered_df["Season"] = filtered_df["Month"].map({12: "Winter", 1: "Winter", 2: "Winter",
                                                  3: "Spring", 4: "Spring", 5: "Spring",
                                                  6: "Summer", 7: "Summer", 8: "Summer",
                                                  9: "Fall", 10: "Fall", 11: "Fall"})
seasonal_counts = filtered_df.groupby(["Season", "Habitat_Type"]).size().reset_index(name="Observation_Count")
fig5 = px.bar(seasonal_counts, x="Season", y="Observation_Count", color="Habitat_Type", barmode="group")
st.plotly_chart(fig5, use_container_width=True)

# 6. Flyover Observed Species
st.subheader("Flyover Species")
flyover_species = filtered_df[filtered_df["Flyover_Observed"] == 1]["Common_Name"].value_counts().nlargest(10).reset_index()
flyover_species.columns = ["Common_Name", "Flyover_Count"]
fig6 = px.bar(flyover_species, x="Flyover_Count", y="Common_Name", orientation='h')
st.plotly_chart(fig6, use_container_width=True)

# 7. Sky Conditions
st.subheader("Observations by Sky Condition")
sky_counts = filtered_df["Sky"].value_counts().reset_index()
sky_counts.columns = ["Sky_Condition", "Observation_Count"]
fig7 = px.bar(sky_counts, x="Observation_Count", y="Sky_Condition", orientation='h')
st.plotly_chart(fig7, use_container_width=True)

# 8. Wind Conditions
st.subheader("Observations by Wind Condition")
wind_counts = filtered_df["Wind"].value_counts().reset_index()
wind_counts.columns = ["Wind_Condition", "Observation_Count"]
fig8 = px.bar(wind_counts, x="Observation_Count", y="Wind_Condition", orientation='h')
st.plotly_chart(fig8, use_container_width=True)

# 9. Disturbance Effect
st.subheader("Observation Count by Disturbance Type")
disturbance_counts = filtered_df["Disturbance"].value_counts().reset_index()
disturbance_counts.columns = ["Disturbance_Type", "Observation_Count"]
fig9 = px.bar(disturbance_counts, x="Observation_Count", y="Disturbance_Type", orientation='h')
st.plotly_chart(fig9, use_container_width=True)

# 10. Species by Admin Unit and Habitat
st.subheader("Species Count by Admin Unit & Habitat")
species_by_unit = filtered_df.groupby(["Admin_Unit_Code", "Habitat_Type"])["Scientific_Name"].nunique().reset_index(name="Unique_Species_Count")
fig10 = px.bar(species_by_unit, x="Admin_Unit_Code", y="Unique_Species_Count", color="Habitat_Type", barmode="group")
st.plotly_chart(fig10, use_container_width=True)

# 11. Species per Visit
st.subheader("Average Species Count per Visit")
visit_species = filtered_df.groupby("Visit")["Scientific_Name"].nunique().reset_index(name="Avg_Species_Per_Visit")
fig11 = px.line(visit_species, x="Visit", y="Avg_Species_Per_Visit", markers=True)
st.plotly_chart(fig11, use_container_width=True)
