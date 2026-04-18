import React, { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import axios from 'axios';

const COLORS = ['#00FFFF', '#FF003C']; // Cyan for Normal, Neon Red for Attack

export default function DataDistributionChart() {
  const [data, setData] = useState([
    { name: 'Normal Traffic', value: 13139 },
    { name: 'Cyber Attacks', value: 52089 }
  ]);

  useEffect(() => {
    const fetchDistribution = async () => {
      try {
        const res = await axios.get('http://localhost:8000/distribution');
        if (res.data && Array.isArray(res.data)) {
          setData(res.data);
        }
      } catch (err) {
        console.error("Failed to fetch distribution data", err);
      }
    };
    fetchDistribution();
  }, []);

  return (
    <div className="bg-void-light p-6 rounded-lg border border-gray-800 h-full flex flex-col">
      <h3 className="text-lg font-semibold text-white mb-4 uppercase tracking-wider">Dataset Distribution</h3>
      <div className="flex-grow min-h-[250px]">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              paddingAngle={5}
              dataKey="value"
              stroke="none"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ backgroundColor: '#0A0A0E', borderColor: '#1f2937', color: '#fff' }}
              itemStyle={{ color: '#fff' }}
            />
            <Legend 
              verticalAlign="bottom" 
              height={36}
              formatter={(value) => <span className="text-gray-400 text-sm">{value}</span>}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4 pt-4 border-t border-gray-800">
        <p className="text-xs text-gray-500 text-center uppercase tracking-tighter">
          Total Samples: {data.reduce((acc, curr) => acc + curr.value, 0).toLocaleString()}
        </p>
      </div>
    </div>
  );
}
