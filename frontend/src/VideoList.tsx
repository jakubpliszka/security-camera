import React, { useEffect, useState } from "react";

const API_URL = "http://localhost:8000";

const VideoList: React.FC = () => {
    const [videos, setVideos] = useState<string[]>([]);
    const [loading, setLoading] = useState<boolean>(false);

    const fetchVideos = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/videos`);
            const data = await res.json();
            setVideos(data);
        } catch {
            setVideos([]);
        }
        setLoading(false);
    };

    useEffect(() => {
        fetchVideos();
    }, []);

    return (
        <div>
            <h2>Recorded Videos</h2>
            <button
                onClick={fetchVideos}
                disabled={loading}
                style={{ marginBottom: 12 }}
            >
                Refresh
            </button>
            {loading ? <div>Loading...</div> : null}
            <ul>
                {videos.length === 0 && !loading && <li>No videos found.</li>}
                {videos.map((video) => (
                    <li key={video} style={{ marginBottom: 8 }}>
                        {video}
                        <a
                            href={`${API_URL}/videos/${video}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{ marginLeft: 12 }}
                        >
                            Play/Download
                        </a>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default VideoList;
