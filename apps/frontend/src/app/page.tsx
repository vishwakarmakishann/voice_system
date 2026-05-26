"use client";

import {
  LiveKitRoom,
  RoomAudioRenderer,
  VoiceAssistantControlBar,
  useRemoteParticipants
} from "@livekit/components-react";
import { useCallback, useState, useEffect } from "react";
import "@livekit/components-styles";

function ConnectionStatus() {
  const participants = useRemoteParticipants();
  const isAgentConnected = participants.length > 0;

  if (!isAgentConnected) {
    return (
      <div className="w-32 h-32 rounded-full bg-yellow-500/10 flex items-center justify-center border border-yellow-500/20 animate-pulse">
        <span className="text-yellow-400 font-medium text-center text-sm px-2">Connecting to AI...</span>
      </div>
    );
  }

  return (
    <div className="w-32 h-32 rounded-full bg-blue-500/10 flex items-center justify-center border border-blue-500/20 shadow-[0_0_30px_rgba(59,130,246,0.3)]">
      <span className="text-blue-400 font-medium text-center text-sm">Listening...</span>
    </div>
  );
}

export default function Home() {
  const [token, setToken] = useState("");
  const [authToken, setAuthToken] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLogin, setIsLogin] = useState(true);
  const [error, setError] = useState("");
  
  useEffect(() => {
    const savedToken = localStorage.getItem("access_token");
    if (savedToken) {
      setAuthToken(savedToken);
    }
  }, []);

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    
    try {
      const endpoint = isLogin ? "/auth/login" : "/auth/register";
      let body: any;
      let headers: any = {};
      
      if (isLogin) {
        body = new URLSearchParams();
        body.append('username', username);
        body.append('password', password);
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
      } else {
        body = JSON.stringify({ username, password });
        headers['Content-Type'] = 'application/json';
      }

      const res = await fetch(`http://localhost:8000${endpoint}`, {
        method: "POST",
        headers,
        body
      });
      
      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.detail || "Authentication failed");
      }
      
      // If registering, it returns the user object, we still need to login
      if (!isLogin) {
        setIsLogin(true);
        setError("Registration successful! Please log in.");
        return;
      }
      
      setAuthToken(data.access_token);
      localStorage.setItem("access_token", data.access_token);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const logout = () => {
    setAuthToken("");
    setToken("");
    localStorage.removeItem("access_token");
  };

  const connect = useCallback(async () => {
    try {
        const response = await fetch("http://localhost:8000/livekit/token", {
          method: "POST",
          headers: { 
              "Content-Type": "application/json",
              "Authorization": `Bearer ${authToken}`
          }
        });
        
      if (!response.ok) {
          if (response.status === 401) {
              logout();
          }
          throw new Error("Failed to get token");
      }
      
      const data = await response.json();
      setToken(data.token);
    } catch (e) {
      console.error("Failed to connect:", e);
    }
  }, [authToken]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-zinc-950 text-white">
      <div className="max-w-2xl w-full flex flex-col items-center">
        <h1 className="text-4xl font-bold mb-8 bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
          Realtime Voice AI
        </h1>

        {!authToken ? (
            <div className="bg-black/50 p-8 rounded-2xl border border-white/10 w-full max-w-md backdrop-blur-md shadow-2xl">
                <h2 className="text-2xl font-semibold mb-6 text-center">{isLogin ? "Welcome Back" : "Create Account"}</h2>
                {error && <p className="text-red-400 text-sm mb-4 text-center">{error}</p>}
                
                <form onSubmit={handleAuth} className="flex flex-col gap-4">
                    <div>
                        <label className="block text-sm text-gray-400 mb-1">Username</label>
                        <input 
                            type="text" 
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:outline-none focus:border-blue-500 transition-colors"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm text-gray-400 mb-1">Password</label>
                        <input 
                            type="password" 
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:outline-none focus:border-blue-500 transition-colors"
                            required
                        />
                    </div>
                    <button type="submit" className="w-full py-3 bg-blue-600 hover:bg-blue-500 rounded-lg font-medium transition-colors mt-2 shadow-lg shadow-blue-500/20">
                        {isLogin ? "Sign In" : "Register"}
                    </button>
                </form>
                
                <p className="mt-6 text-center text-sm text-gray-400">
                    {isLogin ? "Don't have an account?" : "Already have an account?"}{" "}
                    <button onClick={() => { setIsLogin(!isLogin); setError(""); }} className="text-blue-400 hover:text-blue-300">
                        {isLogin ? "Sign up" : "Log in"}
                    </button>
                </p>
            </div>
        ) : !token ? (
            <div className="flex flex-col items-center gap-6">
              <button
                onClick={connect}
                className="px-8 py-4 bg-white/10 hover:bg-white/20 border border-white/20 rounded-xl font-medium transition-all shadow-lg backdrop-blur-sm"
              >
                Connect to Audio Room
              </button>
              <button onClick={logout} className="text-sm text-gray-400 hover:text-white transition-colors">
                  Sign out
              </button>
          </div>
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
            <div className="flex-1 flex flex-col items-center justify-center relative">
              <button onClick={logout} className="absolute top-4 right-4 text-sm text-gray-400 hover:text-white transition-colors z-10 bg-black/50 px-3 py-1 rounded-full border border-white/10">
                  Disconnect & Sign out
              </button>
              <ConnectionStatus />
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
