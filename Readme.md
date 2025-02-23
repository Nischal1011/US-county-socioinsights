# U.S. County SocioInsights

## Overview

U.S. County SocioInsights is an innovative tool that provides real estate agents and policymakers with valuable data-driven insights on housing affordability and socioeconomic issues across U.S. counties. This interactive dashboard, developed using Python, Gradio, and Plotly, assists in addressing housing market challenges, improving community well-being, and guiding policy decisions.

### Significance of U.S. County SocioInsights:
- **The Housing Crisis**: With escalating housing costs and a scarcity of affordable options in the U.S., communities face significant hurdles. Real estate professionals and policymakers require data-driven solutions to identify opportunities and formulate effective strategies.
- **Socioeconomic Understanding**: Besides housing concerns, comprehensive knowledge of crime rates, education, and economic circumstances is fundamental for holistic community growth.
- **Interactive Features**: The dashboard offers a user-friendly interface for exploring county-level data, monitoring trends, and visualizing outcomes.

## Key Features

- **User-Friendly Dashboard**: Featuring a Gradio interface with interactive Plotly maps and charts for real-time analysis of housing affordability, crime rates (graded A-E), education scores, and more.
- **Socioeconomic Data**: Detailed information on crime rates, unemployment figures, poverty rates, educational achievement, and housing cost burdens.
- **State and County Insights**: Easily filter and zoom in on specific states or counties for in-depth analysis.
- **Practical Insights**: Utilize data to identify affordable housing prospects, evaluate community safety, and shape policy initiatives.

## Repository Structure

```
📦 U.S. County SocioInsights
├── 📄 dashboard.py              # Main script to launch the interactive dashboard
├── 📁 data/                     # Data directory
│   └── 📄 final_county_metrics.csv # Final dataset for county-level housing and socioeconomics
├── 📄 requirements.txt          # Required Python packages
├── 📄 .env.example              # Example environment configuration
└── 📄 README.md                 # Project documentation
```

## Getting Started

### Prerequisites

- Python 3.8+
- Git (for cloning the repository)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/us-county-socioinsights.git
cd us-county-socioinsights
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env and add your required configuration
```

5. Prepare your data:
   - Place your `final_county_metrics.csv` file in the `data/` directory
   - Ensure it contains columns for county FIPS, housing data, crime rates, etc.

## Usage

1. Launch the dashboard:
```bash
python dashboard.py
```

2. Accessing the Dashboard:
   - Open a web browser and navigate to assigned local URL (e.g., `http://127.0.0.1:7860`)
   - Use dropdown menus to filter by state, bedroom size, or metric (e.g., "Crime Rate," "Cost Burden")
   - Hover over counties on the map to view detailed metrics, including crime rates and filter based on state.
   
## Sample Output

The interactive dashboard will display:
- A map of U.S. counties with real-time data visualizations
- Charts and plots showing crime rates, housing affordability, and other key socioeconomic factors

## Technical Aspects

- **Frontend**: Developed using Gradio for interactive UI and Plotly for visualizations
- **Backend**: Python, Pandas, and GeoPandas are used for data processing and geospatial analysis
- **Data**: The dashboard utilizes preprocessed data from multiple authoritative sources, combined into the `final_county_metrics.csv` file. County boundary shapefiles are sourced from Census.gov for geographical visualization. Data sources include:
  1. Census.gov for demographic and census data
  2. HUD for Fair Market Rent (FMR) data
  3. SERA for school achievement metrics
  4. BLS for unemployment statistics
  5. Crime data from ICPSR
- **Metrics**: Customized logic to grade crime rates (A-E), housing affordability ratios, and other indicators

## Configuration

Edit `.env` file to customize:
- `DATA_FILE_PATH`: Path to your county data CSV file
- `START_YEAR`: Beginning year for data extraction (default: 2019)
- `END_YEAR`: End year for data extraction (default: current year)

## Contributing

1. Fork the repository
2. Create your feature branch:
```bash
git checkout -b feature/new-feature
```

3. Commit your changes:
```bash
git commit -am 'Add new feature'
```

4. Push to the branch:
```bash
git push origin feature/new-feature
```

5. Submit a pull request

## License

U.S. County SocioInsights is licensed under the MIT License. Refer to LICENSE.md for specifics.

## Acknowledgments

- Special thanks to the U.S. Census Bureau, HUD, and other data sources for providing crucial data
- The project was inspired by the need to address housing affordability and socioeconomic issues in U.S. communities

## Contact Information

For inquiries or collaboration opportunities:
- Contact Nischal Subedi at nis.sub100@gmail.com
- Open an issue in the repository