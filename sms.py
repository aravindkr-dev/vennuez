import phonenumbers
from phonenumbers import geocoder, carrier, timezone

# Replace with the number you want to check
raw_number = "+911234567895"  # Use E.164 format if possible

try:
    # Parse the number (2nd argument is default region if not specified in number)
    parsed_number = phonenumbers.parse(raw_number, "IN")

    # Check if the number is a valid phone number
    is_valid = phonenumbers.is_valid_number(parsed_number)
    is_possible = phonenumbers.is_possible_number(parsed_number)

    if is_valid:
        print("✅ Valid phone number")
        print("Location:", geocoder.description_for_number(parsed_number, "en"))
        print("Carrier:", carrier.name_for_number(parsed_number, "en"))
        print("Timezones:", timezone.time_zones_for_number(parsed_number))
    else:
        print("❌ Invalid phone number")

except phonenumbers.NumberParseException as e:
    print("❌ Error parsing number:", e)
