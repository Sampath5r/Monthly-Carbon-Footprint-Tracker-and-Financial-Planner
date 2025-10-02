import json
import os
import base64
from datetime import datetime, timedelta

# --- Data File Path ---
# This file will store the logged dates for the streak feature
DATA_FILE = 'streak_data.json'

# --- Emission Factors (Sample Data) ---
EMISSION_FACTORS = {
    'electricity_kwh_co2': 0.40,  # kg CO2e per kWh
    'car_km_co2': 0.17,           # kg CO2e per km (average fuel)
    'flight_km_co2': 0.15,        # kg CO2e per km (short/med haul)
    'waste_per_person_co2': 10,   # kg CO2e per month (general waste estimate)
}

# --- Financial Factors (INR) and Benchmarks (Estimates for India) ---
FINANCIAL_FACTORS = {
    'electricity_cost_per_kwh_inr': 8.0, # ₹ per kWh (approximate average)
    'car_cost_per_km_inr': 8.0,          # ₹ per km (approximate cost for fuel and wear)
    # Assumed monthly savings compared to an average omnivorous diet:
    'diet_savings_vegetarian_inr': 1500, # ₹ monthly savings
    'diet_savings_vegan_inr': 2500,      # ₹ monthly savings
    # Eco-Friendly Benchmark Scenario for calculating savings potential:
    'benchmark_kwh': 100,                
    'benchmark_car_km': 100,             
}

# --- Image Utility for Styling ---

def get_base64_image(image_path):
    """Encodes a local image to a base64 string for use in CSS."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        return None

# --- Carbon Footprint Calculation Functions ---

def calculate_energy_footprint(kwh_per_month):
    """Calculates CO2 from home electricity use."""
    return kwh_per_month * EMISSION_FACTORS['electricity_kwh_co2']

def calculate_travel_footprint(car_km_month, flight_km_year):
    """Calculates CO2 from car travel and annual flights."""
    car_co2 = car_km_month * EMISSION_FACTORS['car_km_co2']
    # Divide annual flight CO2 by 12 for monthly calculation
    flight_co2 = (flight_km_year * EMISSION_FACTORS['flight_km_co2']) / 12
    return car_co2 + flight_co2

def calculate_diet_footprint(diet_type, meals_per_month=90):
    """Calculates CO2 from diet based on type."""
    # Factors are simplified estimates based on high/medium/low impact diets
    if diet_type == 'vegan':
        factor = 0.5  
    elif diet_type == 'vegetarian':
        factor = 1.2
    elif diet_type == 'omniverous':
        factor = 2.5
    else: 
        factor = 2.0 # Default for other diets
        
    return meals_per_month * factor

def calculate_total_footprint(energy, travel, diet, waste_reduction_factor=1.0):
    """Sums all components and returns the total and breakdown."""
    waste_co2 = EMISSION_FACTORS['waste_per_person_co2'] * waste_reduction_factor
    total = energy + travel + diet + waste_co2
    
    # Returns a dictionary containing the total and the breakdown by category
    return {
        'Total': total,
        'Energy': energy,
        'Travel': travel,
        'Diet': diet,
        'Waste': waste_co2
    }
    
def calculate_financial_savings(kwh, car_km, diet_type):
    """
    Calculates potential monthly financial savings in INR by comparing user's 
    inputs against an eco-friendly benchmark scenario.
    """
    factors = FINANCIAL_FACTORS
    
    # 1. Energy Savings Calculation
    user_energy_cost = kwh * factors['electricity_cost_per_kwh_inr']
    benchmark_energy_cost = factors['benchmark_kwh'] * factors['electricity_cost_per_kwh_inr']
    # Savings calculated if user's usage is greater than the benchmark
    energy_saving = max(0, user_energy_cost - benchmark_energy_cost)
    
    # 2. Travel Savings Calculation
    user_travel_cost = car_km * factors['car_cost_per_km_inr']
    benchmark_travel_cost = factors['benchmark_car_km'] * factors['car_cost_per_km_inr']
    travel_saving = max(0, user_travel_cost - benchmark_travel_cost)
    
    # 3. Diet Savings (Assumes savings vs. an omnivorous baseline)
    if diet_type == 'vegetarian':
        diet_saving = factors['diet_savings_vegetarian_inr']
    elif diet_type == 'vegan':
        diet_saving = factors['diet_savings_vegan_inr']
    else:
        diet_saving = 0 
        
    total_potential_savings = energy_saving + travel_saving + diet_saving
    
    return {
        'TotalSavings': total_potential_savings,
        'EnergySavings': energy_saving,
        'TravelSavings': travel_saving,
        'DietSavings': diet_saving
    }


# --- Streak Persistence Functions ---

def load_streak_dates():
    """Loads logged dates from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return []
        
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        return sorted(list(set(data.get('logged_dates', []))))
    except (json.JSONDecodeError, KeyError):
        return []

def save_new_log(date_str):
    """Saves a new date string (YYYY-MM-DD) to the JSON file."""
    dates = load_streak_dates()
    if date_str not in dates:
        dates.append(date_str)
        dates.sort() 
    
    with open(DATA_FILE, 'w') as f:
        json.dump({'logged_dates': dates}, f, indent=4)

def calculate_longest_streak(dates_str):
    """Helper function to calculate the longest streak achieved."""
    if not dates_str:
        return 0

    longest_streak = 0
    current_length = 1
    
    unique_dates = sorted(list(set([datetime.strptime(d, '%Y-%m-%d').date() for d in dates_str])))

    for i in range(len(unique_dates) - 1):
        if (unique_dates[i+1] - unique_dates[i]).days == 1:
            current_length += 1
        else:
            longest_streak = max(longest_streak, current_length)
            current_length = 1 
    
    longest_streak = max(longest_streak, current_length)
    
    return longest_streak

def calculate_current_streak():
    """Calculates the current consecutive logging streak."""
    logged_dates_str = load_streak_dates()
    
    if not logged_dates_str:
        return 0, 0 

    all_dates = {datetime.strptime(d, '%Y-%m-%d').date() for d in logged_dates_str}
    
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    current_streak = 0
    check_date = today

    if today in all_dates:
        pass
    elif yesterday in all_dates:
        check_date = yesterday
    else:
        return 0, calculate_longest_streak(logged_dates_str)
        
    while check_date in all_dates:
        current_streak += 1
        check_date -= timedelta(days=1)
        
    longest_streak = calculate_longest_streak(logged_dates_str)

    return current_streak, longest_streak
