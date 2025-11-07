#!/usr/bin/env python3
"""
Analyze raw SunSpec register data to decode inverter information.
Specifically looking for import/export and production data.
"""

import struct

# Raw register data from the user's inverter
registers = [21365,28243,1,66,17742,20552,16723,17696,17742,17746,18265,0,0,0,0,0,0,0,0,0,17774,30319,30976,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,17464,11827,11829,12598,14080,0,0,0,12594,12850,13360,12336,12849,13616,0,0,0,0,0,0,0,0,0,0,65535,32768,701,153,0,65535,65535,65535,65535,65535,65535,65535,96,235,201,45,100,65535,23786,0,5000,0,0,175,1785,0,0,44,54693,65535,65535,65535]

def decode_uint16(val):
    """Decode unsigned 16-bit integer"""
    if val == 0xFFFF:
        return None  # Not implemented
    return val

def decode_int16(val):
    """Decode signed 16-bit integer"""
    if val == 0x8000:
        return None  # Not implemented
    # Convert unsigned to signed
    if val > 32767:
        return val - 65536
    return val

def decode_uint32(high, low):
    """Decode unsigned 32-bit integer from two registers"""
    if high is None or low is None:
        return None
    if high == 0xFFFF and low == 0xFFFF:
        return None
    return (high << 16) | low

def decode_int32(high, low):
    """Decode signed 32-bit integer from two registers"""
    if high is None or low is None:
        return None
    if high == 0x8000 and low == 0:
        return None
    val = (high << 16) | low
    if val > 2147483647:
        return val - 4294967296
    return val

def safe_get(data, idx, default=None):
    """Safely get value from list with bounds checking"""
    try:
        return data[idx]
    except IndexError:
        return default

def decode_string(regs):
    """Decode string from registers"""
    chars = []
    for reg in regs:
        high = (reg >> 8) & 0xFF
        low = reg & 0xFF
        if high != 0:
            chars.append(chr(high))
        if low != 0:
            chars.append(chr(low))
    return ''.join(chars).rstrip('\x00')

def apply_scale_factor(value, sf):
    """Apply scale factor to value"""
    if value is None or sf is None:
        return None
    # Scale factors should typically be in range -10 to 10
    # Values outside this range are likely invalid/not implemented
    if sf < -10 or sf > 10:
        return None
    try:
        return value * (10 ** sf)
    except (OverflowError, ValueError):
        return None

print("=" * 80)
print("SUNSPEC REGISTER ANALYSIS")
print("=" * 80)

# Verify SunSpec signature
if registers[0] == 21365 and registers[1] == 28243:
    sig_str = decode_string([registers[0], registers[1]])
    print(f"\n✓ Valid SunSpec signature detected: {sig_str}")
else:
    print("\n✗ Invalid SunSpec signature!")
    exit(1)

# Parse model blocks
idx = 2
model_num = 0

