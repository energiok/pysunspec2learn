# Complete List of Available SunSpec Registers
## Your Enphase Envoy - All Readable Values

---

## MODEL 1: COMMON (Device Information)
**Modbus 40004-40069**

| Register | Field | Your Value | Description |
|----------|-------|------------|-------------|
| 40004-40019 | Manufacturer | ENPHASE ENERGY | Device manufacturer |
| 40020-40035 | Model | Envoy | Device model |
| 40036-40043 | Options | (empty) | Optional features |
| 40044-40051 | Version | D8.3.5167 | Firmware version |
| 40052-40067 | Serial Number | 122240002150 | Device serial number |
| 40068 | Device Address | - | Modbus slave address |

---

## MODEL 701: DERMeasureAC (Net Meter / Grid Connection Point)
**Modbus 40072-40224** (153 registers)

### ⚡ REAL-TIME POWER (Current Measurements)

| Register | Field | Your Value | Units | Description |
|----------|-------|------------|-------|-------------|
| **40080** | **W** | **101** | **W** | **Net Active Power (+ = export, - = import)** ⭐ |
| 40081 | VA | 219 | VA | Apparent Power |
| 40082 | Var | 180 | VAR | Reactive Power |
| 40083 | PF | 44 | - | Power Factor (×SF) |

### 🔌 CURRENT

| Register | Field | Your Value | Units | Description |
|----------|-------|------------|-------|-------------|
| 40084 | A | 91 | A | Total AC Current (at grid connection) |
| 40072 | A (raw) | 0 | A | Total current (needs SF) |
| 40074 | AL1 | - | A | Phase 1 Current |
| 40075 | AL2 | - | A | Phase 2 Current |
| 40076 | AL3 | - | A | Phase 3 Current |

### ⚡ VOLTAGE

| Register | Field | Your Value | Units | Description |
|----------|-------|------------|-------|-------------|
| 40077 | LLV | - | V | Line-to-Line Voltage (average) |
| 40078 | LNV | - | V | Line-to-Neutral Voltage (average) |
| 40086 | LNV (alt) | 24,001 | V | Likely needs SF (probably 240.01 V) |

### 🌊 FREQUENCY

| Register | Field | Your Value | Units | Description |
|----------|-------|------------|-------|-------------|
| 40087-40088 | Hz | 5000 | Hz | Grid frequency (likely 50.00 or 60.00 Hz with SF) |

### 📊 LIFETIME ENERGY COUNTERS

| Register | Field | Your Value | Units | Description |
|----------|-------|------------|-------|-------------|
| **40089-40092** | **TotWhInj** | **11,470,604** | **Wh** | **Total Energy EXPORTED to Grid** ⭐ |
| **40093-40096** | **TotWhAbs** | **2,938,277** | **Wh** | **Total Energy IMPORTED from Grid** ⭐ |
| 40097-40100 | TotVarhInj | - | VARh | Total Reactive Energy Injected |
| 40101-40104 | TotVarhAbs | - | VARh | Total Reactive Energy Absorbed |

**Your Net Energy Balance:**
- Exported: 11,470.60 kWh
- Imported: 2,938.28 kWh
- **Net: 8,532.33 kWh surplus** 🎉

### 📊 PER-PHASE ENERGY (if available)

#### Phase 1 (L1):
| Register | Field | Units | Description |
|----------|-------|-------|-------------|
| 40104-40107 | TotWhInjL1 | Wh | Phase 1 Energy Exported |
| 40108-40111 | TotWhAbsL1 | Wh | Phase 1 Energy Imported |
| 40112-40115 | TotVarhInjL1 | VARh | Phase 1 Reactive Energy Injected |
| 40116-40119 | TotVarhAbsL1 | VARh | Phase 1 Reactive Energy Absorbed |

#### Phase 2 (L2):
| Register | Field | Units | Description |
|----------|-------|-------|-------------|
| 40125-40128 | TotWhInjL2 | Wh | Phase 2 Energy Exported |
| 40129-40132 | TotWhAbsL2 | Wh | Phase 2 Energy Imported |
| 40133-40136 | TotVarhInjL2 | VARh | Phase 2 Reactive Energy Injected |
| 40137-40140 | TotVarhAbsL2 | VARh | Phase 2 Reactive Energy Absorbed |

#### Phase 3 (L3):
| Register | Field | Units | Description |
|----------|-------|-------|-------------|
| 40146-40149 | TotWhInjL3 | Wh | Phase 3 Energy Exported |
| 40150-40153 | TotWhAbsL3 | Wh | Phase 3 Energy Imported |
| 40154-40157 | TotVarhInjL3 | VARh | Phase 3 Reactive Energy Injected |
| 40158-40161 | TotVarhAbsL3 | VARh | Phase 3 Reactive Energy Absorbed |

### 🌡️ TEMPERATURE SENSORS

| Register | Field | Units | Description |
|----------|-------|-------|-------------|
| 40105 | TmpAmb | °C | Ambient Temperature |
| 40106 | TmpCab | °C | Cabinet Temperature |
| 40107 | TmpSnk | °C | Heat Sink Temperature |
| 40108 | TmpTrns | °C | Transformer Temperature |
| 40109 | TmpSw | °C | IGBT/MOSFET Temperature |
| 40110 | TmpOt | °C | Other Temperature |

