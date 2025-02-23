import gradio as gr
import geopandas as gpd
import pandas as pd
import functools
import plotly.graph_objects as go

@functools.lru_cache(maxsize=None)
def load_data():
    """Load and validate geographic data from final_county_metrics.csv"""
    df = pd.read_csv("data/final_county_metrics.csv", dtype={'fips': str})
    # Filter out rows where geometry is NaN or '0'
    df = df[df['geometry'].notna() & (df['geometry'] != '0')]
    df['geometry'] = gpd.GeoSeries.from_wkt(df['geometry'])
    gdf = gpd.GeoDataFrame(df, crs="EPSG:4269")
    gdf = gdf.to_crs(epsg=4326)
    
    numeric_cols = [
        'pct_cost_burdened', 'pct_severe_cost_burdened', 'vacancy_to_population_ratio',
        'population_in_poverty', 'education_to_income', 'Crime_Rate',
        'school_achievement_score', 'unemployment_rate',
        'value_to_income_ratio', 'poverty_to_rent_burden'
    ] + [f'fmr_{i}' for i in range(5)] + [f'rent_to_income_ratio_{i}' for i in range(5)] + \
        [f'fmr_vs_median_rent_diff_{i}' for i in range(5)] + [f'fmr_vs_median_rent_percent_{i}' for i in range(5)] + \
        [f'affordability_gap_{i}' for i in range(5)] + [f'voucher_feasibility_{i}' for i in range(5)]
    
    gdf[numeric_cols] = gdf[numeric_cols].apply(pd.to_numeric, errors='coerce')
    
    # Get unique states, filter out invalid entries (like '0'), and sort
    states = sorted(gdf['state_name'].dropna().unique().tolist())
    states.insert(0, "USA")  # Add option for full U.S. view
    
    return gdf, gdf.__geo_interface__, states

METRIC_INFO = {
    'FMR': {'format': '${:.2f}', 'description': 'Fair Market Rent set by HUD, representing the 40th percentile rent for standard-quality housing in a county. Lower is better for affordability, as it indicates lower rental costs.', 'prefix': '$', 'bedroom': True},
    'Rent-to-Income Ratio': {'format': '{:.1f}%', 'description': 'Annual FMR as a percentage of median household income, indicating rental affordability. Lower is better (ideally ≤30%), as higher ratios signal cost burden.', 'prefix': '', 'bedroom': True},
    'FMR vs Median Rent Difference': {'format': '${:.2f}', 'description': 'Dollar difference between Fair Market Rent and median gross rent, showing how subsidized rents compare to market rates. Lower is better if negative (FMR < median), indicating more affordable subsidized options.', 'prefix': '$', 'bedroom': True},
    'FMR Deviation (%)': {'format': '{:.1f}%', 'description': 'Percentage difference between FMR and median gross rent, reflecting the relative affordability of subsidized rents. Lower is better if negative, as it suggests FMR is more affordable than median rent.', 'prefix': '', 'bedroom': True},
    'Affordability Gap': {'format': '${:.2f}', 'description': 'Excess annual rent cost over 30% of median household income, measuring unaffordability. Lower is better (ideally $0), as higher gaps indicate greater financial strain.', 'prefix': '$', 'bedroom': True},
    'Voucher Feasibility': {'format': '{:.1f}%', 'description': 'FMR as a percentage of median gross rent, indicating how well housing vouchers cover market rents. Higher is better (ideally ≥100%), as it shows vouchers can meet or exceed market costs.', 'prefix': '', 'bedroom': True},
    'Cost Burden': {'format': '{:.1f}%', 'description': 'Percentage of renters spending more than 30% of their income on rent, a key affordability indicator. Lower is better, as higher percentages signal widespread housing cost stress.', 'prefix': '', 'bedroom': False},
    'Severe Cost Burden': {'format': '{:.1f}%', 'description': 'Percentage of renters spending more than 50% of their income on rent, indicating extreme housing cost pressure. Lower is better, as higher values highlight severe affordability challenges.', 'prefix': '', 'bedroom': False},
    'Vacancy Rate': {'format': '{:.4f}', 'description': 'Ratio of vacant housing units to total population, reflecting housing supply availability. Lower is generally better for market stability, but higher may indicate opportunities for agents in underutilized areas.', 'prefix': '', 'bedroom': False},
    'Poverty Population': {'format': '{:.0f}', 'description': 'Number of residents living below the poverty line, indicating economic need tied to housing affordability. Lower is better, as higher numbers suggest greater housing and financial strain.', 'prefix': '', 'bedroom': False},
    'Education to Income': {'format': '${:.2f}', 'description': 'Estimated income adjusted by the proportion of adults with bachelor’s degrees, reflecting economic potential. Higher is better, as it suggests stronger earning capacity, potentially supporting housing affordability.', 'prefix': '$', 'bedroom': False},
    'School Achievement': {'format': '{:.1f}', 'description': 'County-level school performance score, where 0 represents the national baseline (average performance across the U.S.). Higher is better, as scores above 0 indicate above-average educational outcomes, which can enhance community desirability and property values.', 'prefix': '', 'bedroom': False},
    'Unemployment Rate': {'format': '{:.1f}%', 'description': 'Percentage of the workforce that is unemployed, indicating economic health. Lower is better, as higher rates suggest weaker job markets, potentially impacting housing demand and affordability.', 'prefix': '', 'bedroom': False},
    'Value to Income Ratio': {'format': '{:.1f}', 'description': 'Ratio of median home value to median household income, measuring homeownership affordability. Lower is better (ideally 2.5–3), as higher ratios indicate homes are less affordable relative to income.', 'prefix': '', 'bedroom': False},
    'Poverty to Rent Burden': {'format': '{:.2f}', 'description': 'Ratio of the poverty population to the annual median gross rent, indicating the burden of poverty on housing costs. Lower is better, as higher values suggest greater strain on low-income residents to afford housing.', 'prefix': '', 'bedroom': False},
    'Crime Rate': {'format': '{:.2f}', 'description': 'Scaled crime ratio (total crimes divided by population, scaled from 0-100), indicating safety and security. Lower is better as higher values reflect greater crime levels, reducing community desirability.', 'prefix': '', 'bedroom': False}
}

