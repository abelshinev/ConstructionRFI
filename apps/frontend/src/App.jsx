import { useState, useEffect, useRef } from 'react';
import { HardHat, Shirt, AlertTriangle, Info, Truck, User, Link as LinkIcon, Server } from 'lucide-react';

// --- MOCK DATA ---
// Simulating the output of observation.py for immediate visualization
const MOCK_OBSERVATION = {
  status: "OBSERVATION_COMPLETE",
  total_entities: 3,
  entities: [
    {
      id: "worker_8a3f12",
      category: "WORKER",
      confidence: 0.99,
      bbox: [400, 200, 500, 450], // x1, y1, x2, y2
      equipment: {
        helmet: true,
        vest: false
      }
    },
    {
      id: "worker_9b4c22",
      category: "WORKER",
      confidence: 0.98,
      bbox: [100, 300, 180, 500],
      equipment: {
        helmet: true,
        vest: true
      }
    },
    {
      id: "machinery_4e93ef",
      category: "HEAVY_EQUIPMENT",
      class: "excavator",
      confidence: 0.92,
      bbox: [250, 100, 550, 350]
    }
  ],
  spatial_relationships: [
    {
      source_id: "worker_8a3f12",
      target_id: "machinery_4e93ef",
      relationship: "SPATIAL_PROXIMITY",
      distance_pixels: 111.8
    },
    {
      source_id: "worker_9b4c22",
      target_id: "machinery_4e93ef",
      relationship: "SPATIAL_PROXIMITY",
      distance_pixels: 291.5
    }
  ]
};