### 🎚️ SYSTEM STATUS

| Register | Field | Your Value | Description |
|----------|-------|------------|-------------|
| 40074 | ACType | 0 | AC Wiring Type (0=Single Phase, 1=Split, 2=Three Phase) |
| 40075 | St | - | Operating State (0=Off, 1=On) |
| 40076 | InvSt | - | Inverter State (3=Running, 6=Fault, etc.) |
| 40077 | ConnSt | - | Grid Connection State (0=Disconnected, 1=Connected) |
| 40078-40079 | Alrm | - | Alarm Bitfield (active alarms) |
| 40080-40081 | DERMode | - | Operational Mode (Grid Following/Forming, etc.) |

### ⚙️ THROTTLING INFO

| Register | Field | Units | Description |
|----------|-------|-------|-------------|
| 40165 | ThrotPct | % | Power throttling percentage |
| 40166-40167 | ThrotSrc | - | Throttling source (frequency control, voltage, etc.) |

### 📐 SCALE FACTORS

| Register | Field | Your Value | Description |
|----------|-------|------------|-------------|
| 40218 | A_SF | 0 | Current Scale Factor |
| 40219 | V_SF | 0 | Voltage Scale Factor |
| 40220 | Hz_SF | 0 | Frequency Scale Factor |
| 40221 | W_SF | 0 | Active Power Scale Factor |
| 40222 | PF_SF | 0 | Power Factor Scale Factor |
| 40223 | VA_SF | 0 | Apparent Power Scale Factor |
| 40224 | Var_SF | 702 | Reactive Power Scale Factor (invalid?) |
| 40225 | TotWh_SF | 0 | Energy Scale Factor (0 = no scaling needed) |

---

## MODEL 702: DERCapacity (System Ratings)
**Modbus 40227+** (partial data available)

| Register | Field | Description |
|----------|-------|-------------|
| 40227 | WRtg | Maximum Active Power Rating (W) |
| 40228 | VARtg | Maximum Apparent Power Rating (VA) |
| 40229-40232 | VArRtg | Reactive Power Ratings (all quadrants) |
| 40233 | ARtg | Maximum Current Rating (A) |
| 40234 | PFRtgQ1-Q4 | Power Factor Ratings |
| 40235-40238 | VRtg | Voltage Ratings (nominal, max, min) |

---

## 🎯 MOST USEFUL REGISTERS FOR MONITORING

### Real-Time Dashboard:
1. **40080** - Net Power (W) - Shows if importing/exporting RIGHT NOW
2. **40084** - Current (A) - How much current flowing
3. **40086** - Voltage (V) - Grid voltage
4. **40087-88** - Frequency (Hz) - Grid frequency

### Energy Tracking:
5. **40089-92** - Total Exported (Wh) - Lifetime solar production sent to grid
6. **40093-96** - Total Imported (Wh) - Lifetime grid consumption
7. Net Balance = Exported - Imported = **8,532 kWh surplus**

### System Health:
8. **40075** - Operating State - Is system on/off?
9. **40076** - Inverter State - Is it running/faulting?
10. **40077** - Grid Connection - Connected to grid?
11. **40078-79** - Alarms - Any active alarms?

---

## 📝 NOTES

### What's NOT Available in Model 701:
- **❌ Direct Solar Production** - Model 701 measures at the grid connection (net meter), not solar output
- To get actual solar production, you'd need:
  - Inverter models (103, 160, 203) for per-microinverter data
  - Or calculate: Solar Production = Net Export + Home Consumption

### Data Interpretation:
- **Positive W** = Exporting to grid (solar > consumption)
- **Negative W** = Importing from grid (solar < consumption)
- Energy counters are **cumulative/lifetime** totals
- All values use **scale factors** (SF) for proper conversion
- Your SF values are all 0, meaning no scaling needed (direct values)

### Polling Recommendations:
- **Real-time power (40080)**: Poll every 1-5 seconds
- **Energy counters (40089-96)**: Poll every 5-15 minutes
- **Status fields**: Poll every 30-60 seconds
- **Device info (Model 1)**: Read once at startup

---

## 🔧 PYTHON EXAMPLE: Read Key Values

```python
import sunspec2.modbus.client as client

# Connect to Envoy
d = client.SunSpecModbusClientDeviceTCP(
    slave_id=1,
    ipaddr='YOUR_ENVOY_IP',
    ipport=502
)

# Scan and read Model 701
d.scan()
m701 = d.models[701][0]
m701.read()

# Real-time values
print(f"Net Power: {m701.W.cvalue} W")  # + = export, - = import
print(f"Current: {m701.A.cvalue} A")
print(f"Voltage: {m701.LNV.cvalue} V")
print(f"Frequency: {m701.Hz.cvalue} Hz")

# Energy totals
print(f"Total Exported: {m701.TotWhInj.cvalue/1000:.2f} kWh")
print(f"Total Imported: {m701.TotWhAbs.cvalue/1000:.2f} kWh")
print(f"Net Balance: {(m701.TotWhInj.cvalue - m701.TotWhAbs.cvalue)/1000:.2f} kWh")

# System status
print(f"Operating State: {m701.St.value}")
print(f"Inverter State: {m701.InvSt.value}")
print(f"Grid Connected: {m701.ConnSt.value}")
```