PERCENTAGE_METRICS = {
    'Rent-to-Income Ratio', 'FMR Deviation (%)', 'Voucher Feasibility', 
    'Cost Burden', 'Severe Cost Burden', 'Unemployment Rate'
}

def create_map(bedroom_type, metric_type, state=None):
    """Generate interactive choropleth map with optional state zoom"""
    gdf, geojson, states = load_data()
    
    # Filter by state if specified, otherwise use full USA
    if state and state != "USA":
        gdf = gdf[gdf['state_name'] == state]
        if gdf.empty:
            return go.Figure()  # Return empty figure if no data for state
    
    bedroom_num = int(bedroom_type[0]) if METRIC_INFO[metric_type]['bedroom'] else None
    
    metric_mapping = {
        'FMR': f'fmr_{bedroom_num}',
        'Rent-to-Income Ratio': f'rent_to_income_ratio_{bedroom_num}',
        'FMR vs Median Rent Difference': f'fmr_vs_median_rent_diff_{bedroom_num}',
        'FMR Deviation (%)': f'fmr_vs_median_rent_percent_{bedroom_num}',
        'Affordability Gap': f'affordability_gap_{bedroom_num}',
        'Voucher Feasibility': f'voucher_feasibility_{bedroom_num}',
        'Cost Burden': 'pct_cost_burdened',
        'Severe Cost Burden': 'pct_severe_cost_burdened',
        'Vacancy Rate': 'vacancy_to_population_ratio',
        'Poverty Population': 'population_in_poverty',
        'Education to Income': 'education_to_income',
        'School Achievement': 'school_achievement_score',
        'Unemployment Rate': 'unemployment_rate',
        'Value to Income Ratio': 'value_to_income_ratio',
        'Poverty to Rent Burden': 'poverty_to_rent_burden',
        'Crime Rate': 'Crime_Rate'  # Assuming Crime_Rate is now the scaled ratio (0-100)
    }
    
    metric_col = metric_mapping[metric_type]
    format_str = METRIC_INFO[metric_type]['format']
    
    gdf['hover_text'] = gdf.apply(
        lambda x: f"<b>{x['county_name']}</b><br>"
                 f"State: {x['state_name']}<br>"
                 f"{metric_type}: {format_str.format(x[metric_col])}" if pd.notna(x[metric_col]) else "",
        axis=1
    )

    # Use raw values for percentage metrics (already in %)
    z = gdf[metric_col]
    tickformat = '.1f' if metric_type in PERCENTAGE_METRICS else ',.0f'
    ticksuffix = '%' if metric_type in PERCENTAGE_METRICS else ''
    tickprefix = METRIC_INFO[metric_type]['prefix']

    # Set custom zmin and zmax for percentage metrics
    if metric_type in PERCENTAGE_METRICS:
        zmin = 0
        zmax = min(gdf[metric_col].max(), 200)  # Cap at 200% to handle outliers
    else:
        zmin = None
        zmax = None

    fig = go.Figure(go.Choropleth(
        geojson=geojson,
        locations=gdf['fips'],
        z=z,
        zmin=zmin,
        zmax=zmax,
        featureidkey="properties.fips",
        colorscale='Viridis',
        marker_line_width=0.5,
        marker_line_color='white',
        hoverinfo="text",
        hovertext=gdf['hover_text'],
        colorbar=dict(
            title=metric_type,
            thickness=15,
            tickfont=dict(size=12),
            tickprefix=tickprefix,
            ticksuffix=ticksuffix,
            tickformat=tickformat
        )
    ))

    # Update layout for state zoom or USA view
    if state and state != "USA":
        # Get state bounds for zoom
        state_bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
        fig.update_layout(
            geo=dict(
                scope='usa',
                projection=dict(type='albers usa'),
                center=dict(lat=(state_bounds[1] + state_bounds[3]) / 2, lon=(state_bounds[0] + state_bounds[2]) / 2),
                lonaxis_range=[state_bounds[0], state_bounds[2]],
                lataxis_range=[state_bounds[1], state_bounds[3]],
                showlakes=True,
                lakecolor='rgba(224, 242, 254, 0.8)',
                landcolor='#f5f5f5'
            )
        )
    else:
        fig.update_layout(
            geo=dict(
                scope='usa',
                projection=dict(type='albers usa'),
                showlakes=True,
                lakecolor='rgba(224, 242, 254, 0.8)',
                landcolor='#f5f5f5'
            )
        )

    fig.update_layout(
        height=600,
        margin=dict(r=0, t=40, l=0, b=0),
        font=dict(family="Arial", color="#333333"),
        paper_bgcolor='#ffffff'
    )
    return fig

