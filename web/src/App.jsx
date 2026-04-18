import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Shield } from 'lucide-react';
import TopMetricsBar from './components/TopMetricsBar';
import RealTimeCharts from './components/RealTimeCharts';
import ActionCenter from './components/ActionCenter';
import ExplainabilityPanel from './components/ExplainabilityPanel';
import DataDistributionChart from './components/DataDistributionChart';

const API_BASE = 'http://localhost:8000';
const API_KEY = 'pcad-secure-2024';

function App() {
  const [dataHistory, setDataHistory] = useState([]);
  const [logs, setLogs] = useState(['[INFO] System initialized. Command Center Online.', '[INFO] Connecting to telemetry stream...']);
  const [currentMetrics, setCurrentMetrics] = useState({
    packetSize: 0,
    latency: 0,
    probability: 0.05,
    isThreat: false,
    attackType: 'None'
  });

  // Polling loop
  useEffect(() => {
    const pollInterval = setInterval(async () => {
      try {
        // 1. Fetch live traffic
        const trafficRes = await axios.get(`${API_BASE}/live-traffic?batch_size=1`, {
          headers: { 'X-API-Key': API_KEY }
        });
        
        if (trafficRes.data && trafficRes.data.length > 0) {
          const traffic = trafficRes.data[0];
          
          // 2. Send for prediction
          const predictRes = await axios.post(`${API_BASE}/predict`, {
            features: traffic.features
          }, {
            headers: { 'X-API-Key': API_KEY }
          });
          
          const prediction = predictRes.data;
          const isThreat = prediction.probability >= 0.5;
          
          // 3. Update State
          const timestampStr = new Date(traffic.timestamp).toLocaleTimeString();
          
          setCurrentMetrics({
            packetSize: traffic.packet_size,
            latency: traffic.latency,
            probability: prediction.probability,
            isThreat: isThreat,
            attackType: prediction.attack_type || 'None'
          });

          setDataHistory(prev => {
            const newHistory = [...prev, {
              timeLabel: timestampStr,
              packetSize: traffic.packet_size,
              probability: prediction.probability
            }];
            // Keep last 30 points
            if (newHistory.length > 30) return newHistory.slice(newHistory.length - 30);
            return newHistory;
          });

          // 4. Logs
          setLogs(prev => {
            let newLogs = [...prev, `[INFO] ${timestampStr} | Traffic Processed | Prob: ${prediction.probability.toFixed(3)}`];
            if (isThreat) {
              newLogs.push(`[ALERT] ${timestampStr} | THREAT DETECTED: ${prediction.attack_type || 'Anomalous Signature'}`);
            }
            if (newLogs.length > 50) return newLogs.slice(newLogs.length - 50);
            return newLogs;
          });
        }
      } catch (err) {
        console.error("API Error", err);
      }
    }, 1500); // Poll every 1.5s

    return () => clearInterval(pollInterval);
  }, []);

  const handleTriggerAttack = async () => {
    try {
      setLogs(prev => [...prev, `[USER] Initiating manual attack simulation...`]);
      await axios.post(`${API_BASE}/simulate-attack`, {}, {
        headers: { 'X-API-Key': API_KEY }
      });
      setLogs(prev => [...prev, `[CRITICAL] SIMULATION ACTIVE: Injecting high-density payload at index 8543!`]);
    } catch (err) {
      console.error(err);
      setLogs(prev => [...prev, `[ERROR] Failed to trigger simulation. API offline?`]);
    }
  };

  return (
    <div className="min-h-screen p-6 font-inter">
      {/* Header */}
      <header className="flex justify-between items-center mb-8 border-b border-gray-800 pb-4">
        <div className="flex items-center gap-3">
          <Shield className="w-8 h-8 text-cyan" />
          <h1 className="text-3xl font-black tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-cyan to-blue-500 uppercase">
            Aegis Sentinel
          </h1>
        </div>
        <div className="flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyan/10 border border-cyan/30 text-cyan text-sm font-bold tracking-widest uppercase shadow-[0_0_10px_rgba(0,255,255,0.2)]">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan"></span>
          </span>
          Live Demo Mode
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto">
        <TopMetricsBar 
          isThreat={currentMetrics.isThreat} 
          probability={currentMetrics.probability}
          packetSize={currentMetrics.packetSize}
          latency={currentMetrics.latency}
          attackType={currentMetrics.attackType}
        />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <RealTimeCharts data={dataHistory} isThreat={currentMetrics.isThreat} />
          </div>
          <div className="lg:col-span-1">
            <ActionCenter 
              logs={logs} 
              onTriggerAttack={handleTriggerAttack} 
              isThreat={currentMetrics.isThreat} 
            />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
          <div className="lg:col-span-1">
            <DataDistributionChart />
          </div>
          <div className="lg:col-span-2">
            <ExplainabilityPanel />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
