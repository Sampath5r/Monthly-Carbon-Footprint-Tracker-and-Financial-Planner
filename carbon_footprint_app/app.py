import streamlit as st
import random
from datetime import datetime
# Import all functions and constants from the utility file
from functions import (
    get_base64_image, 
    load_streak_dates, 
    save_new_log, 
    calculate_current_streak, 
    calculate_energy_footprint, 
    calculate_travel_footprint, 
    calculate_diet_footprint, 
    calculate_total_footprint,
    calculate_financial_savings
)

# --- A. Custom Styling and Theme Overrides (Including Background Image) ---

def apply_custom_style():
    """Injects custom CSS for background, font, and button styling."""
    
    # Load the background image using the utility function
    b64_image = get_base64_image("carbonreduction1.jpg")
    
    # Initialize background CSS property string with fallback color
    background_css = "background-color: #121212;"
    
    if b64_image:
        # CONSOLIDATED FIX: Use the specific background properties for max compatibility
        background_css = f"""
        background: url("data:image/jpg;base64,{b64_image}") no-repeat center center fixed; 
        background-size: cover;
        background-color: #121212; /* Fallback/Blend color */
        """
    
    # Use the data-testid selector for the most reliable background application
    # and ensure the main content area is transparent
    background_style = f"""
    [data-testid="stAppViewContainer"] {{
        {background_css}
    }}
    /* Ensure the main page content also allows the background to show through */
    .main {{
        background: none !important;
    }}
    """

    font_css = """
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    
    html, body, [class*="stApp"], .main {
        font-family: 'Roboto', sans-serif !important;
    }
    """
    
    # Merging all CSS styles
    style_css = f"""
    <style>
    {font_css}

    /* BACKGROUND FIX: Targeting the main Streamlit container for max reliability */
    {background_style}

    /* General App Container Styling */
    .stApp {{
        color: white; /* Ensures text is readable against the dark background */
    }}
    
    /* Removes the default background from main Streamlit blocks */
    .main .block-container {{
        background: none; 
    }}
    
    /* Style for the 'Next Fact' button */
    .next-fact-container button {{
        background-color: #2D2D2D; /* Dark Gray */
        color: #4CAF50; /* Green text */
        border: 2px solid #4CAF50;
        border-radius: 8px;
        padding: 5px 15px;
        transition: all 0.2s;
    }}
    .next-fact-container button:hover {{
        background-color: #4CAF50;
        color: #FFFFFF;
    }}
    /* Style for the Log Action button and Calculate button */
    .log-action-button button, .calculate-button button {{
        background-color: #4CAF50; 
        color: white;
        font-size: 16px;
        padding: 10px 20px;
        border-radius: 20px;
        box-shadow: 0 4px #2E7D32;
        transition: all 0.2s;
        width: 100%;
    }}
    .log-action-button button:active, .calculate-button button:active {{
        box-shadow: 0 1px #2E7D32;
        transform: translateY(3px);
    }}
    </style>
    """
    
    # Applying the styles
    st.markdown(style_css, unsafe_allow_html=True)

# Apply styles before anything else
apply_custom_style()


# --- B. DYNAMIC FACT LOGIC ---

FACTS = [
    "Switching to a plant-based diet can cut your food-related emissions by up to 73%.", 
    "Air travel is one of the fastest-growing sources of greenhouse gas emissions.",
    "The average person's annual footprint varies drastically, from 0.5 to over 30 tons of $\\text{CO}_2$e.",
    "Turning down your thermostat by just $1$ degree $\\text{C}$ can reduce your heating bill (and emissions) by up to 10%.",
    "Globally, food waste accounts for about 8% of all greenhouse gas emissions.",
    "Repairing electronics instead of replacing them saves around 40 $\\text{kg}$ of $\\text{CO}_2$ per device.",
    "Choosing public transport or cycling over driving for a 10 $\\text{km}$ commute saves about 1.7 $\\text{kg}$ of $\\text{CO}_2$ daily.",
    "Recycling one aluminum can saves enough energy to run a TV for three hours.",
]

if 'current_fact' not in st.session_state:
    st.session_state['current_fact'] = random.choice(FACTS)

# Initialize calculation results storage
if 'footprint_result' not in st.session_state:
    st.session_state['footprint_result'] = None
    
# Initialize financial savings storage
if 'financial_savings' not in st.session_state:
    st.session_state['financial_savings'] = None


def get_next_fact():
    """Selects a new fact, ensuring it is different from the current one."""
    new_fact = random.choice(FACTS)
    # Simple loop to ensure a change
    while new_fact == st.session_state['current_fact']:
        new_fact = random.choice(FACTS)
    st.session_state['current_fact'] = new_fact


# --- C. STREAK LOGIC (Streamlit specific handlers) ---

def log_action():
    """Logs today's date using the utility function and forces a rerun."""
    today_str = datetime.now().strftime('%Y-%m-%d')
    save_new_log(today_str) # Calls the persistence function from functions.py
    st.rerun() 

# --- D. CARBON FOOTPRINT CALCULATION HANDLER ---

