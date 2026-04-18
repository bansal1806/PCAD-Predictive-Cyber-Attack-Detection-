import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function RealTimeCharts({ data, isThreat }) {
  const lineColor = isThreat ? '#FF003C' : '#00FFFF';
  
  return (
    <div className="space-y-6">
      {/* Traffic Chart */}
      <div className="bg-void-light p-6 rounded-lg border border-gray-800">
        <h3 className="text-lg font-semibold text-white mb-4 uppercase tracking-wider">Live Network Traffic (Packet Size)</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis dataKey="timeLabel" stroke="#9ca3af" fontSize={12} tickMargin={10} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0A0A0E', borderColor: '#1f2937', color: '#fff' }}
                itemStyle={{ color: lineColor }}
              />
              <Line 
                type="monotone" 
                dataKey="packetSize" 
                stroke={lineColor} 
                strokeWidth={2} 
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Probability Chart */}
      <div className="bg-void-light p-6 rounded-lg border border-gray-800">
        <h3 className="text-lg font-semibold text-white mb-4 uppercase tracking-wider">Attack Probability Timeline</h3>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis dataKey="timeLabel" stroke="#9ca3af" fontSize={12} tickMargin={10} />
              <YAxis stroke="#9ca3af" fontSize={12} domain={[0, 1]} ticks={[0, 0.5, 1]} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0A0A0E', borderColor: '#1f2937', color: '#fff' }}
                itemStyle={{ color: isThreat ? '#FF003C' : '#39FF14' }}
              />
              <Line 
                type="stepAfter" 
                dataKey="probability" 
                stroke={isThreat ? '#FF003C' : '#39FF14'} 
                strokeWidth={2} 
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
