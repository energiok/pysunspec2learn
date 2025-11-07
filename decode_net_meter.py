#!/usr/bin/env python3
"""
Decode net meter registers with correct offsets
"""

# Combined register data
part1 = [21365,28243,1,66,17742,20552,16723,17696,17742,17746,18265,0,0,0,0,0,0,0,0,0,17774,30319,30976,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,17464,11827,11829,12598,14080,0,0,0,12594,12850,13360,12336,12849,13616,0,0,0,0,0,0,0,0,0,0,65535,32768,701,153,0,65535,65535,65535,65535,65535,65535,65535,101,219,180,44,91,65535,24001,0,5000,0,0,175,1804,0,0,44,54693,65535,65535,65535]
part2 = [65535,65535,65535,65535,65535,32768,32768,32768,32768,32768,32768,32768,32768,32768,32768,32768,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,32768,32768,32768,32768,32768,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,32768,32768,32768,32768,32768,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65535,65534,65534,65534,0,65534,0,0,0,0,0,0,0,0,0,0,0,0]
part3 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,702,50,5310,4248,80,4248,80,5310,3186,3186,0,65535,0,65535,23000,26400,21900,65535,65535,65535,504,1,2,0,14269,65535]

registers = part1 + part2 + part3

# Model 701 starts at register 72 (after header at 70-71)
model_701_start = 72
model_701_data = registers[model_701_start:model_701_start+153]

print("=" * 90)
print("ENPHASE ENVOY - NET METER MODBUS REGISTER MAP")
print("=" * 90)
print(f"Device: {registers[2]} = Model {registers[2]} (Common)")
print(f"Model 701 at register 70-71, data starts at register 72")
print()

# Check if we have enough data
print(f"Model 701 data available: {len(model_701_data)} of 153 registers")
print()

# Decode based on actual structure
print("=" * 90)
print("KEY NET METERING REGISTERS")
print("=" * 90)

# Model 701 offset mapping
print("\nREGISTER LAYOUT (offsets within Model 701):")
print("-" * 90)

# Current Power - offset 8
W_offset = 8
W_raw = model_701_data[W_offset] if W_offset < len(model_701_data) else None
print(f"Offset {W_offset:3d} (Modbus {40072+W_offset}): W (Active Power) = {W_raw}")

# Current - offset 12
A_offset = 12
A_raw = model_701_data[A_offset] if A_offset < len(model_701_data) else None
print(f"Offset {A_offset:3d} (Modbus {40072+A_offset}): A (Current) = {A_raw}")

# Voltage LN - offset 14
LNV_offset = 14
LNV_raw = model_701_data[LNV_offset] if LNV_offset < len(model_701_data) else None
print(f"Offset {LNV_offset:3d} (Modbus {40072+LNV_offset}): LNV (Voltage) = {LNV_raw}")

# Frequency - offset 15-16 (uint32)
Hz_offset = 15
Hz_high = model_701_data[Hz_offset] if Hz_offset < len(model_701_data) else None
Hz_low = model_701_data[Hz_offset+1] if Hz_offset+1 < len(model_701_data) else None
Hz_raw = (Hz_high << 16) | Hz_low if Hz_high is not None and Hz_low is not None else None
print(f"Offset {Hz_offset:3d}-{Hz_offset+1} (Modbus {40072+Hz_offset}-{40072+Hz_offset+1}): Hz (Frequency) = {Hz_raw}")

print("\n" + "=" * 90)
print("⚡ ENERGY EXPORTED/PRODUCED (TotWhInj)")
print("=" * 90)