def handle_calculation(kwh, car_km, flight_km, diet, recycle):
    """Calculates the footprint, financial savings, and stores the results."""
    
    # 1. Calculate component footprints
    energy_co2 = calculate_energy_footprint(kwh)
    travel_co2 = calculate_travel_footprint(car_km, flight_km)
    diet_co2 = calculate_diet_footprint(diet)

    # 2. Apply waste reduction factor
    waste_factor = 0.8 if recycle else 1.0 # 20% reduction if user recycles
    
    # 3. Calculate CO2 total and breakdown
    co2_result = calculate_total_footprint(energy_co2, travel_co2, diet_co2, waste_factor)
    st.session_state['footprint_result'] = co2_result
    
    # 4. Calculate Financial Savings
    savings_result = calculate_financial_savings(kwh, car_km, diet)
    st.session_state['financial_savings'] = savings_result
    

# --- E. APP LAYOUT ---

st.title("🌱 My Monthly Carbon Footprint App")
st.markdown("---")

# 1. Did You Know Section
st.header("💡 Did You Know?")
col_fact, col_button = st.columns([4, 1])

with col_fact:
    st.info(st.session_state['current_fact'])
    
with col_button:
    st.markdown('<div class="next-fact-container">', unsafe_allow_html=True)
    st.button("Next Fact", on_click=get_next_fact, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# 2. Measures to Reduce Carbon Footprint
st.header("📉 Key Reduction Measures")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Energy")
    st.markdown("- Switch to a **green energy** supplier.")
    st.markdown("- Lower your heating/AC thermostat by **$1$ degree $\\text{C}$**.")
with col2:
    st.subheader("Travel")
    st.markdown("- Choose a train over flying for distances under **$1000 \text{km}$**.")
    st.markdown("- Take public transport or **carpool** daily.")
with col3:
    st.subheader("Diet & Waste")
    st.markdown("- Have **one meat-free day** per week.")
    st.markdown("- Always **recycle** plastic, paper, and glass.")

st.markdown("---")

# 3. STREAK TRACKER SECTION
st.header("🔥 Daily Action Streak")

# Calculate streaks using the function from functions.py
current_streak, longest_streak = calculate_current_streak()

# Display the streak metrics
st.metric(label="Current Streak", value=f"{current_streak} days", delta=f"Longest: {longest_streak} days")

# Log button logic
today_str = datetime.now().strftime('%Y-%m-%d')
logged_dates = load_streak_dates() 

st.markdown('<div class="log-action-button">', unsafe_allow_html=True)
if today_str in logged_dates:
    st.button("✅ Logged Today!", disabled=True, use_container_width=True)
else:
    st.button("🔥 Log Today's Action", on_click=log_action, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---") 

# 4. CARBON FOOTPRINT CALCULATOR INPUTS
st.header("💡 Carbon Footprint Calculator")
st.markdown("Estimate your monthly $\\text{CO}_2$ emissions in $\\text{kg}$ $\\text{CO}_2$e.")

with st.form("carbon_calculator_form"):
    st.subheader("Energy & Travel Inputs")
    col_a, col_b = st.columns(2)
    
    with col_a:
        kwh = st.number_input(
            "Monthly Electricity Consumption ($\text{kWh}$)", 
            min_value=0, value=250, step=10, key="kwh"
        )
        car_km = st.number_input(
            "Monthly Car Travel ($\text{km}$)", 
            min_value=0, value=500, step=10, key="car_km"
        )

    with col_b:
        diet = st.selectbox(
            "Primary Diet Type",
            options=['omniverous', 'vegetarian', 'vegan', 'other'],
            index=0, key="diet_type"
        )
        flight_km = st.number_input(
            "Annual Flight Distance ($\text{km}$)", 
            min_value=0, value=1000, step=100, key="flight_km"
        )
        
    recycle = st.checkbox("I actively and consistently recycle household waste (reduces estimated waste footprint by 20%).", value=True)
    
    st.markdown('<div class="calculate-button">', unsafe_allow_html=True)
    submitted = st.form_submit_button("Calculate Footprint & Savings")
    st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        handle_calculation(kwh, car_km, flight_km, diet, recycle)


# 5. RESULTS DISPLAY (CO2)
if st.session_state['footprint_result']:
    co2_result = st.session_state['footprint_result']
    total_co2 = co2_result['Total']
    
    st.subheader("Your Monthly Footprint Estimate")
    
    st.success(f"Your estimated total monthly carbon footprint is **{total_co2:,.2f} $\\text{{kg}} \\text{{CO}}_2\\text{{e}}$**.")
    
    st.markdown("---")
    # 6. FINANCIAL SAVINGS DISPLAY
    if st.session_state['financial_savings']:
        st.markdown("<br>", unsafe_allow_html=True)
        st.header("💰 Potential Monthly Savings (INR)")
        
        savings_result = st.session_state['financial_savings']
        total_savings = savings_result['TotalSavings']
        
        st.info(f"By optimizing your habits toward the eco-friendly benchmark, you could potentially save **₹{total_savings:,.0f}** per month!")

        st.markdown("---")
        st.subheader("Savings Breakdown")
        
        col_se, col_st, col_sd, col_placeholder = st.columns(4)
        
        # Displaying savings metrics
        col_se.metric("Energy Savings", f"₹{savings_result['EnergySavings']:,.0f}")
        col_st.metric("Travel Savings", f"₹{savings_result['TravelSavings']:,.0f}")
        col_sd.metric("Diet Savings", f"₹{savings_result['DietSavings']:,.0f}")
