"use client";
import { useEffect, useState } from "react";

interface FyersData {
    lp: number; // Last Price
    ch: number; // Change
    chp: number; // Change Percentage
    h: number;
    l: number;
}
interface IndexCardProps {
    title: string;
    symbol: string;
}


const IndexCard = ({ title, symbol}: IndexCardProps) => {
  const [data, setData] = useState<FyersData | null>(null);
  const [status, setStatus] = useState("Connecting...");  
  
  useEffect(() => {
    const socket = new WebSocket(`ws://localhost:8000/ws/price?symbol=${symbol}`);
    socket.onopen = () => setStatus("Live");
    socket.onmessage = (event) => {
        const response = JSON.parse(event.data);
        console.log("Full Data Received:", response);
        if (response.data) setData(response.data);
    };
    socket.onerror = () => setStatus("Error");
    socket.onclose = () => setStatus("Offline");

    return () => socket.close();
    }, [symbol]);

    const isUp = ((data?.ch ?? 0) > 0);
    const isLive = (status === "Live");

    return (
        <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700 min-w-[250px] flex-1">
           <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-bold text-blue-400">{title}</h2>
            <div className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${isLive ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`}></span>
                <span className={`text-[12px] font-medium ${isLive ? 'text-green-400' : 'text-gray-500'}`}>
                    {isLive ? "Live" : "Closed"}
                </span>
            </div>
           </div>

           <div className={`text-4xl font-mono font-bold transition-colors duration-300 ${isUp ? 'text-green-400' : 'text-red-400'}`}>
                {data?.lp ? `₹${data.lp.toLocaleString(undefined, { minimumFractionDigits: 2 })}` : "---"}
           </div>
           {data && (
            <div className={`mt-2 text-sm ${isUp ? 'text-green-400' : 'text-red-400'}`}>
                <span className="font-bold">{isUp ? "▲" : "▼"}</span>
                <span>{data.ch.toFixed(2)}</span>
                <span className="bg-gray-700 px-2 py-0.5 rounded text-[11px]">
                    {data.chp}%
                </span>
            </div>
           )}
        </div>


    );
  
};

export default IndexCard;