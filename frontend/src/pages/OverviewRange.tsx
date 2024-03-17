import React, { useState, useEffect } from 'react'
import Navbar from '../components/navbar/Navbar'
import waves from '../wickedbackground.svg'

type Costs = {
  electricity: number;
  gas: number;
  water: number;
};

type Usage = {
  electricity: number;
  gas: number;
  water: number;
};

function OverviewRange() {

  const [graphData, setGraphData] = useState("");
  const [totalCosts, setTotalCosts] = useState<Costs>({ electricity: 0, gas: 0, water: 0 });
  const [totalUsage, setTotalUsage] = useState<Usage>({ electricity: 0, gas: 0, water: 0 });
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(new Date());

    const fetchData = async () => {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/rangegraph', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          "start": startDate.toISOString().split('T')[0],
          "end": endDate.toISOString().split('T')[0]
          // "date": "2024-01-01"
        })
      });

      if (response.ok) {
        const data = await response.json();
        console.log(data);
        setTotalCosts(data.data.total_costs);
        setTotalUsage(data.data.total_usage);
        setGraphData(data.data.graph);
      } else {
        console.log('Error:', response.status);
      }
    
    }

  

  return (
    <div className="h-screen bg-white flex items-center justify-center px-6 relative">
      <img src={waves} alt="Waves" className="absolute bottom-0 left-0 w-full h-full" />
      <div className="z-10 relative">
        <Navbar selected={1}/>
        
        <div className="-mt-36">
          <h1 className="text-4xl font-bold text-center mt-16 mb-8">Overview</h1>

          <div className="flex flex-col items-center space-y-4">
            <div className="flex space-x-8">
              <input type="date" value={startDate.toISOString().split('T')[0]} onChange={(e) => setStartDate(new Date(e.target.value))} />
              <input type="date" value={endDate.toISOString().split('T')[0]} onChange={(e) => setEndDate(new Date(e.target.value))} />
            </div>
            <input type="button" value="Submit" className="py-2 px-3 bg-blue-500 text-white rounded-lg font-bold" onClick={fetchData}/>
          </div>

          <img src={graphData} className="mt-16" alt="Graph" />

          <div className="flex space-x-16 mt-16">
            <div className="flex flex-col items-center space-y-2">
              <h3 className="text-xl font-bold">Electricity</h3>
              <p className="text-sm">Total: {totalUsage.electricity} kWh</p>
              <p className="text-sm">Cost: {totalCosts.electricity} €</p>
            </div>
            <div className="flex flex-col items-center space-y-2">
              <h3 className="text-xl font-bold">Gas</h3>
              <p className="text-sm">Total: {totalUsage.gas} m³</p>
              <p className="text-sm">Cost: {totalCosts.gas} €</p>
            </div>
            <div className="flex flex-col items-center space-y-2">
              <h3 className="text-xl font-bold">Water</h3>
              <p className="text-sm">Total: {totalUsage.water} m³</p>
              <p className="text-sm">Cost: {totalCosts.water} €</p>
            </div>
          </div>
          <div className="flex flex-col items-center">
            <button onClick={() => window.location.href = "/range"} className="py-4 px-11 bg-blue-500 text-white rounded-lg mt-12 font-bold">Day View</button>
          </div>
        </div>
      </div>
    </div>
  )

}

export default OverviewRange