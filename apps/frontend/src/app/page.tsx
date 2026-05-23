"use client";

import {
  LiveKitRoom,
  RoomAudioRenderer,
  VoiceAssistantControlBar
} from "@livekit/components-react";
import { useCallback, useState } from "react";
import "@livekit/components-styles";

export default function Home() {
  const [token, setToken] = useState("");

  const connect = useCallback(async () => {
    try {
        // Persist the user ID so the memory system recognizes the same user across sessions
        let storedUserId = localStorage.getItem("voice_user_id");
        if (!storedUserId) {
          storedUserId = "user-" + Math.floor(Math.random() * 100000);
          localStorage.setItem("voice_user_id", storedUserId);
        }

        const response = await fetch("http://localhost:8000/livekit/token", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user_id: storedUserId,
            room_name: "voice-room",
          }),
        });
      const data = await response.json();
      setToken(data.token);
    } catch (e) {
      console.error("Failed to connect:", e);
    }
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-zinc-950 text-white">
      <div className="max-w-2xl w-full flex flex-col items-center">
        <h1 className="text-4xl font-bold mb-8 bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
          Realtime Voice AI
        </h1>

        {!token ? (
          <button
            onClick={connect}
            className="px-8 py-4 bg-white/10 hover:bg-white/20 border border-white/20 rounded-xl font-medium transition-all shadow-lg backdrop-blur-sm"
          >
            Connect to Audio Room
          </button>
        ) : (
          <LiveKitRoom
            video={false}
            audio={true}
            token={token}
            serverUrl="ws://localhost:7885"
            data-lk-theme="default"
            className="w-full h-[400px] border border-white/10 rounded-2xl bg-black/50 overflow-hidden flex flex-col shadow-2xl"
            onDisconnected={() => setToken("")}
          >
            <RoomAudioRenderer />
            <div className="flex-1 flex flex-col items-center justify-center">
              <div className="w-32 h-32 rounded-full bg-blue-500/10 flex items-center justify-center border border-blue-500/20 animate-pulse">
                <span className="text-blue-400 font-medium">Connected</span>
              </div>
            </div>
            <div className="p-4 border-t border-white/10 bg-black/40 flex justify-center gap-4">
              <VoiceAssistantControlBar />
            </div>
          </LiveKitRoom>
        )}
      </div>
    </main>
  );
}