def get_stats(bedroom_type, metric_type, state=None):
    """Calculate statistics with county info for min/max, filtered by state if specified"""
    gdf, _, _ = load_data()
    
    # Filter by state if specified, otherwise use full USA
    if state and state != "USA":
        gdf = gdf[gdf['state_name'] == state]
        if gdf.empty:
            return [
                "N/A", "N/A", "N/A (No data)", "N/A (No data)", 
                0, "N/A", "N/A", "N/A"
            ]
    
    bedroom_num = int(bedroom_type[0]) if METRIC_INFO[metric_type]['bedroom'] else None
    
    metric_mapping = {
        'FMR': f'fmr_{bedroom_num}',
        'Rent-to-Income Ratio': f'rent_to_income_ratio_{bedroom_num}',
        'FMR vs Median Rent Difference': f'fmr_vs_median_rent_diff_{bedroom_num}',
        'FMR Deviation (%)': f'fmr_vs_median_rent_percent_{bedroom_num}',
        'Affordability Gap': f'affordability_gap_{bedroom_num}',
        'Voucher Feasibility': f'voucher_feasibility_{bedroom_num}',
        'Cost Burden': 'pct_cost_burdened',
        'Severe Cost Burden': 'pct_severe_cost_burdened',
        'Vacancy Rate': 'vacancy_to_population_ratio',
        'Poverty Population': 'population_in_poverty',
        'Education to Income': 'education_to_income',
        'School Achievement': 'school_achievement_score',
        'Unemployment Rate': 'unemployment_rate',
        'Value to Income Ratio': 'value_to_income_ratio',
        'Poverty to Rent Burden': 'poverty_to_rent_burden',
        'Crime Rate': 'Crime_Rate'  # Now reflects the scaled 0-100 ratio
    }
    
    metric_col = metric_mapping[metric_type]
    gdf = gdf.dropna(subset=[metric_col])
    format_str = METRIC_INFO[metric_type]['format']
    
    # Handle empty DataFrame
    if gdf.empty:
        return [
            "N/A", "N/A", "N/A (No data)", "N/A (No data)", 
            0, "N/A", "N/A", "N/A"
        ]
    
    min_row = gdf.loc[gdf[metric_col].idxmin()]
    max_row = gdf.loc[gdf[metric_col].idxmax()]
    
    return [
        format_str.format(gdf[metric_col].mean()),
        format_str.format(gdf[metric_col].median()),
        f"{format_str.format(gdf[metric_col].min())} ({min_row['county_name']}, {min_row['state_name']})",
        f"{format_str.format(gdf[metric_col].max())} ({max_row['county_name']}, {max_row['state_name']})",
        len(gdf),
        format_str.format(gdf[metric_col].std()),
        format_str.format(gdf[metric_col].quantile(0.25)),
        format_str.format(gdf[metric_col].quantile(0.75))
    ]

