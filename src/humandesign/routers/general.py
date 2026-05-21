# SPDX-License-Identifier: AGPL-3.0-or-later OR LicenseRef-DevAIble-Commercial
#
# Human Design API
# Copyright (C) 2026 Dogan Turkuler <dogan.turkuler@gmail.com>
# https://devaible.com
#
# This file is part of Human Design API, available under dual license:
#   - AGPL-3.0 (open source): see LICENSE-AGPL
#   - Commercial License: see LICENSE-COMMERCIAL or contact dogan.turkuler@gmail.com

from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import JSONResponse, Response
# from timezonefinder import TimezoneFinder # Removed
import json

from .. import features as hd
from .. import hd_constants
from ..utils import serialization as cj
from ..services import chart_renderer as chart
from ..services.geolocation import get_latitude_longitude, tf
from ..dependencies import verify_token
from ..utils.date_utils import clean_birth_date_to_iso, clean_create_date_to_iso
from ..schemas.general import HealthResponse
from ..utils.health_utils import check_swisseph_health
from datetime import datetime

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    """Operational status and system info."""
    from ..api import __version__
    return {
        "status": "ok",
        "version": __version__,
        "timestamp": datetime.now().isoformat(),
        "dependencies": {
            "pyswisseph": check_swisseph_health()
        }
    }

