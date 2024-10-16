import pandas as pd

# Load the CSV file
file_path = './weather_data_no_temp.csv'
data = pd.read_csv(file_path)

# Convert the Timestamp column to seconds since the epoch (UNIX time)
data['Timestamp'] = pd.to_datetime(data['Timestamp']).astype(int) // 10**9

# Save the new file
output_path = './weather_data_no_temp_seconds.csv'
data.to_csv(output_path, index=False)

print("Timestamp has been converted to seconds and saved to", output_path)
