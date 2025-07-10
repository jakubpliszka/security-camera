import React from "react";
import "./App.css";
import ControlPanel from "./ControlPanel";
import VideoList from "./VideoList";
import VideoStream from "./VideoStream";

function App() {
  return (
    <div>
      <VideoStream />
      {/* <ControlPanel /> */}
      <VideoList />
    </div>
  );
}

export default App;
