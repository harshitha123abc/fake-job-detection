"""
Advanced visualizations for fake job detection analysis.
Includes radar charts, gauge charts, and score distributions.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List
import numpy as np


def create_risk_gauge(risk_score: float, risk_level: str) -> go.Figure:
    """Create a circular gauge chart for overall risk score"""

    color_map = {
        "Low":    "#22c55e",
        "Medium": "#f59e0b",
        "High":   "#f43f5e",
    }
    color = color_map.get(risk_level, "#7a8fa6")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Risk Score", 'font': {'size': 15, 'color': '#7a8fa6'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1,
                     'tickcolor': "rgba(255,255,255,.2)",
                     'tickfont': {'color': 'rgba(255,255,255,.4)', 'size': 10}},
            'bar': {'color': color, 'thickness': 0.72},
            'bgcolor': "rgba(255,255,255,.04)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 33],  'color': "rgba(34,197,94,.1)"},
                {'range': [33, 60], 'color': "rgba(245,158,11,.1)"},
                {'range': [60, 80], 'color': "rgba(244,63,94,.1)"},
                {'range': [80, 100],'color': "rgba(244,63,94,.18)"},
            ],
            'threshold': {
                'line': {'color': "#f43f5e", 'width': 2},
                'thickness': 0.75, 'value': 75,
            },
        },
        number={'suffix': "%", 'font': {'size': 36, 'color': color}},
    ))

    fig.update_layout(
        height=220,
        margin=dict(l=20, r=20, t=46, b=10),
        font={'family': "Inter, sans-serif", 'size': 13},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_agent_radar_chart(confidence_breakdown: Dict) -> go.Figure:
    """Create a radar chart where ALL axes mean higher = safer (scam/ML inverted)."""

    categories = [
        "Platform Search",
        "Company Verification",
        "Scam Safety",
        "ML Safety",
        "Data Quality",
    ]

    # Invert scam & ML so larger area always = safer job
    values = [
        confidence_breakdown.get("cross_platform_search", 0),
        confidence_breakdown.get("company_verification", 0),
        100 - confidence_breakdown.get("scam_detection", 0),
        100 - confidence_breakdown.get("ml_fake_probability", 0),
        confidence_breakdown.get("data_quality", 0),
    ]

    avg_safety = sum(values) / len(values)
    if avg_safety >= 60:
        fill_color = "rgba(34,197,94,0.18)"
        line_color = "#22c55e"
    elif avg_safety >= 40:
        fill_color = "rgba(245,158,11,0.18)"
        line_color = "#f59e0b"
    else:
        fill_color = "rgba(244,63,94,0.18)"
        line_color = "#f43f5e"

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[60]*5 + [60],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(34,197,94,0.06)',
        line=dict(color='rgba(34,197,94,0.25)', width=1, dash='dot'),
        name='Safe Zone (60%)',
        hoverinfo='skip',
        showlegend=True,
    ))

    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor=fill_color,
        line=dict(color=line_color, width=2.5),
        name='Safety Profile',
        hovertemplate='<b>%{theta}</b><br>Safety: %{r:.1f}%<extra></extra>',
        showlegend=True,
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100],
                            tickfont=dict(size=10, color='rgba(255,255,255,.3)'),
                            gridcolor='rgba(255,255,255,.08)',
                            linecolor='rgba(255,255,255,.08)'),
            angularaxis=dict(tickfont=dict(size=11, family='Inter, sans-serif',
                                          color='rgba(255,255,255,.6)'),
                             linecolor='rgba(255,255,255,.1)'),
            bgcolor='rgba(255,255,255,.02)',
        ),
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=-0.18, xanchor='center', x=0.5,
                    font=dict(color='rgba(255,255,255,.5)', size=11)),
        height=230,
        margin=dict(l=45, r=45, t=36, b=48),
        font={'family': "Inter, sans-serif", 'size': 12, 'color': 'rgba(255,255,255,.6)'},
        paper_bgcolor="rgba(0,0,0,0)",
        title=dict(text="🛡️ Safety Profile  (larger = safer)",
                   font=dict(size=12, color='rgba(255,255,255,.5)'), x=0.5),
    )
    return fig


def create_score_bars(confidence_breakdown: Dict) -> go.Figure:
    """Horizontal bar chart — green = safe signal, red = risk signal, per agent semantics."""

    # (label, key, higher_is_worse)
    metrics = [
        ("Data Quality",          "data_quality",          False),
        ("ML Fake Probability",   "ml_fake_probability",   True),
        ("Scam Detection",        "scam_detection",        True),
        ("Company Verification",  "company_verification",  False),
        ("Cross-Platform Search", "cross_platform_search", False),
    ]

    agents  = [m[0] for m in metrics]
    scores  = [confidence_breakdown.get(m[1], 0) for m in metrics]
    worse   = [m[2] for m in metrics]

    colors, border_colors = [], []
    for s, w in zip(scores, worse):
        if w:
            c = "#f43f5e" if s >= 60 else ("#f59e0b" if s >= 35 else "#22c55e")
            b = "#e11d48" if s >= 60 else ("#d97706" if s >= 35 else "#16a34a")
        else:
            c = "#22c55e" if s >= 60 else ("#f59e0b" if s >= 35 else "#f43f5e")
            b = "#16a34a" if s >= 60 else ("#d97706" if s >= 35 else "#e11d48")
        colors.append(c)
        border_colors.append(b)

    labels = [f"{s:.0f}%" for s in scores]

    fig = go.Figure(go.Bar(
        y=agents, x=scores, orientation='h',
        marker=dict(color=colors, line=dict(color=border_colors, width=1),
                    opacity=0.88),
        text=labels,
        textposition='inside',
        insidetextanchor='middle',
        textfont=dict(color='white', size=11, family='Inter, sans-serif'),
        hovertemplate='<b>%{y}</b><br>Score: %{x:.1f}%<extra></extra>',
        showlegend=False,
    ))

    fig.add_annotation(x=102, y=4.5, text="🟢 High = Safe",  showarrow=False,
                       xanchor='left', font=dict(size=10, color='#22c55e'), xref='x', yref='y')
    fig.add_annotation(x=102, y=3.5, text="🔴 High = Risk",  showarrow=False,
                       xanchor='left', font=dict(size=10, color='#f43f5e'), xref='x', yref='y')
    fig.add_annotation(x=102, y=2.5, text="🟡 Caution",       showarrow=False,
                       xanchor='left', font=dict(size=10, color='#f59e0b'), xref='x', yref='y')

    fig.update_layout(
        xaxis_title="Score (%)",
        height=210,
        margin=dict(l=185, r=110, t=28, b=28),
        xaxis=dict(range=[0, 100], gridcolor='rgba(255,255,255,.07)',
                   zeroline=False, tickfont=dict(color='rgba(255,255,255,.35)')),
        yaxis=dict(tickfont=dict(color='rgba(255,255,255,.65)')),
        plot_bgcolor='rgba(255,255,255,.02)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': "Inter, sans-serif", 'size': 12, 'color': 'rgba(255,255,255,.6)'},
        title=dict(text="📊 Agent Score Breakdown",
                   font=dict(size=12, color='rgba(255,255,255,.5)'), x=0.5),
    )
    return fig


def create_risk_distribution_pie(confidence_breakdown: Dict, risk_score: float) -> go.Figure:
    """Create a pie chart showing risk factor distribution"""
    
    labels = [
        "Scam Detection",
        "ML Analysis",
        "Company Verification",
        "Platform Search",
        "Data Quality"
    ]
    
    # Weight each component by its contribution to final risk
    values = [
        confidence_breakdown.get("scam_detection", 0) * 0.35,
        confidence_breakdown.get("ml_fake_probability", 0) * 0.20,
        (100 - confidence_breakdown.get("company_verification", 0)) * 0.20,
        (100 - confidence_breakdown.get("cross_platform_search", 0)) * 0.15,
        (100 - confidence_breakdown.get("data_quality", 0)) * 0.10
    ]
    
    colors = ['#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3,
        marker=dict(colors=colors, line=dict(color='white', width=2)),
        textposition='inside',
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Contribution: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        height=400,
        showlegend=True,
        margin=dict(l=40, r=40, t=40, b=40),
        font={'family': "Arial, sans-serif", 'size': 12},
        paper_bgcolor="white"
    )
    
    return fig


def create_multi_metric_dashboard(confidence_breakdown: Dict, risk_score: float, risk_level: str) -> go.Figure:
    """Create a comprehensive dashboard with multiple subplots"""
    
    fig = make_subplots(
        rows=2, cols=2,
        specs=[
            [{"type": "indicator"}, {"type": "bar"}],
            [{"type": "scatter"}, {"type": "bar"}]
        ],
        subplot_titles=("Risk Gauge", "Agent Scores", "Score Trend", "Risk Factors")
    )
    
    # 1. Risk Gauge (top-left)
    color_map = {"Low": "#10b981", "Medium": "#f59e0b", "High": "#ef4444"}
    color = color_map.get(risk_level, "#6b7280")
    
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=risk_score,
            title={'text': "Risk Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 50], 'color': "#d1f2eb"},
                    {'range': [50, 100], 'color': "#fecaca"}
                ],
            },
            number={'suffix': "%"}
        ),
        row=1, col=1
    )
    
    # 2. Agent Scores (top-right)
    agents_short = ["Platform", "Company", "Scam", "ML", "Quality"]
    scores = [
        confidence_breakdown.get("cross_platform_search", 0),
        confidence_breakdown.get("company_verification", 0),
        confidence_breakdown.get("scam_detection", 0),
        confidence_breakdown.get("ml_fake_probability", 0),
        confidence_breakdown.get("data_quality", 0)
    ]
    
    colors = ['#10b981' if s < 50 else '#f59e0b' if s < 75 else '#ef4444' for s in scores]
    
    fig.add_trace(
        go.Bar(x=agents_short, y=scores, marker_color=colors, showlegend=False),
        row=1, col=2
    )
    
    # 3. Score Trend (bottom-left)
    trend_data = list(range(len(scores)))
    fig.add_trace(
        go.Scatter(
            x=agents_short,
            y=scores,
            mode='lines+markers',
            name='Scores',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=10, color=colors),
            showlegend=False
        ),
        row=2, col=1
    )
    
    # 4. Risk Factors (bottom-right)
    risk_factors = ["Scam\nRisk", "ML\nRisk", "Verification\nGap", "Search\nGap", "Quality\nGap"]
    risk_values = [
        confidence_breakdown.get("scam_detection", 0),
        confidence_breakdown.get("ml_fake_probability", 0),
        100 - confidence_breakdown.get("company_verification", 0),
        100 - confidence_breakdown.get("cross_platform_search", 0),
        100 - confidence_breakdown.get("data_quality", 0)
    ]
    
    fig.add_trace(
        go.Bar(x=risk_factors, y=risk_values, marker_color='#ef4444', showlegend=False),
        row=2, col=2
    )
    
    # Update layout
    fig.update_yaxes(range=[0, 100], row=1, col=2)
    fig.update_yaxes(range=[0, 100], row=2, col=1)
    fig.update_yaxes(range=[0, 100], row=2, col=2)
    
    fig.update_layout(
        height=700,
        showlegend=False,
        margin=dict(l=60, r=40, t=80, b=60),
        font={'family': "Arial, sans-serif", 'size': 11},
        paper_bgcolor="white",
        plot_bgcolor="rgba(240, 245, 250, 0.5)"
    )
    
    return fig


def create_risk_level_indicator(risk_level: str, risk_score: float) -> Dict:
    """Create visual indicator data for risk level"""
    
    indicators = {
        "Low": {
            "emoji": "✅",
            "color": "#10b981",
            "bg_color": "#d1f2eb",
            "text_color": "#065f46",
            "border_color": "#10b981",
            "description": "Appears to be a legitimate job posting"
        },
        "Medium": {
            "emoji": "⚠️",
            "color": "#f59e0b",
            "bg_color": "#fef3c7",
            "text_color": "#92400e",
            "border_color": "#f59e0b",
            "description": "Some concerns detected - review carefully"
        },
        "High": {
            "emoji": "🚨",
            "color": "#ef4444",
            "bg_color": "#fee2e2",
            "text_color": "#991b1b",
            "border_color": "#ef4444",
            "description": "Likely a scam - avoid applying"
        }
    }
    
    return indicators.get(risk_level, indicators["Medium"])


def create_agent_summary_table(confidence_breakdown: Dict, agent_results: Dict = None) -> pd.DataFrame:
    """Create a summary table of all agent analyses"""
    
    summary_data = {
        'Agent': [
            'Cross-Platform Search',
            'Company Verification',
            'Scam Detection',
            'ML Fake Probability',
            'Data Quality'
        ],
        'Score': [
            confidence_breakdown.get('cross_platform_search', 0),
            confidence_breakdown.get('company_verification', 0),
            confidence_breakdown.get('scam_detection', 0),
            confidence_breakdown.get('ml_fake_probability', 0),
            confidence_breakdown.get('data_quality', 0)
        ],
        'Status': [],
        'Interpretation': [],
        'Reasoning': []
    }
    
    # Add status and interpretation
    interpretations = {
        'cross_platform_search': [
            'Not found on platforms',
            'Found on some platforms',
            'Verified on major platforms'
        ],
        'company_verification': [
            'Company not verified',
            'Partial verification',
            'Company fully verified'
        ],
        'scam_detection': [
            'No scam indicators',
            'Some suspicious elements',
            'Clear scam signals'
        ],
        'ml_fake_probability': [
            'Likely genuine',
            'Uncertain classification',
            'Likely fake'
        ],
        'data_quality': [
            'Poor data quality',
            'Moderate data quality',
            'Good data quality'
        ]
    }
    
    keys = ['cross_platform_search', 'company_verification', 'scam_detection', 
            'ml_fake_probability', 'data_quality']
    
    for i, key in enumerate(keys):
        score = summary_data['Score'][i]
        
        # Determine status emoji and interpretation
        if key in ['scam_detection', 'ml_fake_probability']:
            # Higher is worse for these
            if score < 33:
                status = "✅"
                interpretation = interpretations[key][0]
            elif score < 67:
                status = "⚠️"
                interpretation = interpretations[key][1]
            else:
                status = "🚨"
                interpretation = interpretations[key][2]
        else:
            # Higher is better for these
            if score >= 67:
                status = "✅"
                interpretation = interpretations[key][2]
            elif score >= 33:
                status = "⚠️"
                interpretation = interpretations[key][1]
            else:
                status = "🚨"
                interpretation = interpretations[key][0]
        
        summary_data['Status'].append(status)
        summary_data['Interpretation'].append(interpretation)
    
    # Add reasoning
    agent_key_map = {
        'cross_platform_search': 'cross_platform_search_agent',
        'company_verification': 'company_verification_agent', 
        'scam_detection': 'scam_detection_agent',
        'ml_fake_probability': 'ml_model_agent',  # Assuming this key
        'data_quality': 'data_quality_agent'  # Assuming this key
    }
    
    for key in keys:
        agent_key = agent_key_map.get(key)
        if agent_results and agent_key in agent_results:
            reasoning = agent_results[agent_key].get('reasoning', 'No reasoning available')
        else:
            reasoning = 'N/A'
        summary_data['Reasoning'].append(reasoning)
    
    return pd.DataFrame(summary_data)
