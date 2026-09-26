# Detect if the value inside the input window changed (user typed/pasted and hit Enter)
with st.container(border=True):
    label_col1, widget_col1 = st.columns([1, 4], vertical_alignment="center")

    with label_col1:
        st.write("Input ")

    with widget_col1:
        typed_input = st.text_input(
            "xxx", 
            value=st.session_state.main_display_var, 
            key="input_win",
            label_visibility="collapsed"
        )

    label_col2, widget_col2 = st.columns([1, 4], vertical_alignment="center")

    with label_col2:
        st.write("Output ")

    with widget_col2:
        st.code(st.session_state.aux_display_var, language="text")		

    # ---------------------------------------------------------
    # 2. Configuration Panel (Bit Widths)
    # ---------------------------------------------------------
    col1, col2 = st.columns(2)
    with col1:
        int_bits = int(st.text_input("Integer Bits:", value=16))
    with col2:
        frac_bits = int(st.text_input("Fraction Bits:", value=16))

    # ---------------------------------------------------------
    # 3. Format Selectors
    # ---------------------------------------------------------
    f_col1, f_col2 = st.columns(2)

    with f_col1:
        st.caption("Input Format")
        input_mode = st.radio(
            "In Mode", 
            options=MODES, 
            format_func=lambda x: x[0],  
            label_visibility="collapsed"
        )

    with f_col2:
        st.caption("Output Format")
        output_mode = st.radio(
            "Out Mode", 
            options=MODES, 
            format_func=lambda x: x[0],  
            label_visibility="collapsed"
        )

    # ---------------------------------------------------------
    # 4. Calculator Buttons Layout & Event Handling
    # ---------------------------------------------------------
    buttons = [
        ('Reset', 'Enter')
    ]

    button_pressed = None

    # Build rows horizontally inside the centered container tracking layout
    for row in buttons:
        cols = st.columns(2) 
        for i, val in enumerate(row):
            with cols[i]:
                if st.button(val, key=f"btn_{val}_{i}", use_container_width=True):
                    button_pressed = val

# =========================================================
# THE CRITICAL STRUCTURAL FIX: 
# Evaluate button loops and inputs in the correct execution order
# =========================================================
keyboard_enter_pressed = False

if typed_input != st.session_state.main_display_var:
    st.session_state.main_display_var = typed_input
    keyboard_enter_pressed = True

# Explicitly link your button press assignment here
button_push_result = button_pressed 

if button_push_result or keyboard_enter_pressed:
 
    if keyboard_enter_pressed and not button_push_result:
        button_push_result = 'Enter'

    # The 'R' routing logic now triggers cleanly because button_push_result is captured
    if button_push_result == 'Reset':
        st.session_state.main_display_var = ""
        st.session_state.aux_display_var = ""
        if "input_win" in st.session_state:
            st.session_state.input_win = ""
        st.rerun()
        
    elif button_push_result in ('Enter'):
        # Parse inputs
        operand1, operand2, operator = get_operands()
        
        operand1_data_error = False
        operand2_data_error = False
        operator_error = False
        
        nibble_size = int_bits // 4
        operand2_present = True if operand2 != "" else False
        
        # Validation Pipeline based on Input Format
        if input_mode[1] == "REAL":
            operand1_data_error = verify_real_input(operand1)
            if operand2_present:
                operand2_data_error = verify_real_input(operand2)
                
        elif input_mode[1] == "HEX":
            if (len(operand1) < nibble_size) and (len(operand1) > 0):
                if any(item in operand1[0] for item in HEX_NEGATIVE_LIST):
                    operand1 = operand1.rjust(nibble_size, "F")
                else:
                    operand1 = operand1.rjust(nibble_size, "0")
            operand1_data_error = verify_hex_input(operand1)
            
            if operand2_present:
                if (len(operand2) < nibble_size) and (len(operand2) > 0):
                    if any(item in operand2[0] for item in HEX_NEGATIVE_LIST):
                        operand2 = operand2.rjust(nibble_size, "F")
                    else:
                        operand2 = operand2.rjust(nibble_size, "0")
                operand2_data_error = verify_hex_input(operand2)
                
        elif input_mode[1] == "BIN":
            operand1_data_error = verify_bin_input(operand1)
            if operand2_present:
                operand2_data_error = verify_bin_input(operand2)
                
        elif input_mode[1] == "FP32":
            exponent_size, mantissa_size = 8, 23
            operand1_data_error = verify_fp32_input(operand1)
            if operand2_present:
                operand2_data_error = verify_fp32_input(operand2)
                
        elif input_mode[1] == "FP64":
            exponent_size, mantissa_size = 11, 52
            operand1_data_error = verify_fp64_input(operand1)
            if operand2_present:
                operand2_data_error = verify_fp64_input(operand2)

        operator_error = verify_operator(operator)
        
        # Core Math Execution
        if not operand1_data_error and not operand2_data_error and not operator_error:
            operand1_binary = convert_to_binary(operand1)
            
            if operand2_present:
                operand2_binary = convert_to_binary(operand2)
                binary_result = binary_math_operation(operand1_binary, operand2_binary, operator)
                calculator_result = convert_from_binary(binary_result)
            else:
                calculator_result = convert_from_binary(operand1_binary)
            
            st.session_state.aux_display_var = str(calculator_result)
            st.rerun()
        else:
            st.session_state.main_display_var = ""
            if "input_win" in st.session_state:
                st.session_state.input_win = ""
            st.session_state.aux_display_var = "ERROR"
            st.rerun()
    else:
        # Append typed keys to your main input tracker
        st.session_state.main_display_var += str(button_push_result)
        st.rerun()
