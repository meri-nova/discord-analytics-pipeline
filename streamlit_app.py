import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
@st.cache_data
def load_data():
    data = pd.read_csv('data/cleaned_users.csv')
    data['joined_at'] = pd.to_datetime(data['joined_at'])
    return data

data = load_data()

# Sidebar for setup
granularity = st.sidebar.selectbox("Select Time Granularity:", ['Daily', 'Weekly', 'Monthly'])
date_range = st.sidebar.date_input("Select Date Range", [])

# Filter data based on selections
if date_range:
    filtered_data = data[(data['joined_at'] >= date_range[0]) & (data['joined_at'] <= date_range[1])]
else:
    filtered_data = data

# Resample data
if granularity == 'Daily':
    resampled_data = filtered_data.resample('D', on='joined_at').size()
elif granularity == 'Weekly':
    resampled_data = filtered_data.resample('W', on='joined_at').size()
else:
    resampled_data = filtered_data.resample('M', on='joined_at').size()


# Convert to DataFrame for Plotly
resampled_data_df = pd.DataFrame({
    'Date': resampled_data.index,
    'Count': resampled_data.values
})

# Create a Plotly express line chart
fig = px.line(resampled_data_df, x='Date', y='Count', title='User Growth Over Time',
              labels={'Count': 'Number of Users'}, markers=True)

# Improving tooltips
fig.update_traces(mode='lines+markers', hoverinfo='all')

# Show plot in Streamlit
st.plotly_chart(fig, use_container_width=True)

continent_counts = data['Continent'].value_counts().reset_index()
continent_counts.columns = ['Continent', 'Users']

# Create a bar chart
fig = px.bar(
    continent_counts,
    x='Continent',
    y='Users',
    title='User Distribution by Continent',
    color='Users',
    labels={'Users':'Number of Users'},
    color_continuous_scale=px.colors.sequential.Viridis
)

st.plotly_chart(fig)

#create 2 columns
col1, col2 = st.columns(2)

with col1:
    top_join_dates = data['joined_at'].dt.date.value_counts().head(7)
    st.write("Top 5 dates with the most user joins:", top_join_dates)

with col2:
    # Assuming 'data' is your DataFrame and 'joined_at' is already a datetime column
    data['day_of_week'] = data['joined_at'].dt.day_name()

    # Count the total number of users joining on each day of the week
    weekly_counts = data['day_of_week'].value_counts()

    # Count the number of unique weeks in the dataset to calculate the average
    num_weeks = data['joined_at'].dt.to_period('W').nunique()

    # Calculate the average number of joins per day of the week
    average_joins_per_day = weekly_counts / num_weeks

    # Display the average joins per day of the week in Streamlit
    st.write("Average user joins by day of the week:", average_joins_per_day)

