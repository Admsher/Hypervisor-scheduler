import pandas as pd



def calculate_correlation(df):
    """
    Calculate the correlation matrix between Counts, Duration, and Periodicity.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing 'Counts', 'Duration', and 'Periodicity'.
    
    Returns:
    pd.DataFrame: Correlation matrix.
    """
    # Check if the required columns are in the DataFrame
    required_columns = ['Counts', 'Duration', 'Periodicity']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"The DataFrame must contain the following columns: {required_columns}")

    # Calculate the correlation matrix
    correlation_matrix = df[['Counts', 'Duration', 'Periodicity']].corr()
    
    return correlation_matrix



dataframe=pd.read_excel("function_logs.xlsx")
# Sample data
print(dataframe)
dataframe.drop("ID",axis=1,inplace=True)
dataframe.drop("Time Lapsed",axis=1,inplace=True)
value_counts = dataframe['Function'].value_counts()
value_counts = dataframe['Function'].value_counts()

# List to hold the rows for the new DataFrame
rows = []

# Loop through the desired function values
for function_value in [1, 2, 3, 4, 5]:
    # Use boolean indexing to find the first matching row
    matching_rows = dataframe[dataframe['Function'] == function_value]
    if not matching_rows.empty:
        # Get the first matching row
        row = matching_rows.iloc[0]
        # Add the count of this function to the row
        row['Counts'] = value_counts.get(function_value, 0)
        # Append the modified row to the list
        rows.append(row)

# Create a new DataFrame from the list of rows
new_dataframe = pd.DataFrame(rows)

# Print the new DataFrame
print("\nNew DataFrame with specific rows and counts:")
print(new_dataframe)

correlation_matrix = calculate_correlation(new_dataframe)


print("Correlation Matrix:")
print(correlation_matrix)
