"""
Local test script for Human Design chart rendering.
Generates an SVG bodygraph chart with a defined Solar Plexus.
"""

import sys
import json

# Add src to path for imports
sys.path.insert(0, r'c:\Users\juand\Documents\TriniHD\humandesign_api\src')

from datetime import datetime
from pytz import timezone
from humandesign.features.core import calc_single_hd_features, get_utc_offset_from_tz
from humandesign.utils import serialization as cj
from humandesign.services.chart_renderer import generate_bodygraph_image
from humandesign import hd_constants

# === USER BIRTH DATA ===
# Replace with your actual birth data:
# This test date produces a defined Solar Plexus for chart verification
BIRTH_YEAR = 1987
BIRTH_MONTH = 1
BIRTH_DAY = 9
BIRTH_HOUR = 10
BIRTH_MINUTE = 30
BIRTH_SECOND = 0
TIMEZONE_STR = 'America/Bogota'  # e.g., 'America/Bogota', 'America/Santiago', 'Europe/Madrid'
# =======================

# Calculate accurate UTC offset from timezone string using pytz
# This handles DST and historic timezone changes automatically
birth_datetime_local = datetime(BIRTH_YEAR, BIRTH_MONTH, BIRTH_DAY, BIRTH_HOUR, BIRTH_MINUTE, BIRTH_SECOND)
tz_obj = timezone(TIMEZONE_STR)
localized_dt = tz_obj.localize(birth_datetime_local)
utc_offset_hours = get_utc_offset_from_tz(
    (BIRTH_YEAR, BIRTH_MONTH, BIRTH_DAY, BIRTH_HOUR, BIRTH_MINUTE, BIRTH_SECOND),
    TIMEZONE_STR
)

# Convert to UTC for reference
utc_dt = localized_dt.astimezone(timezone('UTC'))

# Build timestamp tuple for calculation engine
timestamp = (BIRTH_YEAR, BIRTH_MONTH, BIRTH_DAY, BIRTH_HOUR, BIRTH_MINUTE, BIRTH_SECOND, utc_offset_hours)

print(f"Birth Data: {BIRTH_YEAR}-{BIRTH_MONTH:02d}-{BIRTH_DAY:02d} {BIRTH_HOUR:02d}:{BIRTH_MINUTE:02d}:{BIRTH_SECOND:02d}")
print(f"Timezone: {TIMEZONE_STR}")
print(f"UTC Offset: {utc_offset_hours:+.2f} hours")
print(f"UTC Time: {utc_dt.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Timestamp tuple: {timestamp}")

# Calculate HD features
try:
    single_result = calc_single_hd_features(timestamp, report=False, channel_meaning=False, day_chart_only=False)
    
    # Unpack result
    energy_type = single_result[0]
    inner_authority = single_result[1]
    inc_cross = single_result[2]
    profile = single_result[4]
    definition = single_result[5]
    planets_data = single_result[6]
    active_chakras = single_result[7]
    channels_data = single_result[8]
    birth_date = single_result[9]
    create_date = single_result[10]
    variables = single_result[11]
    
    print(f"\nChart calculated successfully!")
    print(f"Energy Type: {energy_type}")
    print(f"Inner Authority: {inner_authority}")
    print(f"Profile: {profile}")
    print(f"Definition: {definition}")
    print(f"Active Centers (raw): {active_chakras}")
    print(f"Defined Centers (mapped): {[hd_constants.CHAKRA_NAMES_MAP.get(c, c) for c in active_chakras]}")
    
    # Check if Solar Plexus is defined
    sp_defined = "SP" in active_chakras or "Solar Plexus" in [hd_constants.CHAKRA_NAMES_MAP.get(c, c) for c in active_chakras]
    print(f"Solar Plexus Defined: {sp_defined}")
    
except Exception as e:
    print(f"Error calculating HD features: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Format data for chart
try:
    # Create the data structure expected by serialization functions
    data = {
        "birth_date": str(birth_date),
        "create_date": str(create_date),
        "energy_type": energy_type,
        "inner_authority": inner_authority,
        "inc_cross": inc_cross,
        "profile": profile,
        "active_chakras": active_chakras,
        "inactive_chakras": set(hd_constants.CHAKRA_LIST) - set(active_chakras),
        "definition": str(definition),
        "variables": variables
    }
    
    # Generate JSON outputs
    general_json_str = cj.general(data)
    gates_json_str = cj.gatesJSON(planets_data)
    channels_json_str = cj.channelsJSON(channels_data, False)
    
    # Parse back to dicts
    general_output = json.loads(general_json_str)
    gates_output = json.loads(gates_json_str)
    channels_output = json.loads(channels_json_str)
    
    # Final result structure expected by chart renderer
    final_result = {
        "general": general_output,
        "gates": gates_output,
        "channels": channels_output
    }
    
    print(f"\nData formatted for chart.")
    print(f"Defined centers in general output: {general_output.get('defined_centers', [])}")
    
except Exception as e:
    print(f"Error formatting data for chart: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Generate SVG chart
try:
    print("\nGenerating SVG chart...")
    img_bytes = generate_bodygraph_image(final_result, fmt='svg')
    
    # Save to file
    output_path = r'c:\Users\juand\Documents\TriniHD\humandesign_api\test_output.svg'
    with open(output_path, 'wb') as f:
        f.write(img_bytes)
    
    print(f"Chart saved to: {output_path}")
    print(f"File size: {len(img_bytes)} bytes")
    
except Exception as e:
    print(f"Error generating chart: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ Test completed successfully!")
