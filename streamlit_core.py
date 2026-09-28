def convert_to_binary(operand):
    if (input_mode[1] == "REAL"):
        n_binary_string = real_to_twos_comp_binary(operand, int_bits, frac_bits)
        n_int_list = binary_string_to_int_list(n_binary_string)
    elif (input_mode[1] == "HEX"):
        n_binary_string = hexadecimal_to_binary(operand, int_bits, frac_bits, lookup_table)
        n_int_list = binary_string_to_int_list(n_binary_string)
    elif (input_mode[1] == "FP32"):
        current_profile = precision_profile["SINGLE"]
        p = current_profile
        n_binary_string = ieee754_hex_to_binary(operand, p, lookup_table)
        n_int_list = n_binary_string
    elif (input_mode[1] == "FP64"):
        current_profile = precision_profile["DOUBLE"]
        p = current_profile
        n_binary_string = ieee754_hex_to_binary(operand, p, lookup_table)
        n_int_list = n_binary_string
    else: 
        n_int_list = binary_string_to_int_list(operand)

    return n_int_list

def binary_math_operation(operand1, operand2, operator):
	if (operator == "/"):
		if (output_mode[1] == "FP32"):
			current_profile = precision_profile["SINGLE"]
			p = current_profile

			if (1 + p.exponent_size + p.mantissa_size) < (int_bits + frac_bits):
				max_size = int_bits + frac_bits
			else:
				max_size = 64
		elif (output_mode[1] == "FP64"):
			current_profile = precision_profile["DOUBLE"]
			p = current_profile

			if (1 + p.exponent_size + p.mantissa_size) < (int_bits + frac_bits):
				max_size = int_bits + frac_bits
			else:
				max_size = 128
		else:
			max_size = int_bits + frac_bits

		operand1_no_bin_point, operand2_no_bin_point, operand1_fraction_size, operand2_fraction_size = binary_point_alignment(operand1, operand2, False)

		if (operand1[0] == 1):
			operand1_2s_comp, op1_carry = twos_complement(operand1_no_bin_point)
			sign_operand1 = 1
		else:
			operand1_2s_comp = operand1_no_bin_point
			sign_operand1 = 0

		if (operand2[0] == 1):
			operand2_2s_comp, op2_carry = twos_complement(operand2_no_bin_point)
			sign_operand2 = 1
		else:
			operand2_2s_comp = operand2_no_bin_point
			sign_operand2 = 0

		quotient = binary_division(operand1_2s_comp, operand2_2s_comp, max_size)

		if ((sign_operand1 ^ sign_operand2) == 1):
			quotient_size = len(quotient)

			if ('.' in quotient):
				quotient_radix_index = quotient.index('.')
				quotient.pop(quotient_radix_index)
			else:
				quotient_radix_index = quotient_size

			if (quotient_radix_index < quotient_size):
				quotient_fraction_size = quotient_size - (quotient_radix_index + 1)
			else:
				quotient_fraction_size = 0

			quotient_no_bin_point = quotient
			quotient_2s_comp, carry_quotient = twos_complement(quotient_no_bin_point)

			quotient_2s_comp_bin_point = quotient_2s_comp[:quotient_size - quotient_fraction_size - 1] + ['.'] + quotient_2s_comp[quotient_size - quotient_fraction_size - 1:]

			math_result_2s_comp = quotient_2s_comp_bin_point
		else:
			math_result_2s_comp = quotient
		math_result = math_result_2s_comp
	elif (operator == "*"):
		math_result = binary_multiplier(operand1, operand2)
	elif (operator == "+"):
		addend_a, addend_b, operand1_fraction_size, operand2_fraction_size = binary_point_alignment(operand1, operand2, False)

		if (operand1_fraction_size > operand2_fraction_size):
			fraction_size = operand1_fraction_size
		else:
			fraction_size = operand2_fraction_size

		n_sum, n_carry = binary_adder(addend_a, addend_b)

		if ((operand1[0] == 0) and (operand2[0] == 0) and (n_sum[0] == 1)) or ((operand1[0] == 1) and (operand2[0] == 1) and (n_sum[0] == 0)):
			sum_result = [n_carry] + n_sum
		else:
			sum_result = n_sum

		binary_point_index = len(sum_result) - fraction_size

		math_result = sum_result[:binary_point_index] + ['.'] + sum_result[binary_point_index:]
	elif (operator == "-"):
		math_result = binary_subtraction(operand1, operand2)

	return math_result

def convert_from_binary(operand):
    if (output_mode[1] == "REAL"):
        conversion_result = binary_to_real(operand)
    elif (output_mode[1] == "HEX"):
        conversion_result = binary_to_hexadecimal(operand, lookup_table)
    elif (output_mode[1] == "FP32"):
        conversion_result = binary_to_ieee754(operand, precision_profile["SINGLE"], lookup_table)
    elif (output_mode[1] == "FP64"):
        conversion_result = binary_to_ieee754(operand, precision_profile["DOUBLE"], lookup_table)
    else:
        operand_int_list = int_list_to_binary_string(operand, len(operand))
        conversion_result = "".join(operand_int_list)
    return conversion_result                                                                                                                  
