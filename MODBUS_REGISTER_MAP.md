# SunSpec Model 701 - Modbus Register Map
## Net Meter (Import/Export) Register Locations

This document shows the exact Modbus register addresses for reading import/export energy data from your Enphase Envoy.

## SunSpec Base Address

SunSpec devices typically start at **Modbus address 40000** (or sometimes 40001). Your register data shows:
- **40000-40001**: SunSpec signature "SunS"
- **40002**: Model 1 (Common) ID = 1
- **40003**: Model 1 Length = 66 registers
- **40004-40069**: Model 1 data (device info)
- **40070**: Model 701 (DERMeasureAC) ID = 701
- **40071**: Model 701 Length = 153 registers
- **40072**: Model 701 data starts here

## Model 701 Register Layout

Model 701 contains 153 registers of data starting at address **40072**.

### Key Registers for Net Metering

| Register Offset | Modbus Address | Register Name | Type | Size | Description |
|-----------------|----------------|---------------|------|------|-------------|
| **Power Measurements** |
| +8 | 40080 | W | int16 | 1 | Active Power (Watts) - Current production |
| +9 | 40081 | VA | int16 | 1 | Apparent Power |
| +10 | 40082 | Var | int16 | 1 | Reactive Power |
| +11 | 40083 | PF | int16 | 1 | Power Factor |
| | | | | | |
| **Current** |
| +12 | 40084 | A | int16 | 1 | Total AC Current |
| | | | | | |
| **Voltage** |
| +13 | 40085 | LLV | uint16 | 1 | Line-to-Line Voltage |
| +14 | 40086 | LNV | uint16 | 1 | Line-to-Neutral Voltage |
| | | | | | |
| **Frequency** |
| +15-16 | 40087-40088 | Hz | uint32 | 2 | AC Frequency |
| | | | | | |
| **🎯 NET METER DATA (ENERGY)** |
| **+17-20** | **40089-40092** | **TotWhInj** | **uint64** | **4** | **Total Energy EXPORTED/PRODUCED (Wh)** ⭐ |
| **+21-24** | **40093-40096** | **TotWhAbs** | **uint64** | **4** | **Total Energy IMPORTED/CONSUMED (Wh)** ⭐ |
| +25-28 | 40097-40100 | TotVarhInj | uint64 | 4 | Total Reactive Energy Injected |
| +29-32 | 40101-40104 | TotVarhAbs | uint64 | 4 | Total Reactive Energy Absorbed |
| | | | | | |
| **Scale Factors** |
| +146 | 40218 | A_SF | int16 | 1 | Current Scale Factor |
| +147 | 40219 | V_SF | int16 | 1 | Voltage Scale Factor |
| +148 | 40220 | Hz_SF | int16 | 1 | Frequency Scale Factor |
| +149 | 40221 | W_SF | int16 | 1 | Active Power Scale Factor |
| +150 | 40222 | PF_SF | int16 | 1 | Power Factor Scale Factor |
| +151 | 40223 | VA_SF | int16 | 1 | Apparent Power Scale Factor |
| +152 | 40224 | Var_SF | int16 | 1 | Reactive Power Scale Factor |
| +153 | 40225 | TotWh_SF | int16 | 1 | Energy Scale Factor (for TotWhInj/Abs) |

## Reading Net Meter Data

To read import/export energy from your Enphase Envoy:

### Modbus Function Code 3 (Read Holding Registers)

```python
# Read energy exported (production)
# Address: 40089-40092 (4 registers)
exported_raw = modbus_client.read_holding_registers(40089, 4)
exported_value = (exported_raw[0] << 48) | (exported_raw[1] << 32) | (exported_raw[2] << 16) | exported_raw[3]

# Read energy imported (consumption)
# Address: 40093-40096 (4 registers)
imported_raw = modbus_client.read_holding_registers(40093, 4)
imported_value = (imported_raw[0] << 48) | (imported_raw[1] << 32) | (imported_raw[2] << 16) | imported_raw[3]

# Read scale factor
# Address: 40225 (1 register)
scale_factor = modbus_client.read_holding_registers(40225, 1)[0]

# Apply scale factor
exported_wh = exported_value * (10 ** scale_factor)
imported_wh = imported_value * (10 ** scale_factor)

print(f"Total Exported: {exported_wh} Wh = {exported_wh/1000} kWh")
print(f"Total Imported: {imported_wh} Wh = {imported_wh/1000} kWh")
```

## Your Captured Data Analysis

From your register snapshot:
- You provided registers **40000-40097** (98 registers total)
- Model 701 data was **incomplete**: only got to register 40097 (28/153 registers)
- Successfully decoded: **TotWhInj** (exported energy) = **358,442.60 kWh**
- Could NOT decode: **TotWhAbs** (imported energy) - data cut off at register 40097

The imported energy data starts at register **40093**, but you only provided data up to register **40097**, so only got 5 of the 4 required registers.

## Complete Read Command

To get all net meter data including scale factors:

```python
# Read Model 701 header
model_id = modbus_client.read_holding_registers(40070, 1)[0]  # Should be 701
model_len = modbus_client.read_holding_registers(40071, 1)[0]  # Should be 153

# Read complete Model 701 data (all 153 registers)
model_data = modbus_client.read_holding_registers(40072, 153)

# Or just read the specific registers you need:
# Energy + scale factor (registers 40089-40096 + 40225)
energy_data = modbus_client.read_holding_registers(40089, 8)    # TotWhInj and TotWhAbs
scale_factor = modbus_client.read_holding_registers(40225, 1)   # TotWh_SF
```

## Phase-Specific Energy Data

If you want per-phase import/export:

| Phase | Exported (Inj) | Imported (Abs) | Modbus Address |
|-------|----------------|----------------|----------------|
| L1 | TotWhInjL1 | TotWhAbsL1 | 40104-40115 |
| L2 | TotWhInjL2 | TotWhAbsL2 | 40125-40136 |
| L3 | TotWhInjL3 | TotWhAbsL3 | 40146-40157 |

Each is a uint64 (4 registers) using the same TotWh_SF scale factor.

## Important Notes

1. **Addresses are Modbus holding registers** (function code 3)
2. **Register numbering**: Some Modbus tools use 0-based (address 0 = register 1), others use 1-based. If using pymodbus or similar, use the addresses as shown.
3. **Read during production**: Read these registers when the inverter is producing (daytime) for accurate current power values
4. **Energy counters are cumulative**: TotWhInj and TotWhAbs are lifetime counters since installation
5. **Scale factors are static**: Read once at startup, they typically don't change

## Minimal Read for Net Metering

If you only want import/export totals:

**Read 9 registers starting at address 40089:**
- Registers 40089-40092: TotWhInj (exported)
- Registers 40093-40096: TotWhAbs (imported)
- Register 40225: TotWh_SF (scale factor) - Note: this is 129 registers away!

Or read in two commands:
1. `read_holding_registers(40089, 8)` → Get TotWhInj + TotWhAbs
2. `read_holding_registers(40225, 1)` → Get TotWh_SF

Apply scale factor to convert raw values to Watt-hours.
