import streamlit as st
import numpy as np
import time
import random
import matplotlib.pyplot as plt

st.set_page_config(page_title="Cross-Layer Video Transmission Simulator", layout="wide")

st.title("📡 Real-Time Cross-Layer Optimized Video Transmission Simulator")
st.markdown("Simulating how cross-layer optimization impacts video quality, delay, and energy without datasets or models.")

# -------------------------
# USER INPUTS
# -------------------------
col1, col2, col3 = st.columns(3)
bandwidth = col1.slider("Available Bandwidth (MHz)", 1, 20, 10)
snr = col2.slider("Signal-to-Noise Ratio (dB)", 0, 30, 15)
packet_size = col3.slider("Packet Size (KB)", 1, 10, 5)

video_bitrate = st.slider("Initial Video Bitrate (Mbps)", 1, 20, 8)
frames = st.slider("Total Frames to Simulate", 10, 200, 50)

# -------------------------
# SIMULATION FUNCTION
# -------------------------
def simulate_cross_layer(bw, snr_db, pkt_size, bitrate, total_frames):
    snr_lin = 10 ** (snr_db / 10)
    capacity = bw * 1e6 * np.log2(1 + snr_lin)  # Shannon capacity

    results = {"time": [], "bitrate": [], "psnr": [], "delay": [], "energy": [], "throughput": []}
    queue_length = 0
    power_tx = 0.1  # W, constant for simplicity

    for t in range(total_frames):
        # Vary channel randomly ±20%
        capacity_t = capacity * random.uniform(0.8, 1.2)
        adaptive_bitrate = min(bitrate * 1e6, capacity_t * 0.9)  # Application layer decision

        # Transport Layer: congestion control
        cwnd = min(10, max(1, int(capacity_t / (pkt_size * 1024 * 8))))

        # Network Layer: routing overhead (~5%)
        routing_eff = 0.95

        throughput = adaptive_bitrate * routing_eff

        # Link Layer: ARQ retransmission cost (~1.1 if errors)
        link_eff = 1.0 if random.random() > 0.1 else 0.9
        throughput *= link_eff

        # Delay (queue + transmission)
        queue_length += max(0, adaptive_bitrate - capacity_t)
        delay = queue_length / (capacity_t + 1e-9)

        # Physical Layer: Energy consumption
        energy = power_tx * (pkt_size * 8 / capacity_t)

        # Video Quality: Approx PSNR
        mse = max(1, 255**2 / (throughput / (bitrate * 1e6) + 0.1))
        psnr = 20 * np.log10(255 / np.sqrt(mse))

        # Store results
        results["time"].append(t)
        results["bitrate"].append(adaptive_bitrate / 1e6)
        results["psnr"].append(psnr)
        results["delay"].append(delay)
        results["energy"].append(energy)
        results["throughput"].append(throughput / 1e6)

        time.sleep(0.01)

    return results

# -------------------------
# RUN SIMULATION
# -------------------------
if st.button("🚀 Run Simulation"):
    with st.spinner("Running cross-layer optimization simulation..."):
        results = simulate_cross_layer(bandwidth, snr, packet_size, video_bitrate, frames)

    st.success("✅ Simulation Completed!")

    # -------------------------
    # PLOTS
    # -------------------------
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    axs[0,0].plot(results["time"], results["bitrate"], label="Adaptive Bitrate (Mbps)")
    axs[0,0].set_title("Adaptive Video Bitrate")

    axs[0,1].plot(results["time"], results["psnr"], color='orange', label="PSNR (dB)")
    axs[0,1].set_title("Video Quality (PSNR)")

    axs[1,0].plot(results["time"], results["delay"], color='green', label="Delay (s)")
    axs[1,0].set_title("End-to-End Delay")

    axs[1,1].plot(results["time"], results["energy"], color='red', label="Energy (J)")
    axs[1,1].set_title("Energy per Packet")

    for ax in axs.flat:
        ax.legend()
        ax.grid(True)

    st.pyplot(fig)

    # -------------------------
    # SUMMARY
    # -------------------------
    st.subheader("📊 Simulation Summary")
    colA, colB, colC, colD = st.columns(4)
    colA.metric("Avg Bitrate", f"{np.mean(results['bitrate']):.2f} Mbps")
    colB.metric("Avg PSNR", f"{np.mean(results['psnr']):.2f} dB")
    colC.metric("Avg Delay", f"{np.mean(results['delay']):.4f} s")
    colD.metric("Avg Energy", f"{np.mean(results['energy']):.6f} J")