# TotWhInj - offset 17-20 (uint64)
export_offset = 17
if export_offset + 3 < len(model_701_data):
    r0 = model_701_data[export_offset]
    r1 = model_701_data[export_offset+1]
    r2 = model_701_data[export_offset+2]
    r3 = model_701_data[export_offset+3]

    print(f"Offset {export_offset:3d}-{export_offset+3} (Modbus {40072+export_offset}-{40072+export_offset+3}): TotWhInj (uint64)")
    print(f"  Register values: [{r0}, {r1}, {r2}, {r3}]")
    print(f"  Hex: [0x{r0:04X}, 0x{r1:04X}, 0x{r2:04X}, 0x{r3:04X}]")

    # Decode uint64
    exported_raw = (r0 << 48) | (r1 << 32) | (r2 << 16) | r3
    print(f"  Raw 64-bit value: {exported_raw}")

    # Try different scale factors
    print(f"\n  Possible values with different scale factors:")
    for sf in [-3, -2, -1, 0, 1]:
        value = exported_raw * (10 ** sf)
        print(f"    SF={sf:2d}: {value:15,.0f} Wh = {value/1000:12,.2f} kWh = {value/1000000:8,.3f} MWh")

print("\n" + "=" * 90)
print("🏠 ENERGY IMPORTED/CONSUMED (TotWhAbs)")
print("=" * 90)

# TotWhAbs - offset 21-24 (uint64)
import_offset = 21
if import_offset + 3 < len(model_701_data):
    r0 = model_701_data[import_offset]
    r1 = model_701_data[import_offset+1]
    r2 = model_701_data[import_offset+2]
    r3 = model_701_data[import_offset+3]

    print(f"Offset {import_offset:3d}-{import_offset+3} (Modbus {40072+import_offset}-{40072+import_offset+3}): TotWhAbs (uint64)")
    print(f"  Register values: [{r0}, {r1}, {r2}, {r3}]")
    print(f"  Hex: [0x{r0:04X}, 0x{r1:04X}, 0x{r2:04X}, 0x{r3:04X}]")

    # Decode uint64
    imported_raw = (r0 << 48) | (r1 << 32) | (r2 << 16) | r3
    print(f"  Raw 64-bit value: {imported_raw}")

    # Try different scale factors
    print(f"\n  Possible values with different scale factors:")
    for sf in [-3, -2, -1, 0, 1]:
        value = imported_raw * (10 ** sf)
        print(f"    SF={sf:2d}: {value:15,.0f} Wh = {value/1000:12,.2f} kWh = {value/1000000:8,.3f} MWh")

# Check scale factors near the end
print("\n" + "=" * 90)
print("SCALE FACTORS (near end of Model 701)")
print("=" * 90)

sf_offsets = {
    146: "A_SF (Current)",
    147: "V_SF (Voltage)",
    148: "Hz_SF (Frequency)",
    149: "W_SF (Power)",
    150: "PF_SF (Power Factor)",
    151: "VA_SF (Apparent Power)",
    152: "Var_SF (Reactive Power)",
    153: "TotWh_SF (Energy) ⭐"
}

for offset, name in sf_offsets.items():
    if offset < len(model_701_data):
        val = model_701_data[offset]
        # Convert to signed
        if val > 32767:
            val_signed = val - 65536
        else:
            val_signed = val
        print(f"Offset {offset:3d} (Modbus {40072+offset}): {name:30s} = {val:5d} (0x{val:04X}) = {val_signed:+3d} signed")
    else:
        print(f"Offset {offset:3d}: {name:30s} = NOT AVAILABLE")

print("\n" + "=" * 90)
print("📊 MOST LIKELY INTERPRETATION")
print("=" * 90)

# Based on typical Enphase values, scale factor is usually 0 or -1
exported_raw = (model_701_data[17] << 48) | (model_701_data[18] << 32) | (model_701_data[19] << 16) | model_701_data[20]
imported_raw = (model_701_data[21] << 48) | (model_701_data[22] << 32) | (model_701_data[23] << 16) | model_701_data[24]

# Try SF=0 (most common for Envoy)
print("\nAssuming Scale Factor = 0 (no scaling):")
print(f"  Production (Exported): {exported_raw:,} Wh = {exported_raw/1000:,.2f} kWh")
print(f"  Consumption (Imported): {imported_raw:,} Wh = {imported_raw/1000:,.2f} kWh")
print(f"  Net (Export-Import): {(exported_raw-imported_raw)/1000:,.2f} kWh")
print(f"  Current Power: {W_raw} W")

print("\n" + "=" * 90)
