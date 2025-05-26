import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
combined_df = pd.read_csv("cleaned_combined_df.csv")

st.title("Bird Observation Analysis Dashboard")

# Sidebar menu
viz_choice = st.sidebar.selectbox("Select Visualization", ["Bird Count by Name", "Count by Admin Unit & Habitat", "Effect of Factors on Bird Count","Observation Share by Observer"])

# === Visualization 1 ===
if viz_choice == "Bird Count by Name":
    st.sidebar.header("Bird Count by Name Filters")
    name_type = st.sidebar.radio("Search by", ['Common Name', 'Scientific Name'])
    col_name = 'Common_Name' if name_type == 'Common Name' else 'Scientific_Name'
    bird_options = combined_df[col_name].unique()
    selected_birds = st.sidebar.multiselect(f"Select {name_type}(s):", options=bird_options)

    habitats = combined_df['Habitat_Type'].unique()
    selected_habitats = st.sidebar.multiselect("Select Habitat(s):", options=habitats)

    df_viz1 = combined_df.copy()

    if selected_birds:
        df_viz1 = df_viz1[df_viz1[col_name].isin(selected_birds)]

    if selected_habitats:
        df_viz1 = df_viz1[df_viz1['Habitat_Type'].isin(selected_habitats)]

    if df_viz1.empty:
        st.warning("No data available for the selected filters.")
    else:
        if selected_habitats:
            count_df = df_viz1.groupby([col_name, 'Habitat_Type']).size().reset_index(name='Count')
            fig = px.bar(count_df, y=col_name, x='Count', color='Habitat_Type', orientation='h',
                         title="Bird Counts by Name and Habitat")
        else:
            count_df = df_viz1.groupby(col_name).size().reset_index(name='Count')
            fig = px.bar(count_df, y=col_name, x='Count', orientation='h',
                         title="Bird Counts by Name (All Habitats)")

        st.plotly_chart(fig, use_container_width=True)

## === Visualization 2 ===
elif viz_choice == "Count by Admin Unit & Habitat":
    st.sidebar.header("Count by Admin Unit & Habitat Filters")
    name_type = st.sidebar.radio("Search by", ['Common Name', 'Scientific Name'])
    col_name = 'Common_Name' if name_type == 'Common Name' else 'Scientific_Name'
    bird_options = combined_df[col_name].unique()
    selected_bird = st.sidebar.selectbox(f"Select {name_type} (Optional):", options=['None'] + list(bird_options))

    admin_units = combined_df['Admin_Unit_Code'].unique()
    selected_admin_units = st.sidebar.multiselect("Select Admin Unit Code(s):", options=['None'] + list(admin_units), default=['None'])

    habitats = combined_df['Habitat_Type'].unique()
    selected_habitats = st.sidebar.multiselect("Select Habitat(s):", options=habitats)

    df_viz2 = combined_df.copy()

    if selected_bird != 'None':
        df_viz2 = df_viz2[df_viz2[col_name] == selected_bird]

    if 'None' not in selected_admin_units:
        df_viz2 = df_viz2[df_viz2['Admin_Unit_Code'].isin(selected_admin_units)]

    if selected_habitats:
        df_viz2 = df_viz2[df_viz2['Habitat_Type'].isin(selected_habitats)]

    if df_viz2.empty:
        st.warning("No data available for the selected filters.")
    else:
        if 'None' in selected_admin_units:
            # No admin unit filter (overall)
            if not selected_habitats:
                # No habitat selected -> total count bar
                total_count = df_viz2.shape[0]
                count_df = pd.DataFrame({'Category': ['Overall Total'], 'Count': [total_count]})
                fig = px.bar(count_df, x='Category', y='Count', title="Overall Bird Counts (All Habitats)")
            elif len(selected_habitats) == 1:
                # Single habitat selected -> single bar total for habitat
                habitat = selected_habitats[0]
                count = df_viz2.shape[0]
                count_df = pd.DataFrame({'Category': [habitat], 'Count': [count]})
                fig = px.bar(count_df, x='Category', y='Count', title=f"Bird Counts for Habitat: {habitat}")
            else:
                # Multiple habitats selected -> stacked bar of habitats
                count_df = df_viz2.groupby('Habitat_Type').size().reset_index(name='Count')
                fig = px.bar(count_df, x='Habitat_Type', y='Count', color='Habitat_Type', title="Bird Counts by Habitat (Stacked)")
        else:
            # Admin unit(s) selected
            if selected_habitats and len(selected_habitats) > 1:
                count_df = df_viz2.groupby(['Admin_Unit_Code', 'Habitat_Type']).size().reset_index(name='Count')
                fig = px.bar(count_df, x='Admin_Unit_Code', y='Count', color='Habitat_Type', barmode='group',
                             title="Bird Counts by Admin Unit and Habitat")
            else:
                count_df = df_viz2.groupby('Admin_Unit_Code').size().reset_index(name='Count')
                fig = px.bar(count_df, x='Admin_Unit_Code', y='Count', title="Bird Counts by Admin Unit")

        st.plotly_chart(fig, use_container_width=True)


