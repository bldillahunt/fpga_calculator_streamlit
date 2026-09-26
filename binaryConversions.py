def binary_to_fixed_point(bin_str: str, int_bits: int, frac_bits: int) -> int:
	"""Converts a two's complement binary string to a real float value."""
	total_bits = int_bits + frac_bits
	
	if (int_bits > 0):
		bin_str_concatenated = bin_str[:int_bits] + bin_str[int_bits + 1:]
	else:
		bin_str_concatenated = "0" + bin_str[2:]
		
	val = int(bin_str_concatenated, 2)
	
	# Handle negative sign bit
	if (val & (1 << (total_bits - 1))) and (int_bits > 0):
		val -= (1 << total_bits)
		
	return val

def fixed_point_to_binary(val: float, int_bits: int, frac_bits: int) -> str:
	"""Converts a real float value to a signed two's complement binary string."""
	total_bits = int_bits + frac_bits
	val_scaled = round(val * (2**frac_bits))
	val_scaled_masked = val_scaled & ((1 << total_bits) - 1)
	val_scaled_string = f"{val_scaled_masked:0{total_bits}b}"
	print(val_scaled, val_scaled_masked, val_scaled_string)
	binary_point_offset = int_bits
	return f"{val_scaled_string[:binary_point_offset]}.{val_scaled_string[binary_point_offset:]}"




