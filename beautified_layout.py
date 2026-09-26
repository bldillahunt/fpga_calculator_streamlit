import streamlit as st

# 1. Custom CSS to inject the light background and button colors
st.markdown(
    """
    <style>
    /* 1. Style the main calculator box (Border & Light Background) */
    [data-testid="stVContainer"] > div:has([data-testid="stForm"]), 
    .main-calc-box {
        background-color: #f8f9fa !important; /* Soft, light grey background */
        padding: 20px !important;
        border-radius: 12px !important;
        border: 1px solid #dcdcdc !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
    }

    /* 2. Base style for ALL calculator keypad buttons */
    div[data-testid="stButton"] button {
        background-color: #ffffff !important; /* Clean white for number keys */
        color: #333333 !important;
        border: 1px solid #cccccc !important;
        border-radius: 6px !important;
        font-weight: bold !important;
        transition: all 0.2s ease !important;
    }
    
    /* Hover effect for buttons */
    div[data-testid="stButton"] button:hover {
        background-color: #e9ecef !important;
        border-color: #adb5bd !important;
    }

    /* 3. Style special/operator buttons (/, *, -, +, Enter) */
    /* We can target buttons that contain specific symbols or use Streamlit's primary type */
    div[data-testid="stButton"] button[pck="primary"] {
        background-color: #4ea8de !important; /* Beautiful accent blue for Enter */
        color: white !important;
        border: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 2. Outer layout columns to restrict the width (keeping your perfect layout)
left_pad, main_col, right_pad = st.columns([1.5, 7.0, 1.5])

with main_col:
    # 3. Create the bounded container for the calculator
    # Wrapping it in a div with our custom class applies the background color perfectly
    st.markdown('<div class="main-calc-box">', unsafe_allow_html=True)
    
    # --- YOUR EXISTING LAYOUT GOES HERE ---
    st.markdown("### Input Window")
    user_input = st.text_input("Input", label_visibility="collapsed", value="16")
    
    st.markdown("### Output")
    st.text_input("Output", value="Result...", label_visibility="collapsed")
    
    # --- Example Keypad Grid showing the color logic ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.button("7")  # Standard button (White)
    with col2:
        st.button("8")  # Standard button (White)
    with col3:
        st.button("9")  # Standard button (White)
    with col4:
        st.button("/", type="secondary") # Operator button
        
    # Bottom row example with a highlighted execution button
    b_col1, b_col2, b_col3, b_col4 = st.columns(4)
    with b_col1:
        st.button("0")
    with b_col2:
        st.button(".")
    with b_col3:
        # Using type="primary" tells our CSS block to color this button Blue
        st.button("Enter", type="primary") 
    with b_col4:
        st.button("+")
        
    st.markdown('</div>', unsafe_allow_html=True)
