import React, { useState } from "react";

const API_URL = "http://localhost:8000";

const ControlPanel: React.FC = () => {
    const [status, setStatus] = useState<string>("Unknown");
    const [loading, setLoading] = useState<boolean>(false);

    const handleStart = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/start`, { method: "POST" });
            const data = await res.json();
            setStatus(
                data.status === "started" || data.status === "already running"
                    ? "Running"
                    : "Stopped"
            );
        } catch {
            setStatus("Error");
        }
        setLoading(false);
    };

    const handleStop = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/stop`, { method: "POST" });
            const data = await res.json();
            setStatus(
                data.status === "stopped" || data.status === "already stopped"
                    ? "Stopped"
                    : "Running"
            );
        } catch {
            setStatus("Error");
        }
        setLoading(false);
    };

    return (
        <div style={{ marginBottom: 24 }}>
            <h2>Security Camera Control</h2>
            <button
                onClick={handleStart}
                disabled={loading || status === "Running"}
            >
                Start
            </button>
            <button
                onClick={handleStop}
                disabled={loading || status === "Stopped"}
                style={{ marginLeft: 8 }}
            >
                Stop
            </button>
            <div style={{ marginTop: 12 }}>
                Status: <b>{status}</b>
            </div>
        </div>
    );
};

export default ControlPanel;
