import React from "react";

const VideoStream: React.FC = () => {
  const streamUrl = "http://localhost:8000/video_feed";

  return (
    <div style={{ textAlign: "center" }}>
      <h2>Live Camera Feed</h2>
      <img
        src={streamUrl}
        alt="Live Video Stream"
        style={{
          maxWidth: "100%",
          border: "2px solid #ccc",
          borderRadius: "8px",
        }}
      />
    </div>
  );
};

export default VideoStream;
