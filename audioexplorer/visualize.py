import base64
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from io import BytesIO


def test_scatter() -> go.Figure:
    N = 100
    random_x = np.random.randn(N)
    random_y = np.random.randn(N)

    # Create a trace
    trace = go.Scatter(
        x=random_x,
        y=random_y,
        mode='markers'
    )

    # Plot and embed in ipython notebook!
    fig = go.Figure(data=[trace])
    return fig


def make_scatterplot(x, y, customdata=None, text=None, opacity=0.8) -> go.Figure:

    trace0 = go.Scatter(
        x=x,
        y=y,
        mode='markers',
        marker=dict(
            size=4,
            color='red',
            opacity=opacity),
        customdata=customdata,
        text=text,
        hoverinfo='text'
    )

    layout = go.Layout(
        autosize=True,
        hovermode='closest',
        xaxis=dict(
            title='x',
            ticklen=5,
            zeroline=False,
            gridwidth=2,
        ),
        yaxis=dict(
            title='y',
            ticklen=5,
            zeroline=False,
            gridwidth=2,
        ),
        showlegend=False
    )
    fig = go.Figure(data=[trace0], layout=layout)
    return fig


def specgram_base64(signal: np.ndarray, fs, start, end) -> str:
    f, ax = plt.subplots()
    # xticks = np.linspace(start, end, 8).round(2)
    # ax.set_xticklabels(xticks)

    plt.specgram(signal, Fs=fs, xextent=[start, end])
    plt.xlabel('Time [s]')
    plt.ylabel('Frequency [Hz]')
    plt.title('Spectrogram')
    ax.axvline(x=start + 0.4, color='red', alpha=0.3)
    ax.axvline(x=end - 0.4, color='red', alpha=0.3)

    stream = BytesIO()
    plt.savefig(stream, format='png')
    stream.seek(0)
    base64_jpg = base64.b64encode(stream.read()).decode("utf-8")
    return base64_jpg
