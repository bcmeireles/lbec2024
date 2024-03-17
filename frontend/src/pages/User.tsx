import React, { useState, useEffect } from 'react'
import Navbar from '../components/navbar/Navbar'
import waves from '../wickedbackground.svg'
import Switch from '../components/Switch';
import Slider from 'rc-slider';
import SliderRange from 'rc-slider/es/Slider';
import 'rc-slider/assets/index.css';



function User() {
  const [form, setForm] = useState({
    gas: 0,
    electricity: 0,
    water: 0,
    minTemp: 18,
    maxTemp: 24,
    receiveNotifications: false,
    timing: 0,
  });

  // useEffect(() => {
  //   const fetchData = async () => {
  //     const result = await axios('http://localhost:5000/settings', {
  //       method: 'GET',
  //       headers: {
  //         'Content-Type': 'application/json',
  //         'Authorization': `Bearer ${localStorage.getItem('token')}` // assuming you're storing the JWT token in localStorage
  //       }
  //     });

  //     setForm({
  //       gas: result.data.data.gas_price,
  //       electricity: result.data.data.electricity_price,
  //       water: result.data.data.water_price,
  //       minTemp: result.data.data.min_house_temp,
  //       maxTemp: result.data.data.max_house_temp,
  //       receiveNotifications: result.data.data.enable_notifications,
  //       timing: result.data.data.notifications_default_timing,
  //     });
  //   };

  //   fetchData();
  // }, []);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/settings', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setForm({
          gas: data.data.gas_price,
          electricity: data.data.electricity_price,
          water: data.data.water_price,
          minTemp: data.data.min_house_temp,
          maxTemp: data.data.max_house_temp,
          receiveNotifications: data.data.enable_notifications,
          timing: data.data.notifications_default_timing,
        });
      } else {
        console.log('Error:', response.status);
      }
    };

    fetchData();
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setForm((prevForm) => ({
      ...prevForm,
      [name]: type === 'checkbox' ? checked : type === 'number' ? parseFloat(value) : value,
    }));
  };

  const handleDropdownChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm((prevForm) => ({
      ...prevForm,
      [name]: value,
    }));
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    console.log('Submitting form:', form);
  
    const token = localStorage.getItem('token');
    const response = await fetch('http://localhost:5000/settings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(form)
    });
  
    if (response.ok) {
      const data = await response.json();
      console.log('Settings updated successfully:', data);
    } else {
      console.log('Error:', response.status);
    }
  };

  const handleTempChange = (value: number | number[]) => {
    if (Array.isArray(value)) {
      setForm((prevForm) => ({
        ...prevForm,
        minTemp: value[0],
        maxTemp: value[1],
      }));
    } else {
      // Handle the case where value is a single number
    }
  };
  
  

  return (
    <div className="h-screen bg-white flex items-center justify-center px-6 relative">
      <img src={waves} alt="Waves" className="absolute bottom-0 left-0 w-full h-full" />
      <div className="z-10 relative">
      <Navbar selected={4}/>
      <h1 className="text-3xl font-bold text-center mb-8">Change User Settings</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="bg-white border rounded-lg p-2">
            <h2 className="text-2xl font-bold mb-4">Prices</h2>
            <div className="flex items-center justify-between p-4 border-b-2 rounded bg-white">
              <label htmlFor="gas" className="w-24 font-bold">Gas</label>
              <input type="number" name="gas" id="gas" value={form.gas} onChange={handleInputChange} className="flex-1 ml-2 text-right" />
              <span className="ml-2 w-16 text-right">€ / m³</span>
            </div>
            <div className="flex items-center justify-between p-4 border-b-2 rounded bg-white">
              <label htmlFor="electricity" className="w-24 font-bold">Electricity</label>
              <input type="number" name="electricity" id="electricity" value={form.electricity} onChange={handleInputChange} className="flex-1 ml-2 text-right" />
              <span className="ml-2 w-16 text-right">€ / mWh</span>
            </div>
            <div className="flex items-center justify-between p-4 rounded bg-white">
              <label htmlFor="water" className="w-24 font-bold">Water</label>
              <input type="number" name="water" id="water" value={form.water} onChange={handleInputChange} className="flex-1 ml-2 text-right" />
              <span className="ml-2 w-16 text-right">€ / L</span>
            </div>
          </div>

          <div className="bg-white border rounded-lg p-2">
          <h2 className="text-2xl font-bold mb-4">Preferences</h2>
          <label htmlFor="houseT" className="w-24 font-bold mb-4">House Temperature</label>
          <SliderRange
            range
            allowCross={false}
            value={[form.minTemp, form.maxTemp]}
            min={15}
            max={30}
            onChange={handleTempChange}
            trackStyle={[{ backgroundColor: 'rgb(59 130 246)' }]}
          />
          <p>Min: {form.minTemp}°C, Max: {form.maxTemp}°C</p>
          </div>

          <div className="bg-white border rounded-lg p-2">
          <h2 className="text-2xl font-bold mb-4">Notifications</h2>
          <div className="flex items-center justify-between">
            <label htmlFor="receiveNotifications" className="font-bold">Enable notifications?</label>
            <Switch
              name="receiveNotifications"
              id="receiveNotifications"
              checked={form.receiveNotifications}
              onChange={handleInputChange}
            />
          </div>
          {form.receiveNotifications && (
            <div className="flex items-center justify-between mt-4">
              <label htmlFor="timing" className="font-bold">Notification Timing</label>
              <select
                name="timing"
                id="timing"
                value={form.timing}
                onChange={handleDropdownChange}
                className="border rounded p-2 mt-2"
              >
                <option value="">Select timing</option>
                <option value={60}>1 hour before</option>
                <option value={60 * 24}>1 day before</option>
              </select>
            </div>
          )}
        </div>


          <div className="flex justify-center mt-8">
            <button type="submit" className="py-2 px-11 bg-blue-500 text-white rounded-lg font-bold">Submit</button>
          </div>
          
        </form>
        
      </div>
    </div>
  )
}

export default User