# Metric definition table
ALL_METRICS_DISPLAY = """
### Metric Definitions
| Metric | Description |
|--------|-------------|
""" + "\n".join(
    f"| **{metric}** | {METRIC_INFO[metric]['description']} |"
    for metric in METRIC_INFO
)

# Define theme and CSS
theme = gr.themes.Default(
    primary_hue="blue",
    secondary_hue="gray",
    neutral_hue="gray",
    font=("Arial", "sans-serif"),
    font_mono=("Arial", "sans-serif"),
).set(
    body_background_fill="#f5f5f5",
    block_background_fill="#ffffff",
    block_border_width="1px",
    block_border_color="#e0e0e0",
    input_background_fill="#ffffff",
    button_primary_background_fill="#2563eb",
    button_primary_text_color="#ffffff"
)

css = """
.container { max-width: 1400px; margin: 0 auto; padding: 1rem; }
.stats-panel { padding: 1rem; border-radius: 8px; }
.map-container { padding: 1rem; border-radius: 8px; }
.metric-info { font-size: 0.9rem; color: #666666; margin-top: 0.5rem; }
.all-metrics { font-size: 0.9rem; margin-top: 1rem; }
.all-metrics table { width: 100%; border-collapse: collapse; }
.all-metrics th, .all-metrics td { padding: 0.5rem; text-align: left; border-bottom: 1px solid #e0e0e0; }
.all-metrics th:first-child, .all-metrics td:first-child { width: 30%; }
"""

with gr.Blocks(theme=theme, css=css, title="U.S. Housing Market Analysis") as app:
    gr.Markdown(
        """
        # U.S. Housing Market Analysis
        Explore housing affordability and socioeconomic metrics across U.S. counties
        """,
        elem_classes="container"
    )
    
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Group(elem_classes="stats-panel"):
                state_select = gr.Dropdown(
                    choices=load_data()[2],  # Use cached states, ensuring no "0"
                    value="USA",
                    label="State",
                    visible=True
                )
                bedroom_select = gr.Dropdown(
                    choices=["0-Bedroom", "1-Bedroom", "2-Bedroom", "3-Bedroom", "4-Bedroom"],
                    value="2-Bedroom",
                    label="Bedroom Size",
                    visible=True
                )
                metric_select = gr.Dropdown(
                    choices=list(METRIC_INFO.keys()),
                    value="Cost Burden",
                    label="Metric"
                )
                metric_description = gr.Markdown(elem_classes="metric-info")
                stats_output = gr.Dataframe(
                    headers=["Statistic", "Value"],
                    label="Summary Statistics",
                    interactive=False,
                    wrap=True
                )
                gr.Markdown(ALL_METRICS_DISPLAY, elem_classes="all-metrics")
        
        with gr.Column(scale=2):
            with gr.Group(elem_classes="map-container"):
                map_output = gr.Plot(label="Geographic Distribution")

    def update_display(bedroom_type, metric_type, state):
        """Update map, stats, and description based on selection"""
        stats = get_stats(bedroom_type, metric_type, state)
        stats_data = [
            ["Mean", stats[0]],
            ["Median", stats[1]],
            ["Minimum", stats[2]],
            ["Maximum", stats[3]],
            ["Counties", stats[4]],
            ["Std Dev", stats[5]],
            ["Q1 (25th)", stats[6]],
            ["Q3 (75th)", stats[7]]
        ]
        description = f"**{metric_type}**: {METRIC_INFO[metric_type]['description']}"
        bedroom_visibility = METRIC_INFO[metric_type]['bedroom']
        return (
            create_map(bedroom_type, metric_type, state),
            stats_data,
            description,
            gr.update(visible=bedroom_visibility)
        )

    # Event handlers
    inputs = [bedroom_select, metric_select, state_select]
    outputs = [map_output, stats_output, metric_description, bedroom_select]
    
    for input_elem in inputs[:2]:  # Exclude state_select for simplicity
        input_elem.change(
            update_display,
            inputs=inputs,
            outputs=outputs
        )
    state_select.change(
        update_display,
        inputs=inputs,
        outputs=outputs
    )

    app.load(
        fn=lambda: update_display("2-Bedroom", "Cost Burden", "USA"),
        outputs=outputs
    )

if __name__ == "__main__":
    app.launch(share = True)