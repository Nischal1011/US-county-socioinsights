import pandas as pd
import numpy as np

# Load your data
df = pd.read_csv('data/39062-0001-Data.tsv', sep='\t')

# Step 1: Format FIPS codes
df['STATE'] = df['STATE'].astype(str).str.zfill(2)
df['COUNTY'] = df['COUNTY'].astype(str).str.zfill(3)
df['FIPS'] = df['STATE'] + df['COUNTY']

# Filter to most recent year
df = df[df['YEAR'] == df['YEAR'].max()]

# Step 2: Clean population data
df.loc[df['POP'] > 90000, 'POP'] = np.nan
df.loc[df['POP'] < 100, 'POP'] = np.nan

# Step 3: Clean crime data
crime_columns = ['AW', 'AB', 'AI', 'AA', 'JW', 'JB', 'JI', 'JA', 'AH', 'AN', 'JH', 'JN']
for col in crime_columns:
    df.loc[df[col] > 90000, col] = np.nan
    df.fillna({col: 0}, inplace=True)

# Step 4: Calculate total crimes per row
df['Total_Crimes'] = df[crime_columns].sum(axis=1, skipna=True)

# Step 5: Aggregate by county using max for crimes
agg_data = df.groupby('FIPS').agg({
    'Total_Crimes': 'max',
    'POP': 'max',
}).reset_index()

# Step 6: Calculate raw crime ratio
agg_data['Crime_Ratio'] = agg_data['Total_Crimes'] / agg_data['POP']

# Step 7: Scale using percentiles (0-100)
agg_data['Scaled_Crime_Ratio'] = agg_data['Crime_Ratio'].rank(pct=True) * 100

# Handle edge cases
agg_data.loc[agg_data['POP'].isna(), ['Crime_Ratio', 'Scaled_Crime_Ratio']] = np.nan
agg_data.loc[agg_data['Total_Crimes'] == 0, 'Scaled_Crime_Ratio'] = 0

# Step 8: Assign grades based on percentiles
def assign_grade(ratio):
    if pd.isna(ratio):
        return np.nan
    elif ratio <= 20:  # Bottom 20%
        return 'A'
    elif ratio <= 40:  # 20-40%
        return 'B'
    elif ratio <= 60:  # 40-60%
        return 'C'
    elif ratio <= 80:  # 60-80%
        return 'D'
    else:             # Top 20%
        return 'E'

agg_data['Crime_Grade'] = agg_data['Scaled_Crime_Ratio'].apply(assign_grade)

# Step 9: Rename and save
agg_data.rename(columns={'FIPS': 'fips'}, inplace=True)
agg_data.to_csv('data/crime_rate_by_county.csv', index=False)

# Validation
print(agg_data.describe())
print(agg_data.head())
print("\nTop 5 by Scaled_Crime_Ratio:")
print(agg_data.nlargest(5, 'Scaled_Crime_Ratio'))
print("\nGrade Distribution:")
print(agg_data['Crime_Grade'].value_counts().sort_index())

agg_data.rename(columns={'Scaled_Crime_Ratio': 'Crime_Rate'}, inplace=True)
agg_data[['fips', 'Crime_Rate']].to_csv("data/crime_rate_by_county.csv", index=False)
print("Data saved to 'data/crime_rate_by_county.csv'")