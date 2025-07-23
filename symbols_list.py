import refinitiv.data as rd
import pandas as pd
from datetime import timedelta
import os

ric_list = []
for filename in os.listdir("archive"):
    ric_list.append(filename[:filename.find(".")])

def get_roe_and_asset_growth_data_by_date(symbol, start_date, end_date):
    try:
        working_symbol = f"{symbol}.O"
        
        # Get baseline data for asset growth calculation
        baseline_result = rd.get_data(
            universe=working_symbol,
            fields=["TR.TotalAssets", "TR.ROEActValue.date"],
            parameters={"Period": "FQ0:FQ-31", "Frq": "FQ", "Curn": "USD"}
        )
        
        # Get main quarterly data
        result = rd.get_data(
            universe=working_symbol,
            fields=["TR.ROEActValue", "TR.ROEActValue.date", "TR.TotalAssets"],
            parameters={"Period": "FQ0:FQ-27", "Frq": "FQ", "Curn": "USD"}
        )
    except:
        working_symbol = f"{symbol}.N"
        
        # Get baseline data for asset growth calculation
        baseline_result = rd.get_data(
            universe=working_symbol,
            fields=["TR.TotalAssets", "TR.ROEActValue.date"],
            parameters={"Period": "FQ0:FQ-31", "Frq": "FQ", "Curn": "USD"}
        )
        
        # Get main quarterly data
        result = rd.get_data(
            universe=working_symbol,
            fields=["TR.ROEActValue", "TR.ROEActValue.date", "TR.TotalAssets"],
            parameters={"Period": "FQ0:FQ-27", "Frq": "FQ", "Curn": "USD"}
        )
    
    baseline_assets_value = None
    if baseline_result is not None and not baseline_result.empty:
        baseline_df = baseline_result.loc[:, ~baseline_result.columns.duplicated()]
        date_col = next((col for col in baseline_df.columns if 'date' in col.lower()), None)
        assets_col = next((col for col in ['Total Assets', 'TR.TotalAssets'] if col in baseline_df.columns), None)
        
        if date_col and assets_col:
            baseline_df['Date'] = pd.to_datetime(baseline_df[date_col], errors='coerce')
            baseline_df = baseline_df.dropna(subset=['Date']).sort_values('Date')
            baseline_data = baseline_df[baseline_df['Date'] < pd.to_datetime(start_date)]
            if not baseline_data.empty:
                baseline_assets_value = pd.to_numeric(baseline_data[assets_col].iloc[-1], errors='coerce')
    
    if result is None or result.empty:
        return pd.DataFrame()
    
    df = result.loc[:, ~result.columns.duplicated()]
    date_col = next((col for col in df.columns if 'date' in col.lower()), None)
    
    if date_col is None:
        return pd.DataFrame()
    
    df['Date'] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=['Date'])
    df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]
    
    if df.empty:
        return pd.DataFrame()
    
    df = df.sort_values('Date').reset_index(drop=True)
    
    roe_col = next((col for col in ['TR.ROEActValue', 'Return On Equity - Actual'] if col in df.columns), None)
    assets_col = next((col for col in ['TR.TotalAssets', 'Total Assets'] if col in df.columns), None)
    
    asset_growth_rates = []
    if assets_col:
        df[assets_col] = pd.to_numeric(df[assets_col], errors='coerce')
        
        for i in range(len(df)):
            if i == 0:
                current_assets = df[assets_col].iloc[i]
                if (baseline_assets_value and pd.notna(current_assets) and baseline_assets_value != 0):
                    growth_rate = ((current_assets - baseline_assets_value) / baseline_assets_value) * 100
                    asset_growth_rates.append(round(growth_rate, 2))
                else:
                    asset_growth_rates.append(0.0)
            else:
                current_assets = df[assets_col].iloc[i]
                previous_assets = df[assets_col].iloc[i-1]
                
                if pd.notna(current_assets) and pd.notna(previous_assets) and previous_assets != 0:
                    growth_rate = ((current_assets - previous_assets) / previous_assets) * 100
                    asset_growth_rates.append(round(growth_rate, 2))
                else:
                    asset_growth_rates.append(0.0)
    else:
        asset_growth_rates = [0.0] * len(df)
    
    quarterly_df = pd.DataFrame({
        'Symbol': symbol,
        'Date': df['Date'].dt.date,
        'ROE_Percent': pd.to_numeric(df[roe_col], errors='coerce').fillna(0).round(2) if roe_col else 0,
        'Asset_Growth_Rate_Percent': asset_growth_rates
    })
    
    # Check if company has at least 15 data points BEFORE expansion
    if len(quarterly_df) < 15:
        return pd.DataFrame()
    
    expanded_data = []
    for i in range(len(quarterly_df)):
        expanded_data.append(quarterly_df.iloc[i].copy())
        
        if i < len(quarterly_df) - 1:
            next_quarter_date = pd.to_datetime(quarterly_df.iloc[i + 1]['Date'])
            one_day_before_next = (next_quarter_date - timedelta(days=1)).date()
            
            row_copy = quarterly_df.iloc[i].copy()
            row_copy['Date'] = one_day_before_next
            expanded_data.append(row_copy)
    
    return pd.DataFrame(expanded_data).reset_index(drop=True)

def remove_zero_growth_companies(data):
    """
    Remove the first two rows for any company where both have 0% asset growth rate
    """
    if data.empty:
        return data
    
    companies_to_filter = []
    
    # Group by symbol and check first two rows
    for symbol in data['Symbol'].unique():
        company_data = data[data['Symbol'] == symbol].reset_index(drop=True)
        
        # Check if company has at least 2 rows and both have 0% asset growth
        if (len(company_data) >= 2 and 
            company_data.iloc[0]['Asset_Growth_Rate_Percent'] == 0.0 and 
            company_data.iloc[1]['Asset_Growth_Rate_Percent'] == 0.0):
            companies_to_filter.append(symbol)
    
    # Remove first two rows for identified companies
    filtered_data = []
    for symbol in data['Symbol'].unique():
        company_data = data[data['Symbol'] == symbol].reset_index(drop=True)
        
        if symbol in companies_to_filter:
            # Skip first two rows
            if len(company_data) > 2:
                filtered_data.append(company_data.iloc[2:])
            # If company has only 2 rows or less, skip entirely
        else:
            # Keep all rows for this company
            filtered_data.append(company_data)
    
    return pd.concat(filtered_data, ignore_index=True) if filtered_data else pd.DataFrame()

def get_multiple_companies_roe_and_assets(symbols, start_date, end_date):
    rd.open_session("platform.ldp")
    all_data = []
    companies_processed = 0
    companies_included = 0
    
    for i, symbol in enumerate(symbols, 1):
        companies_processed += 1
        df = get_roe_and_asset_growth_data_by_date(symbol, start_date, end_date)
        if not df.empty:
            all_data.append(df)
            companies_included += 1
    
    rd.close_session()
    combined_data = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
    
    # Apply the filtering logic
    if not combined_data.empty:
        combined_data = remove_zero_growth_companies(combined_data)
    
    return combined_data

# Execute
start_date = "2019-07-01"
end_date = "2025-07-01"
symbols = ric_list

data = get_multiple_companies_roe_and_assets(symbols, start_date, end_date)

if not data.empty:
    company_counts = data['Symbol'].value_counts().sort_index()
    data.to_csv('roe_asset_data.csv', index=False)
    print(f"\nData saved to 'roe_asset_data.csv'")
else:
    print("No data retrieved")