@router.get("/calculate")
def calculate_hd(
    year: int = Query(1968, description="Birth year"),
    month: int = Query(2, description="Birth month"),
    day: int = Query(21, description="Birth day"),
    hour: int = Query(11, description="Birth hour"),
    minute: int = Query(0, description="Birth minute"),
    second: int = Query(0, description="Birth second (optional, default 0)"),
    place: Optional[str] = Query(None, description="Birth place (used for geocoding only when latitude/longitude are not provided)"),
    gender: str = Query("male", description="Gender (optional)"),
    islive: bool = Query(True, description="Whether the person is still alive (True) or deceased (False)"),
    latitude: Optional[float] = Query(None, description="Optional latitude for birth place"),
    longitude: Optional[float] = Query(None, description="Optional longitude for birth place"),
    authorized: bool = Depends(verify_token)
):
    # 1. Validate and collect input
    birth_time = (year, month, day, hour, minute, second)

    # 2. Geocode and timezone
    # Strict priority: coordinates first, then text geocoding fallback
    try:
        # PRIORITY 1: Use provided coordinates directly (bypass geocoding entirely)
        if latitude is not None and longitude is not None:
            zone = tf.timezone_at(lat=latitude, lng=longitude) or 'Etc/UTC'
        
        # PRIORITY 2: Fall back to text geocoding if no coordinates provided
        elif place:
            latitude, longitude = get_latitude_longitude(place)
            if latitude is not None and longitude is not None:
                zone = tf.timezone_at(lat=latitude, lng=longitude) or 'Etc/UTC'
            else:
                raise HTTPException(status_code=400, detail=f"Geocoding failed for place: '{place}'. Please check the place name or try a different format.")
        
        # No coordinates and no place string
        else:
            raise HTTPException(status_code=400, detail="Either coordinates (latitude/longitude) or a place name must be provided.")
        
        hours = hd.get_utc_offset_from_tz(birth_time, zone)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error determining timezone or offset: {str(e)}")

    # 3. Prepare timestamp
    timestamp = tuple(list(birth_time) + [float(hours)])

    # 4. Calculate Human Design Features
    try:
        single_result = hd.calc_single_hd_features(timestamp, report=False, channel_meaning=False, day_chart_only=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating Human Design features: {str(e)}")

    # 5. Additional Calculations (Age, Zodiac)
    from ..utils import astrology
    from ..utils import date_utils
    
    age = date_utils.calculate_age(birth_time)
    # Personality Sun longitude is at index 0 of the 'lon' list in date_to_gate_dict (index 6 of result)
    sun_lon = single_result[6]['lon'][0]
    zodiac_sign = astrology.get_zodiac_sign(sun_lon)

    # 6. Format Data for JSON Output
    try:
        data = {
            "birth_date": clean_birth_date_to_iso(single_result[9], hours),
            "create_date": clean_create_date_to_iso(single_result[10]),
            "birth_place": place,
            "energy_type": single_result[0],
            "inner_authority": single_result[1],
            "inc_cross": single_result[2],
            "profile": single_result[4], # Pass tuple directly for serialization helper
            "active_chakras": list(single_result[7]),
            "inactive_chakras": list(set(hd_constants.CHAKRA_LIST) - set(single_result[7])),
            "definition": "{}".format(single_result[5]),
            "variables": single_result[11],
            "age": age,
            "zodiac_sign": zodiac_sign,
            "gender": gender,
            "islive": islive
        }
        
        # Serialize parts
        general_json_str = cj.general(data)
        gates_json_str = cj.gatesJSON(single_result[6])
        channels_json_str = cj.channelsJSON(single_result[8], False)
        
        general_output = json.loads(general_json_str)
        gates_output = json.loads(gates_json_str)
        channels_output = json.loads(channels_json_str)
        
        final_result = {
            "general": general_output,
            "channels": channels_output,
            "gates": gates_output
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing results: {str(e)}")

    return JSONResponse(content=final_result)

@router.get("/bodygraph")
def get_bodygraph_image(
    year: int = Query(1968, description="Birth year"),
    month: int = Query(2, description="Birth month"),
    day: int = Query(21, description="Birth day"),
    hour: int = Query(11, description="Birth hour"),
    minute: int = Query(0, description="Birth minute"),
    second: int = Query(0, description="Birth second (optional, default 0)"),
    place: Optional[str] = Query(None, description="Birth place (used for geocoding only when latitude/longitude are not provided)"),
    fmt: str = Query("png", description="Image format: png, svg, jpg/jpeg"),
    latitude: Optional[float] = Query(None, description="Optional latitude for birth place"),
    longitude: Optional[float] = Query(None, description="Optional longitude for birth place"),
    authorized: bool = Depends(verify_token)
):
    # 1. Validate and collect input
    birth_time = (year, month, day, hour, minute, second)

    # 2. Geocode and timezone
    # Strict priority: coordinates first, then text geocoding fallback
    try:
        # PRIORITY 1: Use provided coordinates directly (bypass geocoding entirely)
        if latitude is not None and longitude is not None:
            zone = tf.timezone_at(lat=latitude, lng=longitude) or 'Etc/UTC'
        
        # PRIORITY 2: Fall back to text geocoding if no coordinates provided
        elif place:
            latitude, longitude = get_latitude_longitude(place)
            if latitude is not None and longitude is not None:
                zone = tf.timezone_at(lat=latitude, lng=longitude) or 'Etc/UTC'
            else:
                raise HTTPException(status_code=400, detail=f"Geocoding failed for place: '{place}'. Please check the place name or try a different format.")
        
        # No coordinates and no place string
        else:
            raise HTTPException(status_code=400, detail="Either coordinates (latitude/longitude) or a place name must be provided.")
        
        hours = hd.get_utc_offset_from_tz(birth_time, zone)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error determining timezone or offset: {str(e)}")

    # 3. Prepare timestamp
    timestamp = tuple(list(birth_time) + [int(hours)])

    # 4. Calculate Human Design Features
    try:
        single_result = hd.calc_single_hd_features(timestamp, report=False, channel_meaning=False, day_chart_only=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating Human Design features: {str(e)}")

    # 5. Format Data for JSON Output (Required for Chart)
    try:
        data = {
            "birth_date": clean_birth_date_to_iso(single_result[9], hours),
            "create_date": clean_create_date_to_iso(single_result[10]),
            "energy_type": single_result[0],
            "inner_authority": single_result[1],
            "inc_cross": single_result[2],
            "profile": single_result[4],
            "active_chakras": single_result[7],
            "inactive_chakras": set(hd_constants.CHAKRA_LIST) - set(single_result[7]),
            "definition": "{}".format(single_result[5]),
            "variables": single_result[11]
        }
        general_json_str = cj.general(data)
        gates_json_str = cj.gatesJSON(single_result[6])
        channels_json_str = cj.channelsJSON(single_result[8], False)
        
        general_output = json.loads(general_json_str)
        gates_output = json.loads(gates_json_str)
        channels_output = json.loads(channels_json_str)
        
        final_result = {
            "general": general_output,
            "gates": gates_output,
            "channels": channels_output
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error formatting data for chart: {e}")
        
    # 6. Generate Image
    try:
        img_bytes = chart.generate_bodygraph_image(final_result, fmt=fmt)
        if fmt == 'svg':
            media_type = "image/svg+xml"
        elif fmt in ['jpg', 'jpeg']:
            media_type = "image/jpeg"
        else:
            media_type = "image/png"
            
        return Response(content=img_bytes, media_type=media_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating chart image: {e}")
