#################################################
##########  PRIMARY BRANDING COLORS    ##########
#################################################
BMHC_COLORS = {
    'primary': '#1f4e79',
    'secondary': '#8cc8ff', 
    'accent': '#ff6b35',
    'neutral': '#2c3e50',
    'light_gray': '#ecf0f1',
    'gold': '#d0a53f'
}

BMHC_PALETTE = list(BMHC_COLORS.values())

###################################################
##########  MATPLOTLIB STLYING FORMAT    ##########
###################################################
def apply_matplotlib_style():
    """Apply BMHC styling to matplotlib"""
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        'font.family': 'Arial',
        'font.size': 12,
        'axes.facecolor': 'white',
        'figure.facecolor': 'white',
        'axes.prop_cycle': plt.cycler('color', BMHC_PALETTE)
    })

################################################
##########  SEABORN STLYING FORMAT    ##########
################################################
def apply_seaborn_style():
    """Apply BMHC styling to seaborn"""
    import seaborn as sns
    sns.set_style("whitegrid")
    sns.set_palette(BMHC_PALETTE)


##############################################
##########  PLOTY STLYING FORMAT    ##########
##############################################
def apply_plotly_style(fig):
    """Apply BMHC styling to plotly figure"""
    fig.update_layout(
        font_family="Inter",
        font_color=BMHC_COLORS['neutral'],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="white",
        xaxis_showgrid=True,
        yaxis_showgrid=True,
        xaxis_gridcolor='#d3d3d3',
        yaxis_gridcolor='#d3d3d3',
        xaxis_gridwidth=1,
        yaxis_gridwidth=1
    )
    
    fig.add_annotation(
        text="©BMHC",
        x=0, y=-0.15, xref="paper", yref="paper",
        xanchor="left",
        width=None,
        font_size=12, font_color="#f8f8f8",
        bgcolor='gray', showarrow=False
    )
    fig.add_annotation(
        text="Source: Black Men's Health Data Team",
        x=1, y=-0.15, xref="paper", yref="paper",
        xanchor="right",
        width=None,
        font_size=12, font_color='#f8f8f8',
        bgcolor='gray', showarrow=False
    )
    return fig