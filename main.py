import pandas as pd
import numpy as np

# Function to load and standardize FIPS
def load_and_standardize_df(file_path, fips_col="fips"):
    """
    Loads a CSV and ensures FIPS is a zero-padded string.
    """
    df = pd.read_csv(file_path)
    df[fips_col] = df[fips_col].astype(str).str.zfill(5)
    return df

# Function to calculate affordability metrics
def calculate_affordability_metrics(df):
    """
    Adds affordability metrics to the merged DataFrame.
    """
    # Handle missing values
    df["median_gross_rent"] = df["median_gross_rent"].fillna(df.groupby("state_fips")["median_gross_rent"].transform("median"))
    df["median_household_income"] = df["median_household_income"].fillna(df.groupby("state_fips")["median_household_income"].transform("median"))
    df.fillna({"total_vacant_housing_units": 0, "school_achievement_score": 0, "unemployment_rate": 0}, inplace=True)
    # Replace negative values with NaN
    df["median_gross_rent"] = np.where(df["median_gross_rent"] < 0, np.nan, df["median_gross_rent"])
    df["median_household_income"] = np.where(df["median_household_income"] < 0, np.nan, df["median_household_income"])

    # Rent-to-Income Ratio (for median_gross_rent and FMRs)
    df["rent_to_income_ratio"] = np.where(
        df["median_household_income"] > 0,
        (df["median_gross_rent"] * 12 / df["median_household_income"]) * 100,
        np.nan
    )
    for beds in range(5):
        df[f"rent_to_income_ratio_{beds}"] = np.where(
            df["median_household_income"] > 0,
            (df[f"fmr_{beds}"] * 12 / df["median_household_income"]) * 100,
            np.nan
        )

    # Percentage of Cost-Burdened Renters (>30% income)
    cost_burdened_cols = ["rent_30_to_34_9_percent", "rent_35_to_39_9_percent", 
                          "rent_40_to_49_9_percent", "rent_50_percent_or_more"]
    if all(col in df.columns for col in cost_burdened_cols):
        df["pct_cost_burdened"] = (
            df[cost_burdened_cols].sum(axis=1) / df["total_renter_households_cost"]
        ) * 100
    else:
        df["pct_cost_burdened_proxy"] = np.where(
            df["rent_to_income_ratio"] > 30,
            100 * (df["renters_50percent_plus_income"] / df["total_population"]),
            0
        )

    # Severe Cost Burden (>50% income)
    df["pct_severe_cost_burdened"] = (df["renters_50percent_plus_income"] / df["total_population"]) * 100

    # FMR vs Median Gross Rent Differences
    for beds in range(5):
        df[f"fmr_vs_median_rent_percent_{beds}"] = np.where(
            (df["median_gross_rent"] > 0) & (df[f"fmr_{beds}"] > 0),
            ((df[f"fmr_{beds}"] - df["median_gross_rent"]) / df["median_gross_rent"]) * 100,
            np.nan
        )

    # Affordability Gap (for median_gross_rent and FMRs)
    for beds in range(5):
        df[f"affordability_gap_{beds}"] = (df[f"fmr_{beds}"] * 12) - (df["median_household_income"] * 0.3)
        df[f"affordability_gap_{beds}"] = np.where(df["median_household_income"] > 0, df[f"affordability_gap_{beds}"], np.nan)

    # Voucher Feasibility
    for beds in range(5):
        df[f"voucher_feasibility_{beds}"] = np.where(
            (df["median_gross_rent"] > 0) & (df[f"fmr_{beds}"] > 0),
            (df[f"fmr_{beds}"] / df["median_gross_rent"]) * 100,
            np.nan
        )

    # Housing Wage (for median_gross_rent and FMRs)
    df["housing_wage"] = (df["median_gross_rent"] * 12) / 2080
    for beds in range(5):
        df[f"housing_wage_{beds}"] = (df[f"fmr_{beds}"] * 12) / 2080

    # Housing Wage to Minimum Wage
    for beds in range(5):
        df[f"housing_wage_to_min_wage_{beds}"] = np.where(
            df["min_wage"] > 0,
            (df[f"housing_wage_{beds}"] / df["min_wage"]) * 100,
            np.nan
        )

    # New Metrics from merged_df
    df["value_to_income_ratio"] = np.where(
        df["median_household_income"] > 0,
        df["median_value_owner_occupied"] / df["median_household_income"],
        np.nan
    )

    df["poverty_to_rent_burden"] = np.where(
        df["median_gross_rent"] > 0,
        df["population_in_poverty"] / (df["median_gross_rent"] * 12),
        np.nan
    )

    df["vacancy_to_population_ratio"] = df["total_vacant_housing_units"] / df["total_population"]

    df["education_to_income"] = (df["population_25plus_bachelors"] / df["population_25plus_total"]) * df["median_household_income"]

    df["stability_index"] = df["population_same_residence_1yr"] / df["total_population"]

    return df


