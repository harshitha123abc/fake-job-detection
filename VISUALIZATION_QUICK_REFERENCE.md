# 🎯 Quick Reference: Visualization Features

## Where to Find Visualizations

After analyzing a job posting, scroll down to the **"📊 Advanced Risk Visualization"** section (appears after the Overall Risk Score progress bar).

## Five Interactive Charts

### 1. 🎯 Multi-Agent Analysis Radar (Signal Radar Chart)
```
What it shows: 5-point radar with all agent scores
How to read: Larger filled area = more comprehensive analysis
Best for: Understanding overall analysis profile
```

**Axis Points:**
- Cross-Platform Search (0-100%)
- Company Verification (0-100%)
- Scam Detection (0-100%)
- ML Fake Probability (0-100%)
- Data Quality (0-100%)

---

### 2. 📈 Overall Risk Gauge
```
What it shows: Circular gauge with overall risk percentage
Color zones: Green (0-25%) → Yellow → Orange → Red (75-100%)
Best for: Quick at-a-glance risk assessment
```

**Interpretation:**
- 🟢 0-25%: LOW RISK (Safe to apply)
- 🟡 25-50%: MODERATE RISK (Review carefully)
- 🟠 50-75%: HIGH RISK (Exercise caution)
- 🔴 75-100%: CRITICAL RISK (Likely a scam)

---

### 3. 📊 Agent Scores Breakdown (Bar Chart)
```
What it shows: Horizontal bars for each agent's score
Color coding: Green (safe) → Yellow (medium) → Red (risky)
Best for: Comparing agent performance
```

**Bar Colors:**
- 🟢 Green (0-33%): Good/Safe score
- 🟡 Yellow (33-67%): Medium concern
- 🔴 Red (67-100%): High risk indicator

---

### 4. 🎨 Risk Factor Contribution (Pie Chart)
```
What it shows: How each agent contributes to final risk
Weights:
  - Scam Detection: 35%
  - ML Analysis: 20%
  - Company Verification: 20%
  - Platform Search: 15%
  - Data Quality: 10%
Best for: Understanding analysis importance
```

---

### 5. 📋 Agent Performance Summary (Table)
```
Columns: Agent | Score | Status | Interpretation
Best for: Detailed, structured review of findings
```

**Status Indicators:**
- ✅ Good: Positive finding
- ⚠️ Medium: Mixed signals
- 🚨 Concerning: High risk

---

## How to Interpret Results

### Example 1: SAFE JOB
```
Gauge: 18% (Green)
Radar: Balanced, most agents high
Summary: ✅ Company Verified, ✅ Platforms, ✅ Low Scam
→ APPLY WITH CONFIDENCE
```

### Example 2: SUSPICIOUS JOB
```
Gauge: 62% (Orange)
Radar: Uneven - high scam, low verification
Summary: ⚠️ Some Red Flags, 🚨 Scam Signals, ❌ No Website
→ RESEARCH THOROUGHLY
```

### Example 3: CLEAR SCAM
```
Gauge: 88% (Red)
Radar: Very uneven - very high scam/ML
Summary: 🚨 MULTIPLE RED FLAGS, 💰 Payment Requests
→ AVOID AT ALL COSTS
```

---

## Agent Quick Reference

| Agent | Good Score | Risky Score | What It Means |
|-------|-----------|-----------|--------------|
| **Platform Search** | 70-100% | 0-30% | Job found on legit sites (good) |
| **Company Verify** | 70-100% | 0-30% | Company has website+LinkedIn (good) |
| **Scam Detection** | 0-30% | 70-100% | AI detected scam patterns (bad if high) |
| **ML Probability** | 0-30% | 70-100% | ML thinks it's fake (bad if high) |
| **Data Quality** | 70-100% | 0-30% | Job posting is detailed (good) |

---

## 5-Second Decision Guide

1. **Look at Gauge**: What's the color?
   - 🟢 Green? → Likely safe
   - 🟡 Yellow? → Review more
   - 🔴 Red? → Proceed with caution

2. **Check Radar**: Is it balanced?
   - Balanced = comprehensive analysis ✅
   - Uneven = specific concerns 🚨

3. **Scan Summary Table**: Any 🚨 icons?
   - Mostly ✅? → Apply
   - Mostly 🚨? → Skip

---

## Browser Tips

**Hover over charts** for detailed tooltips
**Zoom** by dragging on charts
**Download** using camera icon (Plotly toolbar)
**Pan** to see different areas
**Reset** by double-clicking chart

---

## Mobile Viewing

- Charts are responsive but may require scrolling
- Try landscape mode for better view
- All charts fully functional on mobile
- Tap for tooltips instead of hover

---

## Common Questions

**Q: What does a "balanced" radar mean?**
A: All agents scored similarly - no single major concern. Good sign!

**Q: Why is my scam detection 75% but the job seems normal?**
A: AI detected patterns common in scams. Always cross-reference with company info.

**Q: Should I apply if the gauge shows 35%?**
A: 35% is still "Low Risk" (0-50%). Do your own research but it seems okay.

**Q: What if all bars show different colors?**
A: Some agents flagged concerns (red) while others didn't (green). Investigate the red ones.

---

## Save/Share Your Results

1. **Download Chart**: Click camera icon in chart toolbar
2. **Take Screenshot**: Print screen for quick reference
3. **Email Results**: Copy chart image to email

---

**Need more help?** Read [VISUALIZATION_GUIDE.md](./VISUALIZATION_GUIDE.md) for detailed explanations.

Last Updated: April 2026