while idx < len(registers):
    model_id = registers[idx]

    # End of models marker
    if model_id == 65535:
        print(f"\n[End of models marker at register {idx}]")
        break

    if idx + 1 >= len(registers):
        break

    model_len = registers[idx + 1]
    model_num += 1

    print(f"\n{'=' * 80}")
    print(f"MODEL #{model_num}: ID={model_id}, Length={model_len} registers")
    print(f"Register offset: {idx}")
    print(f"{'=' * 80}")

    # Extract model data
    data_start = idx + 2
    data_end = data_start + model_len

    if data_end > len(registers):
        print(f"Warning: Model expects {model_len} registers, but only {len(registers) - data_start} available!")
        print(f"Parsing available data...\n")
        model_data = registers[data_start:]
    else:
        model_data = registers[data_start:data_end]

    # Decode specific models
    if model_id == 1:
        print("\n*** COMMON MODEL (Device Information) ***")
        # Model 1 has fixed length of 66
        print(f"Manufacturer: {decode_string(model_data[0:16])}")
        print(f"Model: {decode_string(model_data[16:32])}")
        print(f"Options: {decode_string(model_data[32:40])}")
        print(f"Version: {decode_string(model_data[40:48])}")
        print(f"Serial Number: {decode_string(model_data[48:64])}")
        device_addr = decode_uint16(model_data[64])
        print(f"Device Address: {device_addr}")

    elif model_id == 701:
        print("\n*** MODEL 701: DERMeasureAC (PRODUCTION/IMPORT/EXPORT DATA) ***")
        print("\nThis model contains the data you're looking for!\n")

        if len(model_data) < 27:
            print(f"ERROR: Insufficient data for Model 701 (need at least 27 registers, have {len(model_data)})")
            print(f"Available data: {model_data}")
            idx = data_end
            continue

        # Parse Model 701 - DER AC Measurement
        # Based on SunSpec Model 701 specification

        # Current measurements
        A = decode_int16(safe_get(model_data, 0))
        A_SF = decode_int16(safe_get(model_data, 1))
        print(f"Current (A): {A} (raw), SF={A_SF}, Actual: {apply_scale_factor(A, A_SF)} A")

        # Phase currents (if available)
        AL1 = decode_int16(safe_get(model_data, 2))
        AL2 = decode_int16(safe_get(model_data, 3))
        AL3 = decode_int16(safe_get(model_data, 4))
        if AL1 is not None:
            print(f"  Phase 1 Current: {apply_scale_factor(AL1, A_SF)} A")
        if AL2 is not None:
            print(f"  Phase 2 Current: {apply_scale_factor(AL2, A_SF)} A")
        if AL3 is not None:
            print(f"  Phase 3 Current: {apply_scale_factor(AL3, A_SF)} A")

        # Voltage measurements
        LLV = decode_uint16(safe_get(model_data, 5))
        LNV = decode_uint16(safe_get(model_data, 6))
        V_SF = decode_int16(safe_get(model_data, 7))
        print(f"\nVoltage (Line-to-Line): {LLV} (raw), SF={V_SF}, Actual: {apply_scale_factor(LLV, V_SF)} V")
        print(f"Voltage (Line-to-Neutral): {LNV} (raw), SF={V_SF}, Actual: {apply_scale_factor(LNV, V_SF)} V")

        # Phase voltages
        VL1 = decode_uint16(safe_get(model_data, 8))
        VL2 = decode_uint16(safe_get(model_data, 9))
        VL3 = decode_uint16(safe_get(model_data, 10))
        if VL1 is not None:
            print(f"  Phase 1 Voltage: {apply_scale_factor(VL1, V_SF)} V")
        if VL2 is not None:
            print(f"  Phase 2 Voltage: {apply_scale_factor(VL2, V_SF)} V")
        if VL3 is not None:
            print(f"  Phase 3 Voltage: {apply_scale_factor(VL3, V_SF)} V")

        # Frequency
        Hz = decode_int16(safe_get(model_data, 11))
        Hz_SF = decode_int16(safe_get(model_data, 12))
        print(f"\nFrequency: {Hz} (raw), SF={Hz_SF}, Actual: {apply_scale_factor(Hz, Hz_SF)} Hz")

        # POWER MEASUREMENTS (PRODUCTION)
        W = decode_int16(safe_get(model_data, 13))
        W_SF = decode_int16(safe_get(model_data, 14))
        actual_power = apply_scale_factor(W, W_SF)
        print(f"\n*** ACTIVE POWER (W): {W} (raw), SF={W_SF}")
        if actual_power is not None:
            print(f"*** ACTUAL POWER: {actual_power} W = {actual_power/1000:.2f} kW ***")
        else:
            print("*** ACTUAL POWER: Not available (invalid scale factor or value) ***")

        # Phase powers
        WL1 = decode_int16(safe_get(model_data, 15))
        WL2 = decode_int16(safe_get(model_data, 16))
        WL3 = decode_int16(safe_get(model_data, 17))
        if WL1 is not None:
            print(f"  Phase 1 Power: {apply_scale_factor(WL1, W_SF)} W")
        if WL2 is not None:
            print(f"  Phase 2 Power: {apply_scale_factor(WL2, W_SF)} W")
        if WL3 is not None:
            print(f"  Phase 3 Power: {apply_scale_factor(WL3, W_SF)} W")

        # Apparent Power
        VA = decode_int16(safe_get(model_data, 18))
        VA_SF = decode_int16(safe_get(model_data, 19))
        print(f"\nApparent Power (VA): {apply_scale_factor(VA, VA_SF)} VA")

        # Reactive Power
        Var = decode_int16(safe_get(model_data, 20))
        Var_SF = decode_int16(safe_get(model_data, 21))
        print(f"Reactive Power (Var): {apply_scale_factor(Var, Var_SF)} Var")

        # Power Factor
        PF = decode_int16(safe_get(model_data, 22))
        PF_SF = decode_int16(safe_get(model_data, 23))
        print(f"Power Factor: {apply_scale_factor(PF, PF_SF)}")

        # ENERGY EXPORTED (PRODUCED/INJECTED)
        print("\n" + "=" * 60)
        print("ENERGY EXPORTED/PRODUCED (TotWhInj)")
        print("=" * 60)
        TotWhInj = decode_uint32(safe_get(model_data, 24), safe_get(model_data, 25))
        TotWh_SF = decode_int16(safe_get(model_data, 26))
        exported_wh = apply_scale_factor(TotWhInj, TotWh_SF)
        print(f"Total Energy EXPORTED: {TotWhInj} (raw), SF={TotWh_SF}")
        if exported_wh is not None:
            print(f"*** ACTUAL EXPORTED: {exported_wh:,.0f} Wh = {exported_wh/1000:,.2f} kWh ***")

        # Phase energy exported
        TotWhInjL1 = decode_uint32(safe_get(model_data, 27), safe_get(model_data, 28))
        TotWhInjL2 = decode_uint32(safe_get(model_data, 29), safe_get(model_data, 30))
        TotWhInjL3 = decode_uint32(safe_get(model_data, 31), safe_get(model_data, 32))
        if TotWhInjL1 is not None and TotWh_SF is not None:
            phase1_exp = apply_scale_factor(TotWhInjL1, TotWh_SF)
            if phase1_exp is not None:
                print(f"  Phase 1 Exported: {phase1_exp:,.0f} Wh")
        if TotWhInjL2 is not None and TotWh_SF is not None:
            phase2_exp = apply_scale_factor(TotWhInjL2, TotWh_SF)
            if phase2_exp is not None:
                print(f"  Phase 2 Exported: {phase2_exp:,.0f} Wh")
        if TotWhInjL3 is not None and TotWh_SF is not None:
            phase3_exp = apply_scale_factor(TotWhInjL3, TotWh_SF)
            if phase3_exp is not None:
                print(f"  Phase 3 Exported: {phase3_exp:,.0f} Wh")

        # ENERGY IMPORTED (ABSORBED/CONSUMED)
        print("\n" + "=" * 60)
        print("ENERGY IMPORTED/CONSUMED (TotWhAbs)")
        print("=" * 60)
        TotWhAbs = decode_uint32(safe_get(model_data, 33), safe_get(model_data, 34))
        imported_wh = apply_scale_factor(TotWhAbs, TotWh_SF)
        print(f"Total Energy IMPORTED: {TotWhAbs} (raw), SF={TotWh_SF}")
        if imported_wh is not None:
            print(f"*** ACTUAL IMPORTED: {imported_wh:,.0f} Wh = {imported_wh/1000:,.2f} kWh ***")

        # Phase energy imported
        TotWhAbsL1 = decode_uint32(safe_get(model_data, 35), safe_get(model_data, 36))
        TotWhAbsL2 = decode_uint32(safe_get(model_data, 37), safe_get(model_data, 38))
        TotWhAbsL3 = decode_uint32(safe_get(model_data, 39), safe_get(model_data, 40))
        if TotWhAbsL1 is not None and TotWh_SF is not None:
            phase1_imp = apply_scale_factor(TotWhAbsL1, TotWh_SF)
            if phase1_imp is not None:
                print(f"  Phase 1 Imported: {phase1_imp:,.0f} Wh")
        if TotWhAbsL2 is not None and TotWh_SF is not None:
            phase2_imp = apply_scale_factor(TotWhAbsL2, TotWh_SF)
            if phase2_imp is not None:
                print(f"  Phase 2 Imported: {phase2_imp:,.0f} Wh")
        if TotWhAbsL3 is not None and TotWh_SF is not None:
            phase3_imp = apply_scale_factor(TotWhAbsL3, TotWh_SF)
            if phase3_imp is not None:
                print(f"  Phase 3 Imported: {phase3_imp:,.0f} Wh")

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        if actual_power is not None:
            print(f"Current Power Production: {actual_power:,.0f} W ({actual_power/1000:.2f} kW)")
        if exported_wh is not None:
            print(f"Total Energy Produced/Exported: {exported_wh/1000:,.2f} kWh")
        if imported_wh is not None:
            print(f"Total Energy Consumed/Imported: {imported_wh/1000:,.2f} kWh")
        if exported_wh is not None and imported_wh is not None:
            net = exported_wh - imported_wh
            print(f"Net Energy (Exported - Imported): {net/1000:,.2f} kWh")

        # Debug: show raw data
        print("\n" + "=" * 60)
        print("DEBUG: Raw Model 701 Data")
        print("=" * 60)
        print(f"Total registers available: {len(model_data)}")
        print(f"Raw data: {model_data}")

    else:
        print(f"\nModel {model_id} - Raw data:")
        print(f"First 10 registers: {model_data[:10]}")

    # Move to next model
    idx = data_end

print("\n" + "=" * 80)
print("Analysis complete!")
print("=" * 80)
