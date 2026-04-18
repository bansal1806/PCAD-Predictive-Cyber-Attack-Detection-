import React, { useRef, useEffect } from 'react';
import { Terminal, Crosshair } from 'lucide-react';

export default function ActionCenter({ logs, onTriggerAttack, isThreat }) {
  const terminalRef = useRef(null);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="space-y-6">
      {/* Trigger Button */}
      <button 
        onClick={onTriggerAttack}
        className="w-full relative group overflow-hidden rounded-lg p-[2px] cursor-pointer"
      >
        <span className="absolute inset-0 bg-gradient-to-r from-crimson to-orange-600 rounded-lg opacity-80 group-hover:opacity-100 transition-opacity duration-300"></span>
        <div className="relative bg-void px-8 py-6 rounded-lg flex items-center justify-center gap-4 group-hover:bg-opacity-0 transition-all duration-300">
          <Crosshair className="w-8 h-8 text-white group-hover:scale-110 transition-transform" />
          <span className="text-xl font-bold text-white uppercase tracking-widest">Trigger Attack Simulation</span>
        </div>
      </button>

      {/* Terminal */}
      <div className="bg-void-light rounded-lg border border-gray-800 flex flex-col h-96 overflow-hidden relative">
        <div className="bg-gray-900 px-4 py-2 border-b border-gray-800 flex items-center gap-2">
          <Terminal className="w-4 h-4 text-gray-400" />
          <span className="text-gray-400 text-xs uppercase font-mono tracking-wider">System Logs</span>
          {isThreat && <span className="ml-auto flex h-3 w-3 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-crimson opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-crimson"></span>
          </span>}
        </div>
        <div ref={terminalRef} className="p-4 flex-1 overflow-y-auto font-mono text-sm space-y-2">
          {logs.map((log, idx) => {
            const isAlert = log.includes('[ALERT]') || log.includes('THREAT') || log.includes('CRITICAL');
            return (
              <div key={idx} className={`${isAlert ? 'text-crimson font-bold' : 'text-gray-400'}`}>
                {log}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
