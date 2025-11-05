BMHC_COLORS = {
    'primary': '#1f4e79',
    'secondary': '#8cc8ff', 
    'accent': '#ff6b35',
    'neutral': '#2c3e50',
    'light_gray': '#ecf0f1'
}

BMHC_PALETTE = list(BMHC_COLORS.values())

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

def apply_seaborn_style():
    """Apply BMHC styling to seaborn"""
    import seaborn as sns
    sns.set_style("whitegrid")
    sns.set_palette(BMHC_PALETTE)

def apply_plotly_style(fig):
    """Apply BMHC styling to plotly figure"""
    fig.update_layout(
        font_family="Arial",
        font_color=BMHC_COLORS['neutral'],
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    return fig