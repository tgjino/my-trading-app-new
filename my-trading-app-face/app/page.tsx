"use client";
import IndexCard from "@/Components/IndexCard";


export default function Home() {

  return (
    <main className="flex min-h-screen flex-col items-center p-12 bg-gray-900 text-white">
        <h1 className="text-3xl font-bold mb-10 text-gray-400">Market Dashboard</h1>

      <div className="flex flex-wrap gap-6 w-full max-w-5xl justify-center">
        <IndexCard title="NIFTY 50 INDEX" symbol="NSE:NIFTY50-INDEX" />
        <IndexCard title="BANK NIFTY INDEX" symbol="NSE:NIFTYBANK-INDEX" />
        <IndexCard title="SENSEX INDEX" symbol="BSE:SENSEX-INDEX" />
      </div>

      <div className="mt-12 text-gray-500 text-sm">
        Data is streamed live from Fyers API. Ensure you have a valid token and the backend server running to see real-time updates.
      </div>
    </main>
  );
};
