import pandas as pd
import plotly.graph_objects as go


def create_sales_line_chart(sales_data: pd.DataFrame) -> go.Figure:
    """
    Crée un graphique linéaire avec double axe Y :
    - Axe gauche  (bleu)   : nombre de ventes
    - Axe droit   (orange) : montant des ventes
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=sales_data["date"],
        y=sales_data["number_sales"],
        name="Number of Sales",
        line=dict(color="#1f77b4"),
        yaxis="y1",
    ))

    fig.add_trace(go.Scatter(
        x=sales_data["date"],
        y=sales_data["amount_sales"],
        name="Amount Sold ($)",
        line=dict(color="#ff7f0e"),
        yaxis="y2",
    ))

    fig.update_layout(
        xaxis=dict(title="Date"),
        yaxis=dict(title="Number of Sales", side="left"),
        yaxis2=dict(
            title="Amount Sold ($)",
            overlaying="y",
            side="right",
        ),
        legend=dict(x=0, y=1.1, orientation="h"),
    )

    return fig
