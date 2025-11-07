# SunSpec Register Analysis Summary

## Overview
Your register data contains valid SunSpec formatted data from an **Enphase Energy Envoy** device.

## Device Information (Model 1 - Common)
- **Manufacturer:** ENPHASE ENERGY
- **Model:** Envoy
- **Version:** D8.3.5167
- **Serial Number:** 122240002150

## Energy Data (Model 701 - DERMeasureAC)

### ✅ SUCCESSFULLY DECODED:

#### **Total Energy Exported/Produced**
- **358,442.60 kWh** (358.4 MWh)
- This is the lifetime cumulative solar energy your system has produced and exported to the grid

### ⚠️ DATA LIMITATIONS:

Your register snapshot is **incomplete** - Model 701 expects 153 registers but only 28 were provided. This affects:

1. **Current Power Production:** Not available (invalid scale factor)
   - This would show your instantaneous power production (in Watts/kW)

2. **Energy Imported:** Not available
   - This would show energy consumed from the grid

3. **Real-time measurements:** Most current measurement fields show as "not implemented" (0xFFFF)
   - Current, voltage, frequency readings appear invalid or not implemented

## What This Means

Your Enphase Envoy has recorded that your solar system has produced **358,442.60 kWh** total since installation.

However, to get **real-time production data** (current power, import/export), you need to:

1. **Read the complete Model 701 data** - You provided 28 registers but need 153
2. **Query the device when it's producing** - Many values show 0 or "not implemented", suggesting either:
   - The inverter is not currently producing (nighttime?)
   - The register snapshot is from a configuration/status read rather than a full data read

## How to Get Complete Data

To read the full SunSpec data from your Enphase Envoy:

```python
import sunspec2.modbus.client as client

# Connect to your Envoy
d = client.SunSpecModbusClientDeviceTCP(
    slave_id=1,
    ipaddr='YOUR_ENVOY_IP',  # e.g., '192.168.1.100'
    ipport=502
)

# Scan for all models
d.scan()

# Read Model 701 for production data
if 701 in d.models:
    m701 = d.models[701][0]
    m701.read()

    # Current power production
    print(f"Current Power: {m701.W.cvalue} W")

    # Energy exported (produced)
    print(f"Total Exported: {m701.TotWhInj.cvalue} Wh")

    # Energy imported (consumed)
    print(f"Total Imported: {m701.TotWhAbs.cvalue} Wh")
```

## Key Register Mappings Found

From your data snapshot:
- Registers 0-1: SunSpec signature "SunS" ✓
- Registers 2-69: Model 1 (Common - Device Info) ✓
- Registers 70-97: Model 701 (DERMeasureAC - partial data) ⚠️

The energy exported value (358,442.60 kWh) was decoded from:
- Registers 94-95 (indices 24-25 in Model 701 data)
- Raw value: 3,584,425,983
- Scale factor: -1 (divide by 10)
- Result: 358,442,598 Wh = 358,442.60 kWh

## Next Steps

1. **For real-time monitoring:** Query your Envoy device directly using the pysunspec2 library
2. **Read during daytime:** Ensure the solar system is producing when you read the registers
3. **Read complete model data:** Request all 153 registers for Model 701, not just the first 28

The script I created (`analyze_registers.py`) can be used to decode any future register dumps you collect.
