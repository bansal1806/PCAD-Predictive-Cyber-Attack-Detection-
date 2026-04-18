import React from 'react';
import { Activity, ShieldAlert, ShieldCheck, Zap } from 'lucide-react';

export default function TopMetricsBar({ isThreat, probability, packetSize, latency, attackType }) {
  const statusColor = isThreat ? 'text-crimson' : 'text-neon-green';
  const bgColor = isThreat ? 'bg-crimson/20 shadow-[0_0_15px_rgba(255,0,60,0.5)]' : 'bg-void-light';

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      {/* Status Card */}
      <div className={`p-6 rounded-lg border border-gray-800 flex items-center gap-4 transition-all duration-300 ${bgColor}`}>
        {isThreat ? <ShieldAlert className="w-10 h-10 text-crimson" /> : <ShieldCheck className="w-10 h-10 text-neon-green" />}
        <div>
          <p className="text-gray-400 text-sm font-semibold uppercase tracking-wider">System Status</p>
          <h2 className={`text-2xl font-bold ${statusColor} leading-tight`}>
            {isThreat ? '🔴 THREAT DETECTED' : '🟢 NORMAL'}
          </h2>
          {isThreat && (
            <p className="text-crimson text-xs font-bold uppercase tracking-wider mt-1 border border-crimson/50 px-2 py-0.5 rounded inline-block bg-crimson/10">
              Type: {attackType}
            </p>
          )}
        </div>
      </div>

      {/* Probability Card */}
      <div className="bg-void-light p-6 rounded-lg border border-gray-800 flex items-center gap-4">
        <Activity className={`w-10 h-10 ${statusColor}`} />
        <div className="w-full">
          <div className="flex justify-between mb-1">
            <span className="text-gray-400 text-sm font-semibold uppercase tracking-wider">Attack Probability</span>
            <span className={`font-bold ${statusColor}`}>{(probability * 100).toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-800 rounded-full h-2.5">
            <div 
              className={`h-2.5 rounded-full transition-all duration-500 ${isThreat ? 'bg-crimson' : 'bg-neon-green'}`} 
              style={{ width: `${Math.min(probability * 100, 100)}%` }}></div>
          </div>
        </div>
      </div>

      {/* Packet Size Card */}
      <div className="bg-void-light p-6 rounded-lg border border-gray-800 flex items-center gap-4">
        <Zap className="w-10 h-10 text-cyan" />
        <div>
          <p className="text-gray-400 text-sm font-semibold uppercase tracking-wider">Pkt Size (sum)</p>
          <h2 className="text-2xl font-bold text-white">{packetSize.toFixed(0)} <span className="text-sm text-gray-500">B</span></h2>
        </div>
      </div>

      {/* Latency Card */}
      <div className="bg-void-light p-6 rounded-lg border border-gray-800 flex items-center gap-4">
        <Activity className="w-10 h-10 text-cyan" />
        <div>
          <p className="text-gray-400 text-sm font-semibold uppercase tracking-wider">Latency (mean)</p>
          <h2 className="text-2xl font-bold text-white">{latency.toFixed(2)} <span className="text-sm text-gray-500">ms</span></h2>
        </div>
      </div>
    </div>
  );
}
