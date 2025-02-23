import pandas as pd
from rapidfuzz import process

# Load and format data
crime_df = pd.read_csv("data/crime_rate_by_county.csv")
crime_df['fips'] = crime_df['fips'].astype(str).str.zfill(5)

census_df = pd.read_csv("data/county_census_data.csv")
census_df['fips'] = census_df['fips'].astype(str).str.zfill(5)

# Extract 'States' column using the first two digits of FIPS
crime_df['States'] = crime_df['fips'].str[:2]
census_df['States'] = census_df['fips'].str[:2]

# Function to match Crime_Rate for each census FIPS
def match_crime_rate(census_fips, census_state, crime_df):
    # Filter crime_df for the correct state
    state_filtered_crime = crime_df[crime_df['States'] == census_state].copy()
    if state_filtered_crime.empty:
        return None

    crime_fips_list = state_filtered_crime['fips'].tolist()
    crime_rates = state_filtered_crime['Crime_Rate'].tolist()

    # 1. Exact match
    if census_fips in crime_fips_list:
        return state_filtered_crime.loc[state_filtered_crime['fips'] == census_fips, 'Crime_Rate'].iloc[0]

    # 2. Fuzzy matching to find the nearest FIPS in crime_df
    fuzzy_match = process.extractOne(census_fips, crime_fips_list)
    if fuzzy_match:
        match_fips, score = fuzzy_match[:2]
        if score >= 80:  # Adjust threshold as needed for similarity
            return state_filtered_crime.loc[state_filtered_crime['fips'] == match_fips, 'Crime_Rate'].iloc[0]

    return None  # Return None if no match is found

# Apply the matching logic to each census FIPS
census_df['Crime_Rate'] = census_df.apply(
    lambda row: match_crime_rate(row['fips'], row['States'], crime_df),
    axis=1
)

# Create final output DataFrame with only census_fips and Crime_Rate
final_df = census_df[['fips', 'Crime_Rate']]
final_df = final_df.dropna(subset=['Crime_Rate'])  # Drop rows where Crime_Rate is None

# Display results
print(final_df)

# Save output
final_df.to_csv('data/fuzzy_matched_crime_data.csv', index=False)