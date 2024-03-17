import React, { useState, useEffect } from 'react';
import moment from 'moment';
import 'react-datepicker/dist/react-datepicker.css';
import DatePicker from 'react-datepicker';
import Navbar from '../../components/navbar/Navbar';
import waves from '../../wickedbackground.svg';
import './CreateEvent.css';
import Switch from '../../components/Switch';

interface Event {
  title: string;
  start: Date;
  end: Date;
  toNotify: boolean;
  notifyTiming: number;
}

const CreateEvent: React.FC = () => {
  const [title, setTitle] = useState('');
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);

  const [notify, setNotify] = useState(false);
  const [timing, setTiming] = useState(0);

  useEffect(() => {
    const token = localStorage.getItem('token');
    fetch('http://localhost:5000/profile', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    }).then((response) => {
      if (response.ok) {
        response.json().then((data) => {
          console.log(data)
          setNotify(data.data.enable_notifications);
          setTiming(data.data.notifications_default_timing);
        });
      }
    }
    );
  }, []);

  const handleCreateEvent = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (title && startDate && endDate) {
      console.log('Creating event');
      const token = localStorage.getItem('token');
      fetch('http://localhost:5000/events', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          title: title,
          start: moment(startDate).format(),
          end: moment(endDate).format(),
          toNotify: notify,
          notifyTiming: timing
        })
      }).then((response) => {
        if (response.ok) {
          console.log("Form submitted successfully");
          window.location.href = '/calendar';
        } else {
          console.log("Error:", response.status);
        }
      });
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    if (name === 'title') {
      setTitle(value);
    }
  };

  return (
    <div className="h-screen bg-white flex flex-col items-center justify-center px-24 relative">
      <img src={waves} alt="Waves" className="absolute bottom-0 left-0 w-full h-full" />
      <div className="z-10 relative w-full space-y-4">
        <Navbar selected={2} />
        <h1 className="text-3xl font-bold text-center mb-8">Create New Event</h1>
        <form onSubmit={handleCreateEvent} className="space-y-4">
          <div className="border p-4 rounded bg-white">
            <label htmlFor="title" className="block font-bold mb-2 text-center border-b-2">Event Title</label>
            <input type="text" name="title" id="title" value={title} onChange={handleInputChange} className="w-full text-center border" />
          </div>
          <div className="datepicker-container space-y-4">
            <DatePicker
              selected={startDate}
              onChange={(date: Date) => setStartDate(date)}
              showTimeSelect
              timeFormat="HH:mm"
              timeIntervals={15}
              dateFormat="MMMM d, yyyy h:mm aa"
              placeholderText="Start date and time"
              className="rounded-md text-center"
            />
            <DatePicker
              selected={endDate}
              onChange={(date: Date) => setEndDate(date)}
              showTimeSelect
              timeFormat="HH:mm"
              timeIntervals={15}
              dateFormat="MMMM d, yyyy h:mm aa"
              placeholderText="End date and time"
              className="rounded-md text-center"
            />
          </div>
          <div className="flex items-center justify-between">
            <label htmlFor="receiveNotifications" className="font-bold">Enable notifications?</label>
            <Switch
              name="receiveNotifications"
              id="receiveNotifications"
              checked={notify}
              onChange={() => setNotify(!notify)}
            />
          </div>
          {notify && (
            <div className="flex items-center justify-between mt-4">
              <label htmlFor="timing" className="font-bold">Notification Timing</label>
              <select
                name="timing"
                id="timing"
                value={timing}
                onChange={(e) => setTiming(parseInt(e.target.value))}
                className="border rounded p-2 mt-2"
              >
                <option value={0}>Select timing</option>
                <option value={60}>1 hour before</option>
                <option value={60 * 24}>1 day before</option>
              </select>
            </div>
          )}
          <div className="flex justify-center mt-4">
            <button type="submit" className="py-2 px-11 bg-blue-500 text-white rounded-lg font-bold">Create Event</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateEvent;
