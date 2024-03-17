import React, { useState, useEffect } from 'react'
import Navbar from '../components/navbar/Navbar'
import waves from '../wickedbackground.svg'

function Overview() {

  const [totalCosts, setTotalCosts] = useState([]);
  const [totalUsage, setTotalUsage] = useState([]);
  const [graphData, setGraphData] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/daygraph', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          // 'date': new Date().toISOString().split('T')[0]
          "date": "2024-01-01"
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
    };

    fetchData();
  }, []);

  return (
    <div className="h-screen bg-white flex items-center justify-center px-6 relative">
      <img src={waves} alt="Waves" className="absolute bottom-0 left-0 w-full h-full" />
      <div className="z-10 relative">
        <img src={graphData} alt="Graph" />
        <Navbar selected={1}/>
      </div>
    </div>
  )
}

export default Overview