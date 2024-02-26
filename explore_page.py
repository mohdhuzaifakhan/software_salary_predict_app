import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def shorten_categories(categories, cutoff):
    categorical_map = {}
    for i in range(len(categories)):
        if categories.values[i] >= cutoff:
            categorical_map[categories.index[i]] = categories.index[i]
        else:
            categorical_map[categories.index[i]] = 'Other'
    return categorical_map


def clean_experience(x):
    if x ==  'More than 50 years':
        return 50
    if x == 'Less than 1 year':
        return 0.5
    return float(x)


def clean_education(x):
    if 'Bachelor’s degree' in x:
        return 'Bachelor’s degree'
    if 'Master’s degree' in x:
        return 'Master’s degree'
    if 'Professional degree' in x or 'Other doctoral' in x:
        return 'Post grad'
    return 'Less than a Bachelors'


@st.cache_data
def load_data():
    df = pd.read_csv("survey_results_public.csv")
    df = df[["Country", "EdLevel", "YearsCodePro", "Employment", "ConvertedCompYearly"]]
    df = df[df["ConvertedCompYearly"].notnull()]
    df = df.dropna()
    df = df[df["Employment"] == "Employed, full-time"]
    df = df.drop("Employment", axis=1)

    country_map = shorten_categories(df.Country.value_counts(), 400)
    df["Country"] = df["Country"].map(country_map)
    df = df[df["ConvertedCompYearly"] <= 250000]
    df = df[df["ConvertedCompYearly"] >= 10000]
    df = df[df["Country"] != "Other"]

    df["YearsCodePro"] = df["YearsCodePro"].apply(clean_experience)
    df["EdLevel"] = df["EdLevel"].apply(clean_education)
    df = df.rename({"ConvertedCompYearly": "Salary"}, axis=1)
    return df

df = load_data()

def show_explore_page():
    st.title("Explore Software Engineer Salaries")

    st.write(
        """
    ### Stack Overflow Developer Survey 2023
    """
    )

    data = df["Country"].value_counts()

    # Get the top 5 countries and their counts
    top_countries = data.head(5)

    # Get the count of other countries
    other_countries_count = data.shape[0] - top_countries.shape[0]

    # Create a figure and axes for the pie charts
    fig, ax = plt.subplots(figsize=(12, 8))  # Adjust the figure size as desired

    # Plot the outer pie chart for top 5 countries
    outer_wedges, outer_texts, outer_autotexts = ax.pie(top_countries, labels=top_countries.index, autopct="%1.1f%%", pctdistance=0.85,
                                                        wedgeprops=dict(width=0.3, edgecolor='w'), startangle=90)

    # Plot the inner pie chart for "Other" category
    inner_wedges, inner_texts, inner_autotexts = ax.pie([other_countries_count], labels=["Other"], autopct="%1.1f%%", pctdistance=0.75,
                                                        radius=0.6, wedgeprops=dict(width=0.4, edgecolor='w'), startangle=90)

    # Customize the appearance of the pie charts
    plt.setp(inner_autotexts, size=10, weight="bold", color="white")  # Increase font size and make text bold and white
    plt.setp(outer_autotexts, size=12, weight="bold", color="white")  # Increase font size and make text bold and white
    ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle

    # Set title for the pie chart
    ax.set_title("Nested Pie Chart of Data from Different Countries", fontsize=16, fontweight="bold")

    # Show the pie chart using Streamlit
    st.pyplot(fig)

    st.write(
        """
    #### Mean Salary Based On Country
    """
    )

    data = df.groupby(["Country"])["Salary"].mean().sort_values(ascending=True)
    st.bar_chart(data)

    st.write(
        """
    #### Mean Salary Based On Experience
    """
    )

    data = df.groupby(["YearsCodePro"])["Salary"].mean().sort_values(ascending=True)
    st.line_chart(data)
