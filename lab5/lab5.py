import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
from scipy import signal
import matplotlib.gridspec as gridspec

class HarmonicVisualizer:
    def __init__(self):
        self.amplitude = 1.0
        self.frequency = 1.0
        self.phase = 0.0
        self.noise_mean = 0.0
        self.noise_covariance = 0.2
        self.show_noise = True
        self.show_filtered = True
        
        self.filter_order = 3
        self.cutoff_freq = 2.0
        
        self.t = np.linspace(0, 10, 1000)
        
        self.clean_signal = self.generate_harmonic()
        self.noise = np.random.normal(self.noise_mean, self.noise_covariance, len(self.t))
        self.noisy_signal = self.clean_signal + self.noise
        self.filtered_signal = self.filter_signal()
        
    def generate_harmonic(self):
        return self.amplitude * np.sin(2 * np.pi * self.frequency * self.t + self.phase)
    
    def filter_signal(self):
        b, a = signal.butter(self.filter_order, self.cutoff_freq * 2 / 100)
        return signal.filtfilt(b, a, self.noisy_signal)
    
    def setup_ui(self):
        self.fig = plt.figure(figsize=(12, 8))
        gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
        
        self.ax = self.fig.add_subplot(gs[0])
        
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Amplitude')
        self.ax.set_title('Harmonic Visualization with Noise and Filtering')
        
        self.clean_line, = self.ax.plot(self.t, self.clean_signal, 'g-', label='Clean Harmonic')
        self.noisy_line, = self.ax.plot(self.t, self.noisy_signal, 'r-', alpha=0.5, label='Noisy Harmonic')
        self.filtered_line, = self.ax.plot(self.t, self.filtered_signal, 'b-', label='Filtered Harmonic')
        
        self.ax.legend()
        
        controls_ax = self.fig.add_subplot(gs[1])
        controls_ax.set_visible(False)
        
        ax_amplitude = plt.axes([0.15, 0.35, 0.65, 0.03])
        ax_frequency = plt.axes([0.15, 0.3, 0.65, 0.03])
        ax_phase = plt.axes([0.15, 0.25, 0.65, 0.03])
        ax_noise_mean = plt.axes([0.15, 0.2, 0.65, 0.03])
        ax_noise_cov = plt.axes([0.15, 0.15, 0.65, 0.03])
        ax_filter_order = plt.axes([0.15, 0.1, 0.3, 0.03])
        ax_cutoff_freq = plt.axes([0.5, 0.1, 0.3, 0.03])
        
        self.slider_amp = Slider(ax_amplitude, 'Amplitude', 0.1, 5.0, valinit=self.amplitude)
        self.slider_freq = Slider(ax_frequency, 'Frequency', 0.1, 5.0, valinit=self.frequency)
        self.slider_phase = Slider(ax_phase, 'Phase', 0.0, 2*np.pi, valinit=self.phase)
        self.slider_noise_mean = Slider(ax_noise_mean, 'Noise Mean', -1.0, 1.0, valinit=self.noise_mean)
        self.slider_noise_cov = Slider(ax_noise_cov, 'Noise Variance', 0.01, 1.0, valinit=self.noise_covariance)
        self.slider_filter_order = Slider(ax_filter_order, 'Filter Order', 1, 10, valinit=self.filter_order, valstep=1)
        self.slider_cutoff_freq = Slider(ax_cutoff_freq, 'Cutoff Frequency', 0.1, 10.0, valinit=self.cutoff_freq)
        
        ax_reset = plt.axes([0.8, 0.025, 0.1, 0.04])
        self.button_reset = Button(ax_reset, 'Reset')
        
        ax_check = plt.axes([0.05, 0.025, 0.15, 0.1])
        self.check_buttons = CheckButtons(ax_check, ['Show Noise', 'Show Filtered'], [self.show_noise, self.show_filtered])
        
        self.slider_amp.on_changed(self.update_harmonic)
        self.slider_freq.on_changed(self.update_harmonic)
        self.slider_phase.on_changed(self.update_harmonic)
        self.slider_noise_mean.on_changed(self.update_noise)
        self.slider_noise_cov.on_changed(self.update_noise)
        self.slider_filter_order.on_changed(self.update_filter)
        self.slider_cutoff_freq.on_changed(self.update_filter)
        self.button_reset.on_clicked(self.reset)
        self.check_buttons.on_clicked(self.update_visibility)
        
        plt.figtext(0.5, 0.01, "Instructions: Use sliders to adjust parameters, checkboxes to toggle noise and filter display.", 
                   ha="center", bbox={"facecolor":"lightgray", "alpha":0.5, "pad":5})
        
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.45)
    
    def update_harmonic(self, val):
        self.amplitude = self.slider_amp.val
        self.frequency = self.slider_freq.val
        self.phase = self.slider_phase.val
        
        self.clean_signal = self.generate_harmonic()
        self.noisy_signal = self.clean_signal + self.noise  # Use existing noise
        self.filtered_signal = self.filter_signal()
        
        self.update_plot()
    
    def update_noise(self, val):
        self.noise_mean = self.slider_noise_mean.val
        self.noise_covariance = self.slider_noise_cov.val
        
        self.noise = np.random.normal(self.noise_mean, self.noise_covariance, len(self.t))
        self.noisy_signal = self.clean_signal + self.noise
        self.filtered_signal = self.filter_signal()
        
        self.update_plot()
    
    def update_filter(self, val):
        self.filter_order = int(self.slider_filter_order.val)
        self.cutoff_freq = self.slider_cutoff_freq.val
        
        self.filtered_signal = self.filter_signal()
        
        self.update_plot()
    
    def update_visibility(self, label):
        if label == 'Show Noise':
            self.show_noise = not self.show_noise
        elif label == 'Show Filtered':
            self.show_filtered = not self.show_filtered
        
        self.update_plot()
    
    def update_plot(self):
        self.clean_line.set_ydata(self.clean_signal)
        
        if self.show_noise:
            self.noisy_line.set_ydata(self.noisy_signal)
            self.noisy_line.set_visible(True)
        else:
            self.noisy_line.set_visible(False)
        
        if self.show_filtered:
            self.filtered_line.set_ydata(self.filtered_signal)
            self.filtered_line.set_visible(True)
        else:
            self.filtered_line.set_visible(False)
        
        self.ax.relim()
        self.ax.autoscale_view()
        
        self.fig.canvas.draw_idle()
    
    def reset(self, event):
        self.slider_amp.reset()
        self.slider_freq.reset()
        self.slider_phase.reset()
        self.slider_noise_mean.reset()
        self.slider_noise_cov.reset()
        self.slider_filter_order.reset()
        self.slider_cutoff_freq.reset()
        
        self.amplitude = 1.0
        self.frequency = 1.0
        self.phase = 0.0
        self.noise_mean = 0.0
        self.noise_covariance = 0.2
        self.filter_order = 3
        self.cutoff_freq = 2.0
        
        self.clean_signal = self.generate_harmonic()
        self.noise = np.random.normal(self.noise_mean, self.noise_covariance, len(self.t))
        self.noisy_signal = self.clean_signal + self.noise
        self.filtered_signal = self.filter_signal()
        
        self.show_noise = True
        self.show_filtered = True
        
        if not self.check_buttons.get_status()[0]:
            self.check_buttons.set_active(0)  
        if not self.check_buttons.get_status()[1]:
            self.check_buttons.set_active(1)  
        
        self.update_plot()
    
    def run(self):
        self.setup_ui()
        plt.show()

if __name__ == "__main__":
    visualizer = HarmonicVisualizer()
    visualizer.run()
