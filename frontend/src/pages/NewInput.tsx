import React, { useState, useEffect, ChangeEvent } from 'react';
import Navbar from '../components/navbar/Navbar'
import waves from '../wickedbackground.svg'

function NewInput() {
  const [user, setUser] = useState(null);
  const [file, setFile] = useState<File | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/profile', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        console.log(data);
        setUser(data.data.name);
      } else {
        console.log('Error:', response.status);
      }
    };

    fetchData();
  }, []);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleImport = async () => {
    if (!file) {
      console.log('No file selected');
      return;
    }

    try {
      const jsonData = await file.text();
      const parsedData = JSON.parse(jsonData);

      // Send the parsed data to your server to handle the import process
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/import', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(parsedData)
      });

      if (response.ok) {
        console.log('Import successful');
      } else {
        console.log('Error:', response.status);
      }
    } catch (error) {
      console.log('Error:', error);
    }
  };

  const handleExportClick = async () => {
    const token = localStorage.getItem('token');
    const response = await fetch('http://localhost:5000/export', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });

    if (response.ok) {
      const data = await response.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], {type : 'application/json'});
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'data.json'; // you can give any name for the file here
      a.click();
    } else {
      console.log('Error:', response.status);
    }
  };

  return (
    <div className="h-screen bg-white flex flex-col items-center justify-center px-6 relative">
      <img src={waves} alt="Waves" className="absolute bottom-0 left-0 w-full h-full" />
      <div className="z-10 relative w-full">
        <Navbar selected={3}/>
        <div className="-mt-36">
          <h1 className="text-4xl font-bold text-center">Welcome, {user}</h1>
          <h2 className="text-3xl font-bold text-center mt-16">New Input</h2>
        </div>
        <div className="flex flex-col items-center mt-32 space-y-16">
          <button onClick={() => {window.location.href = "/adddata"}} className="w-64 py-7 px-11 bg-blue-500 text-white font-bold rounded-lg text-2xl">
            Manual Input
          </button>
          <input
              type="file"
              accept=".json"
              id="import-input"
              onChange={handleFileChange}
            />
          <button onClick={handleImport} className="w-64 py-7 px-11 bg-blue-500 text-white font-bold rounded-lg text-2xl">
            Import
          </button>
          <button onClick={handleExportClick} className="w-64 py-7 px-11 bg-blue-500 text-white font-bold rounded-lg text-2xl">
            Export
          </button>
        </div>
      </div>
    </div>
  )
}

export default NewInput