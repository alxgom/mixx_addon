# plotly_theme.py
import plotly.io as pio

def register_swing_theme():
    custom_template = dict(
        layout=dict(
            paper_bgcolor="rgba(1,1,1,0.01)",  # Matches your Dash body background
            plot_bgcolor="rgba(0,0,0,0)",   # Matches your card background
            font=dict(
                family="Quicksand",
                color="#3A3A3A"
            ),
            title=dict(
                font=dict(
                    family="Raleway",
                    color="#2C3E50"
                )
            ),
            xaxis=dict(
                gridcolor="#E6E2D3",
                zerolinecolor="#E6E2D3",
                showline=True,
                linecolor="#CBA135",
                ticks="outside",
                tickcolor="#CBA135",
            ),
            yaxis=dict(
                gridcolor="#E6E2D3",
                zerolinecolor="#E6E2D3",
                showline=True,
                linecolor="#CBA135",
                ticks="outside",
                tickcolor="#CBA135",
            ),
            legend=dict(
                bgcolor="#FFFDF8",
                bordercolor="#CBA135",
                borderwidth=1,
                font=dict(color="#3A3A3A")
            )
            # Add more styling if you want
        )
    )

    pio.templates["swing_theme"] = custom_template
    pio.templates.default = "swing_theme"
