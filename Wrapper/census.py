import requests
import pandas as pd
import os

class CensusAPIWrapper:
    BASE_URL = "https://api.census.gov/data/2023/acs/acs5"

    def __init__(self, api_key):
        self.api_key = api_key

    def get_county_data(self, variables):
        """Fetch data at county level"""
        params = {
            "get": ",".join(variables + ["NAME"]),
            "for": "county:*",
            "key": self.api_key
        }
        return self._make_request(params)

    def _make_request(self, params):
        """Shared request handling logic"""
        response = requests.get(self.BASE_URL, params=params)
        
        if response.status_code != 200:
            raise Exception(f"API Request Failed: {response.status_code} - {response.text}")

        data = response.json()
        df = pd.DataFrame(data[1:], columns=data[0])
        
        # Clean column names
        df = df.rename(columns={
            "county": "county_fips",
            "state": "state_fips"
        })
        
        return df

if __name__ == "__main__":
    API_KEY = os.getenv("censusapi")
    census_api = CensusAPIWrapper(API_KEY)

    variables = {
        # Housing Market Stability
        "B25004_001E": "total_vacant_housing_units",      # Vacancy rate proxy
        "B25077_001E": "median_value_owner_occupied",    # Median home value
        "B25064_001E": "median_gross_rent",              # Rental market indicator
        # Economic Indicators
        "B19013_001E": "median_household_income",         # Income stability
        "B17001_002E": "population_in_poverty",           # Poverty count
        # Demographic Stability
        "B01003_001E": "total_population",               # Population size
        "B07001_001E": "population_same_residence_1yr",  # Mobility/stability
        # Educational Quality
        "B15003_022E": "population_25plus_bachelors",    # Bachelor’s degree or higher
        "B15003_001E": "population_25plus_total",        # Total 25+ for education rate
        # Affordability
        "B25070_010E": "renters_50percent_plus_income"    # Renters spending 50%+ on rent
    }

    variable_list = list(variables.keys())

    # Fetch data at county level
    df = census_api.get_county_data(variable_list)

    # Rename columns using the mapping dictionary
    df = df.rename(columns=variables)

    # Convert numeric columns
    numeric_cols = [col for col in df.columns if col not in ["NAME", "county_fips", "state_fips"]]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    df['fips'] = df['state_fips'].astype(str).str.zfill(2) + df['county_fips'].astype(str).str.zfill(3)
    df['fips'] = df['fips'].astype(str).str.zfill(5)

    df.to_csv("data/county_census_data.csv", index=False)