export default function App() {
  const [data, setData] = useState(MOCK_OBSERVATION);
  const [assetId, setAssetId] = useState('demo-asset-123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [useMock, setUseMock] = useState(true);

  // Example of how you would fetch from your real FastAPI backend
  const fetchObservationData = async () => {
    if (useMock) {
      setData(MOCK_OBSERVATION);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      // Replace with your actual FastAPI endpoint URL
      const response = await fetch(`http://localhost:8000/assets/${assetId}/observations`);
      if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
      const json = await response.json();
      
      if (json.status === "PROCESSING") {
        setError("Asset is still processing in the background...");
      } else {
        setData(json.data);
      }
    } catch (err) {
      setError(err.message);
      // Fallback to mock on error for demo purposes
      setData(MOCK_OBSERVATION); 
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchObservationData();
  }, [useMock]);

  // Helper math to find box centers for drawing the proximity lines
  const getCenter = (bbox) => {
    return {
      x: (bbox[0] + bbox[2]) / 2,
      y: (bbox[1] + bbox[3]) / 2
    };
  };

  const getEntityById = (id) => data.entities.find(e => e.id === id);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 font-sans flex flex-col">
      
      {/* HEADER */}
      <header className="bg-slate-900 border-b border-slate-800 p-4 flex items-center justify-between shadow-md z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500/20 text-blue-400 rounded-lg">
            <Server size={24} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Vision Edge Dashboard</h1>
            <p className="text-xs text-slate-400">Observation Graph Visualizer</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm bg-slate-800 p-1 rounded-lg border border-slate-700">
            <button 
              onClick={() => setUseMock(true)}
              className={`px-3 py-1.5 rounded-md transition-colors ${useMock ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
            >
              Mock Data
            </button>
            <button 
              onClick={() => setUseMock(false)}
              className={`px-3 py-1.5 rounded-md transition-colors ${!useMock ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
            >
              Live API
            </button>
          </div>
          
          {!useMock && (
            <div className="flex gap-2">
              <input 
                type="text" 
                value={assetId}
                onChange={(e) => setAssetId(e.target.value)}
                placeholder="Asset UUID..."
                className="bg-slate-800 border border-slate-700 rounded-md px-3 py-1.5 text-sm outline-none focus:border-blue-500 transition-colors"
              />
              <button 
                onClick={fetchObservationData}
                className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-1.5 rounded-md text-sm font-medium transition-colors"
              >
                Fetch
              </button>
            </div>
          )}
        </div>
      </header>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 flex overflow-hidden">
        
        {/* LEFT COLUMN: Visualizer Canvas */}
        <div className="flex-1 p-6 relative bg-slate-950 overflow-hidden flex flex-col">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-slate-300 flex items-center gap-2">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-400"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"></path><circle cx="12" cy="13" r="3"></circle></svg>
              Camera Feed Overlay
            </h2>
            {error && <span className="text-red-400 text-sm bg-red-400/10 px-3 py-1 rounded border border-red-400/20">{error}</span>}
            {loading && <span className="text-blue-400 text-sm animate-pulse">Fetching observations...</span>}
          </div>

          <div className="flex-1 relative border-2 border-dashed border-slate-800 rounded-xl bg-slate-900 overflow-hidden">
            {/* In production, an <img /> would go here. 
              We use a gray background representing a standard 800x600 camera frame. 
            */}
            <div className="absolute inset-0 flex items-center justify-center text-slate-700 pointer-events-none">
              [ 800x600 Camera Frame ]
            </div>

            {data && (
              <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 800 600">
                {/* 1. Draw Edges (Spatial Relationships) */}
                {data.spatial_relationships.map((rel, idx) => {
                  const source = getEntityById(rel.source_id);
                  const target = getEntityById(rel.target_id);
                  if (!source || !target) return null;

                  const sCenter = getCenter(source.bbox);
                  const tCenter = getCenter(target.bbox);

                  return (
                    <g key={`edge-${idx}`}>
                      <line 
                        x1={sCenter.x} y1={sCenter.y} 
                        x2={tCenter.x} y2={tCenter.y} 
                        stroke="#f59e0b" // Amber
                        strokeWidth="2" 
                        strokeDasharray="6,6"
                        className="opacity-70"
                      />
                      {/* Distance Label */}
                      <rect 
                        x={(sCenter.x + tCenter.x)/2 - 30} 
                        y={(sCenter.y + tCenter.y)/2 - 12} 
                        width="60" height="24" rx="4" 
                        fill="#1e293b" stroke="#f59e0b" strokeWidth="1"
                      />
                      <text 
                        x={(sCenter.x + tCenter.x)/2} 
                        y={(sCenter.y + tCenter.y)/2 + 4} 
                        fill="#fcd34d" fontSize="12" textAnchor="middle" fontWeight="bold"
                      >
                        {rel.distance_pixels.toFixed(0)} px
                      </text>
                    </g>
                  );
                })}

                {/* 2. Draw Nodes (Bounding Boxes) */}
                {data.entities.map(entity => {
                  const [x1, y1, x2, y2] = entity.bbox;
                  const width = x2 - x1;
                  const height = y2 - y1;
                  const isWorker = entity.category === "WORKER";
                  
                  const strokeColor = isWorker ? "#3b82f6" : "#ef4444"; // Blue for Worker, Red for Equip
                  const bgColor = isWorker ? "rgba(59, 130, 246, 0.1)" : "rgba(239, 68, 68, 0.1)";

                  return (
                    <g key={entity.id}>
                      {/* Bounding Box */}
                      <rect 
                        x={x1} y={y1} width={width} height={height} 
                        fill={bgColor} stroke={strokeColor} strokeWidth="3" rx="4"
                      />
                      
                      {/* Label Tab */}
                      <rect 
                        x={x1 - 1.5} y={y1 - 25} width={isWorker ? 120 : 100} height="25" rx="4"
                        fill={strokeColor}
                      />
                      <text x={x1 + 6} y={y1 - 8} fill="white" fontSize="12" fontWeight="bold">
                        {isWorker ? "WORKER" : entity.class.toUpperCase()}
                      </text>
                      
                      {/* PPE Overlay (If Worker) */}
                      {isWorker && (
                        <g transform={`translate(${x1 + width - 60}, ${y1 + 5})`}>
                          <rect width="55" height="24" rx="4" fill="#1e293b" opacity="0.9" />
                          {/* Helmet indicator */}
                          <circle cx="15" cy="12" r="4" fill={entity.equipment.helmet ? "#22c55e" : "#ef4444"} />
                          {/* Vest indicator */}
                          <circle cx="40" cy="12" r="4" fill={entity.equipment.vest ? "#22c55e" : "#ef4444"} />
                        </g>
                      )}
                    </g>
                  );
                })}
              </svg>
            )}
          </div>
        </div>

        {/* RIGHT COLUMN: The Emitted Graph JSON / Telemetry */}
        <div className="w-[400px] border-l border-slate-800 bg-slate-900/50 flex flex-col">
          <div className="p-4 border-b border-slate-800">
            <h2 className="text-sm font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <LinkIcon size={16} className="text-emerald-400" />
              Graph Payload Emitted
            </h2>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            
            {/* WORKERS LIST */}
            <div>
              <h3 className="text-xs font-semibold text-slate-500 uppercase mb-3 border-b border-slate-800 pb-2">Identified Entities</h3>
              <div className="space-y-3">
                {data?.entities.filter(e => e.category === 'WORKER').map(worker => (
                  <div key={worker.id} className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-blue-400 flex items-center gap-2">
                        <User size={14} /> {worker.id.substring(0, 13)}...
                      </span>
                      <span className="text-xs text-slate-500 border border-slate-700 px-2 py-0.5 rounded">
                        {(worker.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="flex gap-4 mt-3">
                      <div className={`flex items-center gap-1.5 text-xs ${worker.equipment.helmet ? 'text-emerald-400' : 'text-red-400'}`}>
                        <HardHat size={14} /> {worker.equipment.helmet ? 'Helmet OK' : 'No Helmet'}
                      </div>
                      <div className={`flex items-center gap-1.5 text-xs ${worker.equipment.vest ? 'text-emerald-400' : 'text-red-400'}`}>
                        <Shirt size={14} /> {worker.equipment.vest ? 'Vest OK' : 'No Vest'}
                      </div>
                    </div>
                  </div>
                ))}

                {/* MACHINERY LIST */}
                {data?.entities.filter(e => e.category === 'HEAVY_EQUIPMENT').map(equip => (
                  <div key={equip.id} className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-red-400 flex items-center gap-2 capitalize">
                        <Truck size={14} /> {equip.class}
                      </span>
                      <span className="text-xs font-mono text-slate-500">ID: {equip.id.substring(0, 8)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* RAW FACTS / SPATIAL RELATIONSHIPS */}
            <div>
              <h3 className="text-xs font-semibold text-slate-500 uppercase mb-3 border-b border-slate-800 pb-2">Spatial Facts</h3>
              <div className="space-y-2">
                {data?.spatial_relationships.map((rel, idx) => (
                  <div key={idx} className="bg-slate-800/30 border border-slate-700/50 rounded-lg p-3 text-sm">
                    <div className="flex items-center gap-2 text-slate-300">
                      <span className="text-blue-400 font-mono text-xs">{rel.source_id.split('_')[1]}</span>
                      <span className="text-slate-500">is</span>
                      <span className="text-amber-400 font-bold">{rel.distance_pixels.toFixed(1)}px</span>
                      <span className="text-slate-500">from</span>
                      <span className="text-red-400 font-mono text-xs">{rel.target_id.split('_')[1]}</span>
                    </div>
                  </div>
                ))}
                {data?.spatial_relationships.length === 0 && (
                  <p className="text-sm text-slate-500 italic">No proximity thresholds triggered.</p>
                )}
              </div>
            </div>

            {/* RAW JSON VIEW */}
            <div>
              <h3 className="text-xs font-semibold text-slate-500 uppercase mb-3 border-b border-slate-800 pb-2">Payload to Context Graph</h3>
              <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 overflow-x-auto">
                <pre className="text-[10px] text-emerald-500/80 font-mono leading-tight">
                  {JSON.stringify(data, null, 2)}
                </pre>
              </div>
            </div>

          </div>
        </div>

      </main>
    </div>
  );
}