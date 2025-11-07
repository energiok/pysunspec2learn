#!/usr/bin/env python3
"""
Analyze complete SunSpec register data with Modbus addresses.
Shows exact register numbers and decoded values.
"""

import struct

# Combined register data from the user's inverter
# Array 1: Base + Model 1 + start of Model 701
registers_part1 = [21365,28243,1,66,17742,20552,16723,17696,17742,17746,18265,0,0,0,0,0,0,0,0,0,17774,30319,30976,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,17464,11827,11829,12598,14080,0,0,0,12594,12850,13360,12336,12849,13616,0,0,0,0,0,0,0,0,0,0,65535,32768,701,153,0,65535,65535,65535,65535,65535,65535,65535,101,219,180,44,91,65535,24001,0,5000,0,0,175,1804,0,0,44,54693,65535,65535,65535]

# Array 2: Continuation of Model 701
registers_part2 = [65535,65535,65535,65535,65535,32768,32768,32768,32768,32768,32768,32768,32768,32768,32768,32768,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,32768,32768,32768,32768,32768,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,32768,32768,32768,32768,32768,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65534,65534,65534,0,65534,0,0,0,0,0,0,0,0,0,0,0,0]

# Array 3: End of Model 701 + Model 702
registers_part3 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,702,50,5310,4248,80,4248,80,5310,3186,3186,0,65535,0,65535,23000,26400,21900,65535,65535,65535,504,1,2,0,14269,65535]

# Combine all arrays
registers = registers_part1 + registers_part2 + registers_part3

MODBUS_BASE = 40000  # Standard SunSpec base address

def decode_uint16(val):
    """Decode unsigned 16-bit integer"""
    if val is None:
        return None
    if val == 0xFFFF:
        return None  # Not implemented
    return val

def decode_int16(val):
    """Decode signed 16-bit integer"""
    if val is None:
        return None
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

def decode_uint64(r0, r1, r2, r3):
    """Decode unsigned 64-bit integer from four registers"""
    if r0 is None or r1 is None or r2 is None or r3 is None:
        return None
    if r0 == 0xFFFF and r1 == 0xFFFF and r2 == 0xFFFF and r3 == 0xFFFF:
        return None
    return (r0 << 48) | (r1 << 32) | (r2 << 16) | r3

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
    if sf < -10 or sf > 10:
        return None
    try:
        return value * (10 ** sf)
    except (OverflowError, ValueError):
        return None

print("=" * 100)
print("COMPLETE SUNSPEC MODBUS REGISTER ANALYSIS")
print("=" * 100)
print(f"Total registers: {len(registers)}")
print(f"Register range: {MODBUS_BASE} to {MODBUS_BASE + len(registers) - 1}")

# Verify SunSpec signature
if registers[0] == 21365 and registers[1] == 28243:
    sig_str = decode_string([registers[0], registers[1]])
    print(f"\n✓ Valid SunSpec signature detected: '{sig_str}'")
    print(f"  Modbus {MODBUS_BASE}-{MODBUS_BASE+1}: {registers[0]}, {registers[1]}")
else:
    print("\n✗ Invalid SunSpec signature!")
    exit(1)

# Parse model blocks
idx = 2
model_num = 0

