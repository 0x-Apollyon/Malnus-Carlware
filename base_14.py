def string_to_base14(string):
    combined_int = 0
    for char in string:
        combined_int = combined_int * 256 + ord(char)
    
    if combined_int == 0:
        return '0'
    digits = "0123456789abcd"
    base14 = ""
    while combined_int > 0:
        remainder = combined_int % 14
        base14 = digits[remainder] + base14
        combined_int = combined_int // 14
    return base14

def base14_to_string(b14):
    digits = "0123456789abcd"
    value = 0
    for char in b14:
        value = value * 14 + digits.index(char)
    
    chars = []
    while value > 0:
        value, remainder = divmod(value, 256)
        chars.append(chr(remainder))
    return ''.join(reversed(chars))

# Example usage:
original_string = "open calc.exe"
base14_string = string_to_base14(original_string)
print(f"Base14: {base14_string}")
converted_back = base14_to_string("74880637d187c68080b3dc0")
print(f"Converted back: {converted_back}")