# === Visualization 3 ===
elif viz_choice == "Effect of Factors on Bird Count":
    st.sidebar.header("Effect of Factors Filters")
    name_type = st.sidebar.radio("Search by", ['Common Name', 'Scientific Name'])
    col_name = 'Common_Name' if name_type == 'Common Name' else 'Scientific_Name'
    bird_options = combined_df[col_name].unique()
    selected_birds = st.sidebar.multiselect(f"Select {name_type}(s) (Optional):", options=bird_options)

    habitats = combined_df['Habitat_Type'].unique()
    selected_habitats = st.sidebar.multiselect("Select Habitat(s) (Optional):", options=habitats)

    factor = st.sidebar.selectbox("Select Factor to Study:", ['Temperature', 'Humidity', 'Sky', 'Wind'])

    df_viz3 = combined_df.copy()

    if selected_birds:
        df_viz3 = df_viz3[df_viz3[col_name].isin(selected_birds)]

    if selected_habitats:
        df_viz3 = df_viz3[df_viz3['Habitat_Type'].isin(selected_habitats)]

    if df_viz3.empty:
        st.warning("No data available for the selected filters.")
    else:
        # Prepare factor grouping
        if factor == 'Temperature':
            bins = range(10, 45, 5)
            df_viz3['Factor_Group'] = pd.cut(df_viz3['Temperature'], bins=bins, right=False).astype(str)
        elif factor == 'Humidity':
            bins = range(0, 110, 10)
            df_viz3['Factor_Group'] = pd.cut(df_viz3['Humidity'], bins=bins, right=False).astype(str)
        else:
            df_viz3['Factor_Group'] = df_viz3[factor]

        # Plotting logic:
        # If multiple habitats selected, separate lines by Habitat_Type
        # If no habitat selected, show total line only
        if selected_habitats and len(selected_habitats) > 1:
            grouped = df_viz3.groupby(['Factor_Group', 'Habitat_Type']).size().reset_index(name='Count')
            fig = px.line(grouped, x='Factor_Group', y='Count', color='Habitat_Type', markers=True,
                          title=f"Effect of {factor} on Bird Count by Habitat")
        else:
            # If birds selected, color by bird else no color
            if selected_birds:
                grouped = df_viz3.groupby(['Factor_Group', col_name]).size().reset_index(name='Count')
                fig = px.line(grouped, x='Factor_Group', y='Count', color=col_name, markers=True,
                              title=f"Effect of {factor} on Bird Count")
            else:
                grouped = df_viz3.groupby('Factor_Group').size().reset_index(name='Count')
                fig = px.line(grouped, x='Factor_Group', y='Count', markers=True,
                              title=f"Effect of {factor} on Bird Count")

        st.plotly_chart(fig, use_container_width=True)
# === Visualization 4 ===
elif viz_choice == "Observation Share by Observer":
    st.sidebar.header("Filters for Observer Share Pie Chart")

    # Observer Filter
    observer_options = combined_df['Observer'].dropna().unique()
    selected_observers = st.sidebar.multiselect("Select Observer(s):", options=observer_options)

    # Habitat Filter
    habitat_options = combined_df['Habitat_Type'].dropna().unique()
    selected_habitats = st.sidebar.multiselect("Select Habitat Type(s):", options=habitat_options)

    # Admin Unit Filter
    admin_unit_options = combined_df['Admin_Unit_Code'].dropna().unique()
    selected_admin_units = st.sidebar.multiselect("Select Admin Unit Code(s):", options=admin_unit_options)

    # Filter data based on selections
    df_viz4 = combined_df.copy()

    if selected_observers:
        df_viz4 = df_viz4[df_viz4['Observer'].isin(selected_observers)]

    if selected_habitats:
        df_viz4 = df_viz4[df_viz4['Habitat_Type'].isin(selected_habitats)]

    if selected_admin_units:
        df_viz4 = df_viz4[df_viz4['Admin_Unit_Code'].isin(selected_admin_units)]

    if df_viz4.empty:
        st.warning("No data available for the selected filters.")
    else:
        pie_data = df_viz4['Observer'].value_counts().reset_index()
        pie_data.columns = ['Observer', 'Count']
        fig = px.pie(pie_data, names='Observer', values='Count', title="Observation Count Share by Observer")
        st.plotly_chart(fig, use_container_width=True)
