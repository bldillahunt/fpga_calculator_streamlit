import streamlit as st

# 1. Inject custom CSS for the mobile keypad
st.html("""
<style>
div[data-testid="stVScrollBlock"]:has(div[class*="st-key-keypad_row"]) {
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 8px !important;
}
div[class*="st-key-keypad_row"] > div[data-testid="column"] {
    width: 25% !important;
    flex: 1 1 0% !important;
    min-width: 0px !important;
}
div[class*="st-key-keypad_row"] button {
    width: 100% !important;
    padding: 12px 0px !important;
}
</style>
""")

st.title("Adaptive Calculator Layout")

if "calc_input" not in st.session_state:
    st.session_state.calc_input = ""

# Display field
st.text_input("Result", value=st.session_state.calc_input, disabled=False)

# 2. Add the toggle switch
use_keypad = st.checkbox("Enable Mobile Keypad", value=False)

# Helper function to evaluate the math
def evaluate_expression():
    try:
        # Note: eval is used here for simplicity; consider a safer parser for production
        st.session_state.calc_input = str(eval(st.session_state.calc_input))
    except:
        st.session_state.calc_input = "Error"

# 3. Conditional Layout Logic
if use_keypad:
    # --- MOBILE KEYPAD MODE ---
    buttons = [
        ["7", "8", "9", "/"],
        ["4", "5", "6", "*"],
        ["1", "2", "3", "-"],
        ["C", "0", "=", "+"]
    ]

    for row_idx, row in enumerate(buttons):
        with st.container(key=f"keypad_row_{row_idx}"):
            cols = st.columns(4)
            for col_idx, button_label in enumerate(row):
                with cols[col_idx]:
                    if st.button(button_label, key=f"btn_{row_idx}_{col_idx}"):
                        if button_label == "C":
                            st.session_state.calc_input = ""
                        elif button_label == "=":
                            evaluate_expression()
                        else:
                            st.session_state.calc_input += button_label
                        st.rerun()
else:
    # --- PC MODE (Just Reset and Enter) ---
    st.write("?? Use your physical keyboard to type in the field above.")
    
    # Place Reset and Enter side-by-side
    pc_cols = st.columns(2)
    
    with pc_cols[0]:
        if st.button("Reset", type="secondary", use_container_width=True):
            st.session_state.calc_input = ""
            st.rerun()
            
    with pc_cols[1]:
        if st.button("Enter", type="primary", use_container_width=True):
            evaluate_expression()
            st.rerun()
