import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# Load data
@st.cache_data
def load_data(path):
    data = pd.read_csv(path)
    date_cols = [col for col in data.columns if col.endswith('_at')]
    for col in date_cols:
        data[col] = pd.to_datetime(data[col])
    return data

user_data = load_data('data/cleaned_users.csv')
messages_data = load_data('data/cleaned_messages.csv')

# Sidebar for setup
granularity = st.sidebar.selectbox("Select Time Granularity:", ['Daily', 'Weekly', 'Monthly'])
# date_range = st.sidebar.date_input("Select Date Range", [])

# # Filter data based on selections
# if date_range:
#     filtered_data = data[(data['joined_at'] >= date_range[0]) & (data['joined_at'] <= date_range[1])]
# else:
#     filtered_data = data
filtered_data = user_data

# Resample data
if granularity == 'Daily':
    resampled_data = filtered_data.resample('D', on='joined_at').size()
    resampled_data1 = resampled_data[:-1]
    resampled_messages = messages_data.resample('D', on='created_at').size()
elif granularity == 'Weekly':
    resampled_data = filtered_data.resample('W', on='joined_at').size()
    resampled_data1 = resampled_data[:-1]
    resampled_messages = messages_data.resample('W', on='created_at').size()
else:
    resampled_data = filtered_data.resample('M', on='joined_at').size()
    resampled_data1 = resampled_data[:-1]
    resampled_messages = messages_data.resample('M', on='created_at').size()


total_users = len(user_data)
monthly_signups = user_data.resample('M', on='joined_at').size()

# Identify the last two months in the data for comparison
if len(monthly_signups) >= 2:
    last_month_users = monthly_signups.iloc[-2]
    previous_month_users = monthly_signups.iloc[-3]
    
    # Calculate the month-over-month growth
    if previous_month_users > 0:
        month_over_month_growth = ((last_month_users - previous_month_users) / previous_month_users) * 100
    else:
        month_over_month_growth = 0  # Avoid division by zero if no users were signed up the month before last
else:
    last_month_users = 0
    month_over_month_growth = 0 


daily_signups = user_data.resample('D', on='joined_at').size()
avg_daily_signups = daily_signups.mean()


kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(label="Total Users", value=total_users)
with kpi2:
    st.metric(label="Last Month Users", value=last_month_users, delta=int(last_month_users - previous_month_users))
with kpi3:
    st.metric(label="Average Daily Sign-ups", value=f"{avg_daily_signups:.2f}")
with kpi4:
    st.metric(label="Month-over-Month Growth", value=f"{month_over_month_growth:.2f}%")

# Convert to DataFrame for Plotly
resampled_data_df = pd.DataFrame({
    'Date': resampled_data1.index,
    'Count': resampled_data1.values
})

# Create a Plotly express line chart
fig = px.line(resampled_data_df, x='Date', y='Count', title='User Growth Over Time',
              labels={'Count': 'Number of Users'}, markers=True)

# Improving tooltips
fig.update_traces(mode='lines+markers', hoverinfo='all')

# Show plot in Streamlit
st.plotly_chart(fig, use_container_width=True)

# Calculate the cumulative sum
cumulative_data = resampled_data.cumsum()

# Convert to DataFrame for plotting
cumulative_data_df = pd.DataFrame({
    'Date': cumulative_data.index,
    'Cumulative Count': cumulative_data.values
})

# Create a line chart using Plotly Express
fig = px.line(cumulative_data_df, x='Date', y='Cumulative Count', title='Cumulative User Growth Over Time',
              labels={'Cumulative Count': 'Total Users'}, markers=True)

# Improving tooltips for better insight
fig.update_traces(mode='lines+markers', hoverinfo='all')

# Display the plot in Streamlit
st.plotly_chart(fig, use_container_width=True)

continent_counts = user_data['Continent'].value_counts().reset_index()
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

col1, col2 = st.columns(2)

with col1:
    top_join_dates = user_data['joined_at'].dt.date.value_counts().head(7)
    st.write("Top 5 dates with the most user joins:", top_join_dates)

with col2:
    # Assuming 'data' is your DataFrame and 'joined_at' is already a datetime column
    user_data['day_of_week'] = user_data['joined_at'].dt.day_name()

    # Count the total number of users joining on each day of the week
    weekly_counts = user_data['day_of_week'].value_counts()

    # Count the number of unique weeks in the dataset to calculate the average
    num_weeks = user_data['joined_at'].dt.to_period('W').nunique()

    # Calculate the average number of joins per day of the week
    average_joins_per_day = weekly_counts / num_weeks
    st.write("Average user joins by day of the week:", average_joins_per_day)

user_activity = messages_data['username'].value_counts()
active_users = messages_data['username'].nunique()
total_users = user_data['user_id'].nunique()

# Most Active Users
st.subheader('Top 20 Most Active Users')
fig = px.bar(user_activity.head(20), title='Top 20 Active Users', labels={'index': 'Username', 'value': 'Message Count'}, orientation='h', color='value', color_continuous_scale='rainbow')
st.plotly_chart(fig)

# Active vs Inactive Users
st.subheader('Active vs. Inactive Users')
active_inactive = {'Status': ['Active', 'Inactive'], 'Count': [active_users, total_users - active_users]}
active_inactive_df = pd.DataFrame(active_inactive)
fig = px.pie(active_inactive_df, values='Count', names='Status', title='Percentage of Active and Inactive Users')
st.plotly_chart(fig)

# Most Active Times
st.subheader('Most Active Times on Server')
messages_data['hour'] = messages_data['created_at'].dt.hour
hourly_activity = messages_data['hour'].value_counts().sort_index().reset_index()
hourly_activity.columns = ['hour', 'Message Count']  # Rename columns for clarity

# Convert hour to military time format (e.g., 0 -> 0000, 23 -> 2300)
hourly_activity['hour_military'] = hourly_activity['hour'].apply(lambda x: f"{x:02}00")

# Create a horizontal bar chart with a color scale
fig = px.bar(hourly_activity, y='hour_military', x='Message Count', title='Hourly Activity on Server',
             labels={'hour_military': 'Hour of the Day (Military Time)', 'Message Count': 'Number of Messages'},
             color='Message Count',  # Use the message count for color scale
             color_continuous_scale='Viridis',
             orientation='h')

# Adding text labels on the bars
fig.update_traces(text=hourly_activity['Message Count'], textposition='outside')
st.plotly_chart(fig)


# Activity Trend Over Time
st.subheader('Activity Trend Over Time')
fig = px.line(resampled_messages.reset_index(name='Number of Messages'), x='created_at', y='Number of Messages', title='Daily Messages Sent Over Time',
              labels={'created_at': 'Date'})
fig.update_traces(line_color='#147852')

st.plotly_chart(fig)

# Calculate the cumulative sum
cumulative_data = resampled_messages.cumsum()

# Convert to DataFrame for plotting
cumulative_data_df = pd.DataFrame({
    'Date': cumulative_data.index,
    'Cumulative Count': cumulative_data.values
})

# Create a line chart using Plotly Express
fig = px.line(cumulative_data_df, x='Date', y='Cumulative Count', title='Cumulative User Growth Over Time',
              labels={'Cumulative Count': 'Total Users'}, markers=True)

# Improving tooltips for better insight
fig.update_traces(mode='lines+markers', hoverinfo='all', line_color='#147852')

# Display the plot in Streamlit
st.plotly_chart(fig, use_container_width=True)
