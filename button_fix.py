# 4. Calculator Buttons Layout & Event Handling
st.markdown("### Keypad")

# Custom CSS to force the buttons into small, uniform squares instead of wide bars
st.markdown("""
    <style>
    div[data-testid="stColumn"] button {
        max-width: 60px !important;
        height: 50px !important;
        font-family: monospace !important;
        font-size: 16px !important;
        margin: 0 auto !important;
        display: block !important;
    }
    </style>
""", unsafe_allow_html=True)

buttons = [
    ('7', '8', '9', '/'),
    ('4', '5', '6', '*'),
    ('1', '2', '3', '-'),
    ('0', '.', 'R', '+'),
    ('A', 'B', 'C', 'D'),
    ('E', 'F', 'Enter', '=')
]

# Track button pushes
button_push_result = None

# Using an inner column block to squeeze the calculator layout tight
_, center_pad, _ = st.columns([1, 2, 1]) 

with center_pad:
    for row in buttons:
        cols = st.columns(4)
        for i, val in enumerate(row):
            if cols[i].button(val, use_container_width=True):
                button_push_result = val