def nullify_outliers_minimally(df, columns, threshold=3.0):
    for col in columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = max(Q1 - threshold * IQR, df[col].min())
        upper_bound = min(Q3 + threshold * IQR, df[col].max())
        df[col] = df[col].where((df[col] >= lower_bound) & (df[col] <= upper_bound), None)
    return df

if __name__ == "__main__":
    # Load and standardize datasets
    crime_df = load_and_standardize_df("data/fuzzy_matched_crime_data.csv")
    unemployment_df = load_and_standardize_df("data/national_county_bls_unemployment.csv")
    school_score_df = load_and_standardize_df("data/seda_county_2019.csv")
    zillow_home_value_df = load_and_standardize_df("data/county_zhvi_data.csv")
    census_df = load_and_standardize_df("data/county_census_data.csv")
    census_df = census_df.drop(['state_fips', 'median_gross_rent', 'total_vacant_housing_units', 'county_fips', 'median_household_income', 'NAME'], axis = 1)
    fmr_df = pd.read_csv("data/census_fmr_county.csv")
    fmr_df["GEOID"] = fmr_df["GEOID"].astype(str).str.zfill(5)  # Assuming GEOID is fips equivalent
    fmr_df.rename(columns={"GEOID": "fips"}, inplace=True)
    fmr_df = fmr_df.drop_duplicates(subset="fips")
    # Merge datasets
    merged_df = census_df.merge(school_score_df, on="fips", how="left")
    merged_df_v1 = merged_df.merge(unemployment_df, on="fips", how="left")
    merged_df_v2 = merged_df_v1.merge(zillow_home_value_df, on="fips", how="left")
    merged_df_v3 = merged_df_v2.merge(crime_df, on="fips", how="left")
    merged_df_v4 = merged_df_v3.merge(fmr_df, on="fips", how="left")

   


    final_df = nullify_outliers_minimally(merged_df_v4, ['median_household_income', 'median_value_owner_occupied'])

    final_df = calculate_affordability_metrics(merged_df_v4)



    cols = [
        'fmr_0', 'fmr_1', 'fmr_2', 'fmr_3', 'fmr_4', 'geometry', 
        'rent_to_income_ratio_0', 'rent_to_income_ratio_1', 
        'rent_to_income_ratio_2', 'rent_to_income_ratio_3', 'rent_to_income_ratio_4', 
        'pct_cost_burdened', 'pct_severe_cost_burdened', 
        'fmr_vs_median_rent_diff_0', 'fmr_vs_median_rent_percent_0', 
        'fmr_vs_median_rent_diff_1', 'fmr_vs_median_rent_percent_1', 
        'fmr_vs_median_rent_diff_2', 'fmr_vs_median_rent_percent_2', 
        'fmr_vs_median_rent_diff_3', 'fmr_vs_median_rent_percent_3', 
        'fmr_vs_median_rent_diff_4', 'fmr_vs_median_rent_percent_4', 
        'affordability_gap_0', 'affordability_gap_1', 'affordability_gap_2', 
        'affordability_gap_3', 'affordability_gap_4', 
        'voucher_feasibility_0', 'voucher_feasibility_1', 
        'voucher_feasibility_2', 'voucher_feasibility_3', 'voucher_feasibility_4',
        'vacancy_to_population_ratio', 'population_in_poverty', 'stability_index', 
        'education_to_income', 'school_achievement_score'
        , 'unemployment_rate', 'value_to_income_ratio', 'poverty_to_rent_burden', 'state_name', 'county_name' ,'geometry','Crime_Rate', 'fips'
    ]

    final_df_v1 = final_df[cols]
    final_df_v1.to_csv("data/final_county_metrics.csv", index=False)
    
    print("Merged data with metrics saved to 'data/final_county_metrics.csv'")