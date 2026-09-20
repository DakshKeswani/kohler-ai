import streamlit as st
import os
import base64
from catalog import KOHLER_INVENTORY
from engine import BathroomOptimizationEngine
from visualizer import generate_2d_floorplan

# -----------------------------------------------------------------------------
# 1. PAGE SETUP & KOHLER DARK LUXURY AESTHETIC
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="KOHLER Studio AI | Spatial Atelier",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

KOHLER_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
    }

    .stApp {
        background-color: #0E1013 !important;
        color: #E2E4E9 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #14171C !important;
        border-right: 1px solid rgba(200, 169, 126, 0.2) !important;
    }

    h1, h2, h3, h4, h5, h6, 
    [data-testid="stHeader"] *, 
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        letter-spacing: 1.2px;
    }
    
    .stCaption, p[data-testid="stCaptionContainer"] {
        color: #A0A5B5 !important;
    }

    .gold-label {
        color: #C8A97E !important;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }

    .luxury-card {
        background: #181C23 !important;
        border: 1px solid rgba(200, 169, 126, 0.28) !important;
        border-radius: 6px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .luxury-card:hover {
        border-color: #C8A97E !important;
    }

    .badge-pvd {
        display: inline-block;
        background-color: rgba(200, 169, 126, 0.12) !important;
        color: #E2CA9E !important;
        border: 1px solid #C8A97E !important;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-right: 6px;
    }

    div.stButton > button {
        background-color: #C8A97E !important;
        color: #0E1013 !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 10px 22px !important;
    }
    div.stButton > button:hover {
        background-color: #DFC59B !important;
        color: #000000 !important;
    }
</style>
"""
st.markdown(KOHLER_CSS, unsafe_allow_html=True)

def get_base64_image(image_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base_dir, 'assets', image_name)
    try:
        with open(img_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""

# -----------------------------------------------------------------------------
# 2. SIDEBAR CONFIGURATION
# -----------------------------------------------------------------------------
st.markdown('<p class="gold-label">KOHLER INDIA AI LABS</p>', unsafe_allow_html=True)
st.title("Atelier Intelligent: Architectural Bathroom Planner")
st.caption("Combinatorial Constraint Engine • Whole-Home Palette Harmonization • Vastu Spatial Routing")

with st.sidebar:
    st.markdown('<p class="gold-label">DIMENSIONAL CONSTRAINTS</p>', unsafe_allow_html=True)
    length = st.slider("Room Length (ft)", 7.0, 25.0, 10.5, 0.5)
    width = st.slider("Room Width (ft)", 5.0, 20.0, 8.0, 0.5)
    budget = st.number_input("Target Budget Envelope (₹)", min_value=50000, value=450000, step=25000)

    st.markdown("---")
    st.markdown('<p class="gold-label">AESTHETIC & HARMONIZATION</p>', unsafe_allow_html=True)
    house_palette = st.selectbox(
        "Whole-House Palette",
        ["Japandi & Warm Earth Tones", "Modern Obsidian & Industrial Slate", "Neo-Classical Parisian Luxury"]
    )
    theme = st.selectbox(
        "Kohler Style Direction",
        ["Minimalist Modern", "Classic Luxury", "Japanese Zen"]
    )

    st.markdown("---")
    st.markdown('<p class="gold-label">SPATIAL ORIENTATION (VASTU)</p>', unsafe_allow_html=True)
    vastu_toggle = st.checkbox("Enable Vastu Shastra Spatial Routing", value=True)
    entrance = st.selectbox("Bathroom Entrance Direction", ["South", "North", "East", "West"])

    st.markdown("---")
    if st.button("Generate Atelier Plans", use_container_width=True):
        engine = BathroomOptimizationEngine(
            length=length, width=width, budget=budget,
            aesthetic_theme=theme, home_palette=house_palette,
            vastu_enabled=vastu_toggle, entrance_dir=entrance
        )
        with st.spinner("Calculating combinatorial spatial constraints..."):
            st.session_state["plans"] = engine.solve()
            st.session_state["budget"] = budget
            st.session_state["params"] = {
                "length": length,
                "width": width,
                "vastu": vastu_toggle,
                "entrance": entrance,
                "palette": house_palette
            }

# -----------------------------------------------------------------------------
# 3. INTERACTIVE 3-STEP CONSULTATION FLOW
# -----------------------------------------------------------------------------
if "plans" in st.session_state and st.session_state["plans"]:
    plans = st.session_state["plans"]
    params = st.session_state["params"]
    user_budget = st.session_state["budget"]

    # STEP 1: PLAN EXPLORATION & SELECTION
    st.markdown('<p class="gold-label">STEP 1: INSPECT & SELECT BASE PLAN</p>', unsafe_allow_html=True)
    
    plan_names = [f"Plan {chr(65+i)} (₹{p['total_cost']:,.0f})" for i, p in enumerate(plans)]
    selected_plan_str = st.radio(
        "Choose your preferred layout package to proceed with customization:",
        options=plan_names,
        horizontal=True
    )
    selected_idx = plan_names.index(selected_plan_str)
    selected_plan = plans[selected_idx]

    # Inspection View of the Selected Plan
    col_left, col_right = st.columns([1.1, 0.9], gap="large")

    with col_left:
        st.markdown(f"##### Curated Package: **{selected_plan_str}**")
        
        for item in selected_plan["items"]:
            img_filename = item.get("img_file", f"{item['category']}.png")
            img_b64 = get_base64_image(img_filename)
            img_tag = f'<img src="data:image/png;base64,{img_b64}" style="max-width: 80px; max-height: 80px; object-fit: contain;" />' if img_b64 else ""

            st.markdown(f"""
            <div class="luxury-card" style="display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1;">
                    <div style="display: flex; justify-content: space-between; margin-right: 15px;">
                        <span style="font-weight: 600; color: #FFFFFF; font-size: 0.98rem;">{item['name']}</span>
                        <span style="color: #C8A97E; font-weight: 600;">₹{item['price']:,.0f}</span>
                    </div>
                    <p style="color: #8C92AC; font-size: 0.78rem; margin: 3px 0 8px 0;">SKU: {item['sku']} | Footprint: {item['w']}' × {item['d']}'</p>
                    <span class="badge-pvd">{item['finish']}</span>
                </div>
                <div style="width: 85px; text-align: center;">{img_tag}</div>
            </div>
            """, unsafe_allow_html=True)

        m1, m2 = st.columns(2)
        m1.metric("Base Package Cost", f"₹{selected_plan['total_cost']:,.0f}")
        m2.metric("Aesthetic Fidelity", f"{round(selected_plan['score'] * 100)} / 100")

    with col_right:
        st.markdown('<p class="gold-label">ARCHITECTURAL SCHEMATIC</p>', unsafe_allow_html=True)
        fig = generate_2d_floorplan(
            params["length"], params["width"], selected_plan["items"], 
            params["vastu"], params["entrance"]
        )
        st.pyplot(fig, use_container_width=True)

    # STEP 2: ACCESSORIES & ADD-ONS (No remaining budget shown yet!)
    st.markdown("---")
    st.markdown('<p class="gold-label">STEP 2: CURATE LUXURY ADD-ONS (OPTIONAL)</p>', unsafe_allow_html=True)
    
    plan_remaining_allowance = user_budget - selected_plan["total_cost"]

    # Filter accessories that could physically fit in the envelope
    eligible_accessories = [
        acc for acc in KOHLER_INVENTORY 
        if acc["category"] == "accessory" and acc["price"] <= plan_remaining_allowance
    ]
    
    selected_addons = []
    addon_cost = 0

    if eligible_accessories:
        st.markdown("<p style='color: #A0A5B5; font-size: 0.9rem; margin-bottom: 20px;'>Select finishing touches to include in your final specification:</p>", unsafe_allow_html=True)
        
        checkbox_states = {}
        
        # Build a visual product card for each accessory
        for acc in eligible_accessories:
            # Create a 3-column layout: Image (small), Text (wide), Checkbox (small)
            c_img, c_text, c_box = st.columns([1, 6, 1.5], gap="small")
            
            with c_img:
                img_file = acc.get("img_file", "accessory.png")
                b64 = get_base64_image(img_file)
                if b64:
                    st.markdown(f'<img src="data:image/png;base64,{b64}" style="width: 100%; max-width: 60px; object-fit: contain; padding: 4px; background: rgba(255,255,255,0.05); border-radius: 4px;" />', unsafe_allow_html=True)
            
            with c_text:
                st.markdown(f"""
                <div style='line-height: 1.3;'>
                    <strong style='color: #FFFFFF; font-size: 0.95rem; letter-spacing: 0.5px;'>{acc['name']}</strong> 
                    <span style='color: #C8A97E; font-weight: 600; font-size: 0.95rem; margin-left: 5px;'>(+₹{acc['price']:,.0f})</span><br>
                    <span style='color: #8C92AC; font-size: 0.8rem;'>{acc['desc']}</span>
                </div>
                """, unsafe_allow_html=True)
                
            with c_box:
                key = f"acc_{selected_idx}_{acc['sku']}"
                checkbox_states[acc["sku"]] = st.checkbox("Add to Cart", key=key)
                
            st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True) # Spacing between rows
            
        st.markdown("<br>", unsafe_allow_html=True)
        skip_addons = st.checkbox("🚫 Skip Add-ons (Proceed directly with base package)", value=False, key=f"skip_{selected_idx}")
        
        if not skip_addons:
            for acc in eligible_accessories:
                if checkbox_states[acc["sku"]]:
                    selected_addons.append(acc)
                    
            addon_cost = sum(a["price"] for a in selected_addons)

            if addon_cost > plan_remaining_allowance:
                st.error("⚠️ Selected add-ons exceed the targeted budget limit. Please uncheck an item.")
    else:
        st.info("The base plan fully maximizes your targeted budget. No additional add-ons available.")
        skip_addons = True

    # STEP 3: FINAL SPECIFICATION & REMAINING ENVELOPE (Revealed ONLY here)
    st.markdown("---")
    st.markdown('<p class="gold-label">STEP 3: FINAL ATELIER SPECIFICATION & BALANCE</p>', unsafe_allow_html=True)
    
    final_investment = selected_plan["total_cost"] + addon_cost
    final_remaining = user_budget - final_investment

    summary_box = f"""
    <div style="background: #14171C; border: 1px solid rgba(200, 169, 126, 0.4); border-radius: 8px; padding: 22px;">
        <h4 style="margin: 0 0 10px 0; color: #FFFFFF;">Selected: {selected_plan_str.split(' (')[0]} Suite</h4>
        <p style="color: #A0A5B5; font-size: 0.88rem; margin-bottom: 15px;">
            Harmonized with <strong>{params['palette']}</strong> &bull; Vastu Orientation: <strong>{'Compliant' if params['vastu'] else 'Standard'}</strong>
        </p>
        <hr style="border: 0; border-top: 1px solid rgba(200, 169, 126, 0.2); margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between; font-size: 0.95rem; margin-bottom: 6px;">
            <span style="color: #C5CAD5;">Core Fixtures ({len(selected_plan['items'])} items):</span>
            <span style="color: #FFFFFF; font-weight: 600;">₹{selected_plan['total_cost']:,.0f}</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.95rem; margin-bottom: 6px;">
            <span style="color: #C5CAD5;">Add-on Accessories ({len(selected_addons)} items):</span>
            <span style="color: #FFFFFF; font-weight: 600;">₹{addon_cost:,.0f}</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 1.15rem; font-weight: 700; margin-top: 12px; padding-top: 10px; border-top: 1px solid rgba(200, 169, 126, 0.3);">
            <span style="color: #C8A97E;">Total Investment:</span>
            <span style="color: #C8A97E;">₹{final_investment:,.0f}</span>
        </div>
    </div>
    """
    st.markdown(summary_box, unsafe_allow_html=True)

    # The Remaining Envelope is displayed ONLY at this point
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Final Investment", f"₹{final_investment:,.0f}")
    c2.metric("Remaining Envelope", f"₹{final_remaining:,.0f}", help="Unallocated funds from your target budget limit.")
    c3.metric("Floor Spatial Occupancy", f"{round(selected_plan['footprint_ratio'] * 100)}%", help="ADA clearance threshold: < 40%")

elif "plans" in st.session_state and not st.session_state["plans"]:
    st.error("⚠️ Optimization Failed: No valid Kohler ensemble fits the specified budget and physical dimensions. Please increase your budget or room size.")