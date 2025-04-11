import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import numpy.fft as fft

class CustomFilter:
    def __init__(self, filter_type="moving_average", window_size=10):
        self.filter_type = filter_type
        self.window_size = window_size
    
    def moving_average(self, signal, window_size):
        kernel = np.ones(window_size) / window_size
        padded_signal = np.pad(signal, (window_size//2, window_size//2), mode='edge')
        filtered = np.zeros_like(signal)
        
        for i in range(len(signal)):
            filtered[i] = np.sum(padded_signal[i:i+window_size] * kernel)
        
        return filtered
    
    def gaussian_filter(self, signal, window_size, sigma=1.0):
        x = np.linspace(-3*sigma, 3*sigma, window_size)
        kernel = np.exp(-0.5 * (x/sigma)**2)
        kernel = kernel / np.sum(kernel)
        
        padded_signal = np.pad(signal, (window_size//2, window_size//2), mode='edge')
        filtered = np.zeros_like(signal)
        
        for i in range(len(signal)):
            filtered[i] = np.sum(padded_signal[i:i+window_size] * kernel)
            
        return filtered
    
    def median_filter(self, signal, window_size):
        padded_signal = np.pad(signal, (window_size//2, window_size//2), mode='edge')
        filtered = np.zeros_like(signal)
        
        for i in range(len(signal)):
            filtered[i] = np.median(padded_signal[i:i+window_size])
            
        return filtered
    
    def high_pass_filter(self, signal, cutoff=0.1):
        signal_fft = fft.fft(signal)
        frequencies = fft.fftfreq(len(signal))
        mask = np.abs(frequencies) > cutoff
        filtered_fft = signal_fft * mask
        filtered = np.real(fft.ifft(filtered_fft))
        
        return filtered
    
    def low_pass_filter(self, signal, cutoff=0.1):
        signal_fft = fft.fft(signal)
        frequencies = fft.fftfreq(len(signal))
        mask = np.abs(frequencies) < cutoff
        filtered_fft = signal_fft * mask
        filtered = np.real(fft.ifft(filtered_fft))
        
        return filtered
        
    def apply(self, signal):
        if self.filter_type == "moving_average":
            return self.moving_average(signal, self.window_size)
        elif self.filter_type == "gaussian":
            return self.gaussian_filter(signal, self.window_size)
        elif self.filter_type == "median":
            return self.median_filter(signal, self.window_size)
        elif self.filter_type == "high_pass":
            return self.high_pass_filter(signal)
        elif self.filter_type == "low_pass":
            return self.low_pass_filter(signal)
        else:
            return signal

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.H1("Harmonic Signal Visualization with Noise and Filtering", 
           style={'textAlign': 'center', 'margin': '20px'}),
    
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H4("Signal Parameters"),
                
                html.Label("Signal Type:"),
                dcc.Dropdown(
                    id='signal-type',
                    options=[
                        {'label': 'Sine Wave', 'value': 'sine'},
                        {'label': 'Square Wave', 'value': 'square'},
                        {'label': 'Sawtooth', 'value': 'sawtooth'},
                        {'label': 'Triangle', 'value': 'triangle'}
                    ],
                    value='sine'
                ),
                
                html.Label("Amplitude:"),
                dcc.Slider(
                    id='amplitude-slider',
                    min=0.1,
                    max=5.0,
                    step=0.1,
                    value=1.0,
                    marks={i: str(i) for i in range(6)},
                ),
                
                html.Label("Frequency:"),
                dcc.Slider(
                    id='frequency-slider',
                    min=0.1,
                    max=5.0,
                    step=0.1,
                    value=1.0,
                    marks={i: str(i) for i in range(6)},
                ),
                
                html.Label("Phase:"),
                dcc.Slider(
                    id='phase-slider',
                    min=0,
                    max=2*np.pi,
                    step=0.1,
                    value=0,
                    marks={0: '0', round(np.pi): 'π', round(2*np.pi): '2π'},
                ),
                
                html.H4("Noise Parameters", style={'marginTop': '20px'}),
                
                html.Label("Noise Type:"),
                dcc.Dropdown(
                    id='noise-type',
                    options=[
                        {'label': 'Gaussian', 'value': 'gaussian'},
                        {'label': 'Uniform', 'value': 'uniform'},
                        {'label': 'None', 'value': 'none'}
                    ],
                    value='gaussian'
                ),
                
                html.Label("Noise Mean:"),
                dcc.Slider(
                    id='noise-mean-slider',
                    min=-1.0,
                    max=1.0,
                    step=0.1,
                    value=0.0,
                    marks={-1: '-1', 0: '0', 1: '1'},
                ),
                
                html.Label("Noise Variance:"),
                dcc.Slider(
                    id='noise-variance-slider',
                    min=0.01,
                    max=1.0,
                    step=0.01,
                    value=0.2,
                    marks={0: '0', 0.5: '0.5', 1: '1'},
                ),
                
                html.H4("Filter Parameters", style={'marginTop': '20px'}),
                
                html.Label("Filter Type:"),
                dcc.Dropdown(
                    id='filter-type',
                    options=[
                        {'label': 'Moving Average', 'value': 'moving_average'},
                        {'label': 'Gaussian', 'value': 'gaussian'},
                        {'label': 'Median', 'value': 'median'},
                        {'label': 'Low-Pass', 'value': 'low_pass'},
                        {'label': 'High-Pass', 'value': 'high_pass'},
                        {'label': 'None', 'value': 'none'}
                    ],
                    value='moving_average'
                ),
                
                html.Label("Window Size:"),
                dcc.Slider(
                    id='window-size-slider',
                    min=3,
                    max=51,
                    step=2,
                    value=11,
                    marks={3: '3', 11: '11', 21: '21', 31: '31', 41: '41', 51: '51'},
                ),
                
                html.Div([
                    dbc.Button("Reset All", id="reset-button", color="danger", className="me-1", style={'marginTop': '20px'}),
                    dbc.Button("Apply Settings", id="apply-button", color="primary", className="me-1", style={'marginTop': '20px'})
                ], style={'textAlign': 'center'})
            ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px'})
        ], width=3),
        
        dbc.Col([
            dcc.Graph(id='time-domain-graph', style={'height': '300px'}),
            dcc.Graph(id='frequency-domain-graph', style={'height': '300px'}),
            dbc.Card([
                dbc.CardBody([
                    html.H5("Display Options"),
                    dbc.Checklist(
                        id="signal-checklist",
                        options=[
                            {"label": "Show Clean Signal", "value": "clean"},
                            {"label": "Show Noisy Signal", "value": "noisy"},
                            {"label": "Show Filtered Signal", "value": "filtered"}
                        ],
                        value=["clean", "noisy", "filtered"],
                        inline=True
                    )
                ])
            ], style={'marginTop': '20px'})
        ], width=9)
    ])
])