while idx < len(registers):
    model_id = registers[idx]
    modbus_addr = MODBUS_BASE + idx

    # End of models marker
    if model_id == 65535:
        print(f"\n[End of models marker at Modbus {modbus_addr}]")
        break

    if idx + 1 >= len(registers):
        break

    model_len = registers[idx + 1]
    model_num += 1

    print(f"\n{'=' * 100}")
    print(f"MODEL #{model_num}: ID={model_id}, Length={model_len} registers")
    print(f"  Header at Modbus {modbus_addr}-{modbus_addr+1}")
    print(f"  Data starts at Modbus {modbus_addr+2}")
    print(f"{'=' * 100}")

    # Extract model data
    data_start = idx + 2
    data_end = data_start + model_len

    if data_end > len(registers):
        print(f"Warning: Model expects {model_len} registers, but only {len(registers) - data_start} available!")
        model_data = registers[data_start:]
    else:
        model_data = registers[data_start:data_end]

    # Decode specific models
    if model_id == 1:
        print("\n*** COMMON MODEL (Device Information) ***")
        print(f"Manufacturer: {decode_string(model_data[0:16])}")
        print(f"Model: {decode_string(model_data[16:32])}")
        print(f"Version: {decode_string(model_data[40:48])}")
        print(f"Serial Number: {decode_string(model_data[48:64])}")

    elif model_id == 701:
        print("\n*** MODEL 701: DERMeasureAC (NET METERING DATA) ***\n")

        base_addr = MODBUS_BASE + data_start

        # Get scale factors first
        A_SF = decode_int16(safe_get(model_data, 146))
        V_SF = decode_int16(safe_get(model_data, 147))
        Hz_SF = decode_int16(safe_get(model_data, 148))
        W_SF = decode_int16(safe_get(model_data, 149))
        PF_SF = decode_int16(safe_get(model_data, 150))
        VA_SF = decode_int16(safe_get(model_data, 151))
        Var_SF = decode_int16(safe_get(model_data, 152))
        TotWh_SF = decode_int16(safe_get(model_data, 153))

        print("SCALE FACTORS:")
        print(f"  Modbus {base_addr+146}: A_SF = {A_SF}")
        print(f"  Modbus {base_addr+147}: V_SF = {V_SF}")
        print(f"  Modbus {base_addr+148}: Hz_SF = {Hz_SF}")
        print(f"  Modbus {base_addr+149}: W_SF = {W_SF}")
        print(f"  Modbus {base_addr+153}: TotWh_SF = {TotWh_SF} ⭐")

        # Current Power
        print("\n" + "─" * 100)
        print("CURRENT POWER (Real-time)")
        print("─" * 100)
        W = decode_int16(safe_get(model_data, 8))
        actual_power = apply_scale_factor(W, W_SF)
        print(f"  Modbus {base_addr+8}: W = {W} (raw), SF={W_SF}")
        if actual_power is not None:
            print(f"  ⚡ CURRENT POWER: {actual_power:,.0f} W ({actual_power/1000:.3f} kW)")
        else:
            print(f"  ⚡ CURRENT POWER: Not available")

        # Current
        A = decode_int16(safe_get(model_data, 12))
        print(f"\n  Modbus {base_addr+12}: A = {A} (raw), SF={A_SF}")
        if apply_scale_factor(A, A_SF) is not None:
            print(f"  Current: {apply_scale_factor(A, A_SF):.2f} A")

        # Voltage
        LNV = decode_uint16(safe_get(model_data, 14))
        print(f"  Modbus {base_addr+14}: LNV = {LNV} (raw), SF={V_SF}")
        if apply_scale_factor(LNV, V_SF) is not None:
            print(f"  Voltage: {apply_scale_factor(LNV, V_SF):.1f} V")

        # Frequency
        Hz_raw = decode_uint32(safe_get(model_data, 15), safe_get(model_data, 16))
        print(f"  Modbus {base_addr+15}-{base_addr+16}: Hz = {Hz_raw} (raw), SF={Hz_SF}")
        if apply_scale_factor(Hz_raw, Hz_SF) is not None:
            print(f"  Frequency: {apply_scale_factor(Hz_raw, Hz_SF):.2f} Hz")

        # ENERGY EXPORTED (PRODUCTION)
        print("\n" + "═" * 100)
        print("🌞 ENERGY EXPORTED / PRODUCED (Lifetime)")
        print("═" * 100)
        TotWhInj_raw = decode_uint64(
            safe_get(model_data, 17),
            safe_get(model_data, 18),
            safe_get(model_data, 19),
            safe_get(model_data, 20)
        )
        exported_wh = apply_scale_factor(TotWhInj_raw, TotWh_SF)

        print(f"  Modbus {base_addr+17}-{base_addr+20}: TotWhInj (uint64)")
        print(f"    Register values: [{safe_get(model_data, 17)}, {safe_get(model_data, 18)}, {safe_get(model_data, 19)}, {safe_get(model_data, 20)}]")
        print(f"    Raw value: {TotWhInj_raw}")
        print(f"    Scale factor: {TotWh_SF}")
        if exported_wh is not None:
            print(f"  ⚡ TOTAL EXPORTED: {exported_wh:,.0f} Wh = {exported_wh/1000:,.2f} kWh = {exported_wh/1000000:,.3f} MWh")
        else:
            print(f"  ⚡ TOTAL EXPORTED: Not available")

        # ENERGY IMPORTED (CONSUMPTION)
        print("\n" + "═" * 100)
        print("🏠 ENERGY IMPORTED / CONSUMED (Lifetime)")
        print("═" * 100)
        TotWhAbs_raw = decode_uint64(
            safe_get(model_data, 21),
            safe_get(model_data, 22),
            safe_get(model_data, 23),
            safe_get(model_data, 24)
        )
        imported_wh = apply_scale_factor(TotWhAbs_raw, TotWh_SF)

        print(f"  Modbus {base_addr+21}-{base_addr+24}: TotWhAbs (uint64)")
        print(f"    Register values: [{safe_get(model_data, 21)}, {safe_get(model_data, 22)}, {safe_get(model_data, 23)}, {safe_get(model_data, 24)}]")
        print(f"    Raw value: {TotWhAbs_raw}")
        print(f"    Scale factor: {TotWh_SF}")
        if imported_wh is not None:
            print(f"  ⚡ TOTAL IMPORTED: {imported_wh:,.0f} Wh = {imported_wh/1000:,.2f} kWh = {imported_wh/1000000:,.3f} MWh")
        else:
            print(f"  ⚡ TOTAL IMPORTED: Not available")

        # NET ENERGY
        if exported_wh is not None and imported_wh is not None:
            net_wh = exported_wh - imported_wh
            print("\n" + "═" * 100)
            print("📊 NET ENERGY BALANCE")
            print("═" * 100)
            print(f"  Net (Exported - Imported): {net_wh/1000:,.2f} kWh = {net_wh/1000000:,.3f} MWh")
            if net_wh > 0:
                print(f"  ✓ You've exported {net_wh/1000:,.2f} kWh more than you've imported!")
            else:
                print(f"  ⚠ You've imported {abs(net_wh)/1000:,.2f} kWh more than you've exported")

        # Reactive power
        Var = decode_int16(safe_get(model_data, 10))
        print(f"\n  Modbus {base_addr+10}: Var = {Var} (raw), SF={Var_SF}")
        if apply_scale_factor(Var, Var_SF) is not None:
            print(f"  Reactive Power: {apply_scale_factor(Var, Var_SF):.0f} VAR")

    elif model_id == 702:
        print("\n*** MODEL 702: DERCapacity (System Ratings) ***\n")

        base_addr = MODBUS_BASE + data_start

        # DER Capacity contains system ratings
        WRtg = decode_uint16(safe_get(model_data, 0))
        VARtg = decode_uint16(safe_get(model_data, 1))
        VArRtgQ1 = decode_int16(safe_get(model_data, 2))
        VArRtgQ2 = decode_int16(safe_get(model_data, 3))
        VArRtgQ3 = decode_int16(safe_get(model_data, 4))
        VArRtgQ4 = decode_int16(safe_get(model_data, 5))
        ARtg = decode_uint16(safe_get(model_data, 6))

        # Get scale factors
        W_SF = decode_int16(safe_get(model_data, 44))

        print(f"  Modbus {base_addr+0}: WRtg = {WRtg} (Max Active Power Rating)")
        print(f"  Modbus {base_addr+1}: VARtg = {VARtg} (Max Apparent Power Rating)")
        print(f"  Modbus {base_addr+6}: ARtg = {ARtg} (Max Current Rating)")
        print(f"  Modbus {base_addr+44}: W_SF = {W_SF}")

        if WRtg is not None and W_SF is not None:
            max_w = apply_scale_factor(WRtg, W_SF)
            if max_w is not None:
                print(f"\n  ⚡ System Max Power: {max_w:,.0f} W ({max_w/1000:.2f} kW)")

    else:
        print(f"\nModel {model_id} data present but not decoded in detail")

    # Move to next model
    idx = data_end

print("\n" + "=" * 100)
print("QUICK REFERENCE - KEY MODBUS REGISTERS")
print("=" * 100)
print(f"Production (Export):  Modbus {MODBUS_BASE+89}-{MODBUS_BASE+92}  (TotWhInj - uint64)")
print(f"Consumption (Import): Modbus {MODBUS_BASE+93}-{MODBUS_BASE+96}  (TotWhAbs - uint64)")
print(f"Energy Scale Factor:  Modbus {MODBUS_BASE+225}               (TotWh_SF - int16)")
print(f"Current Power:        Modbus {MODBUS_BASE+80}                (W - int16)")
print(f"Power Scale Factor:   Modbus {MODBUS_BASE+221}               (W_SF - int16)")
print("=" * 100)
