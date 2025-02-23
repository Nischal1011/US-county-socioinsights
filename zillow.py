import pandas as pd  

if __name__ == "__main__":
    # Load the Zillow ZIP-level dataset
    zillow_df = pd.read_csv("data/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv")

    zillow_df_v1 = zillow_df[['RegionID', 'CountyName', '2025-01-31']]

    # Aggregate ZIP-level ZHVI to county level by taking the median home value per county
    county_zhvi = (
        zillow_df_v1
        .groupby('RegionID')  # Group by county
        .agg({
            '2025-01-31': 'median'  # Use median ZHVI across ZIPs in each county
        })
        .reset_index()
        .rename(columns={'2025-01-31': 'median_zhvi_county'})  # Rename for clarity
    )

    county_zhvi.rename(columns = {'RegionID': 'fips', '2025-01-31':'median_zhvi'}, inplace = True)

    county_zhvi['fips'] = county_zhvi['fips'].astype('str').str.zfill(5)


    # Save to CSV for integration with other data
    county_zhvi.to_csv("data/county_zhvi_data.csv", index=False)
    print("Data saved to 'county_zhvi_data.csv'")