def generate_signal(t, signal_type, amplitude, frequency, phase):
    if signal_type == 'sine':
        return amplitude * np.sin(2 * np.pi * frequency * t + phase)
    elif signal_type == 'square':
        return amplitude * np.sign(np.sin(2 * np.pi * frequency * t + phase))
    elif signal_type == 'sawtooth':
        return amplitude * ((2 * ((frequency * t + phase / (2 * np.pi)) % 1)) - 1)
    elif signal_type == 'triangle':
        return amplitude * (2 * np.abs(2 * ((frequency * t + phase / (2 * np.pi)) % 1) - 1) - 1)

def generate_noise(size, noise_type, mean, variance):
    if noise_type == 'gaussian':
        return np.random.normal(mean, np.sqrt(variance), size)
    elif noise_type == 'uniform':
        return np.random.uniform(mean - np.sqrt(3*variance), mean + np.sqrt(3*variance), size)
    elif noise_type == 'none':
        return np.zeros(size)

@app.callback(
    [Output('time-domain-graph', 'figure'),
     Output('frequency-domain-graph', 'figure')],
    [Input('apply-button', 'n_clicks'),
     Input('signal-checklist', 'value')],
    [State('signal-type', 'value'),
     State('amplitude-slider', 'value'),
     State('frequency-slider', 'value'),
     State('phase-slider', 'value'),
     State('noise-type', 'value'),
     State('noise-mean-slider', 'value'),
     State('noise-variance-slider', 'value'),
     State('filter-type', 'value'),
     State('window-size-slider', 'value')]
)
def update_graphs(n_clicks, visible_signals, signal_type, amplitude, frequency, phase, 
                 noise_type, noise_mean, noise_variance, filter_type, window_size):
    t = np.linspace(0, 10, 1000)
    
    clean_signal = generate_signal(t, signal_type, amplitude, frequency, phase)
    noise = generate_noise(len(t), noise_type, noise_mean, noise_variance)
    noisy_signal = clean_signal + noise
    
    custom_filter = CustomFilter(filter_type=filter_type, window_size=window_size)
    filtered_signal = custom_filter.apply(noisy_signal) if filter_type != 'none' else noisy_signal
    
    fig_time = go.Figure()
    
    if 'clean' in visible_signals:
        fig_time.add_trace(go.Scatter(x=t, y=clean_signal, mode='lines', name='Clean Signal', line=dict(color='green')))
    
    if 'noisy' in visible_signals:
        fig_time.add_trace(go.Scatter(x=t, y=noisy_signal, mode='lines', name='Noisy Signal', line=dict(color='red', dash='dash')))
    
    if 'filtered' in visible_signals:
        fig_time.add_trace(go.Scatter(x=t, y=filtered_signal, mode='lines', name='Filtered Signal', line=dict(color='blue')))
    
    fig_time.update_layout(
        title='Time Domain Signal',
        xaxis_title='Time (s)',
        yaxis_title='Amplitude',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    freqs = fft.fftfreq(len(t), t[1] - t[0])
    mask = freqs >= 0
    
    clean_fft = np.abs(fft.fft(clean_signal))
    noisy_fft = np.abs(fft.fft(noisy_signal))
    filtered_fft = np.abs(fft.fft(filtered_signal))
    
    fig_freq = go.Figure()
    
    if 'clean' in visible_signals:
        fig_freq.add_trace(go.Scatter(x=freqs[mask], y=clean_fft[mask], mode='lines', name='Clean Signal Spectrum', line=dict(color='green')))
    
    if 'noisy' in visible_signals:
        fig_freq.add_trace(go.Scatter(x=freqs[mask], y=noisy_fft[mask], mode='lines', name='Noisy Signal Spectrum', line=dict(color='red', dash='dash')))
    
    if 'filtered' in visible_signals:
        fig_freq.add_trace(go.Scatter(x=freqs[mask], y=filtered_fft[mask], mode='lines', name='Filtered Signal Spectrum', line=dict(color='blue')))
    
    fig_freq.update_layout(
        title='Frequency Domain Analysis',
        xaxis_title='Frequency (Hz)',
        yaxis_title='Magnitude',
        xaxis=dict(range=[0, 5]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig_time, fig_freq

@app.callback(
    [Output('signal-type', 'value'),
     Output('amplitude-slider', 'value'),
     Output('frequency-slider', 'value'),
     Output('phase-slider', 'value'),
     Output('noise-type', 'value'),
     Output('noise-mean-slider', 'value'),
     Output('noise-variance-slider', 'value'),
     Output('filter-type', 'value'),
     Output('window-size-slider', 'value'),
     Output('signal-checklist', 'value')],
    Input('reset-button', 'n_clicks')
)
def reset_values(n_clicks):
    return 'sine', 1.0, 1.0, 0, 'gaussian', 0.0, 0.2, 'moving_average', 11, ["clean", "noisy", "filtered"]

if __name__ == '__main__':
    app.run_server(debug=True)
