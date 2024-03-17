import React, { useState } from 'react';
import moment from 'moment';
import 'react-datepicker/dist/react-datepicker.css';
import DatePicker from 'react-datepicker';
import Navbar from '../../components/navbar/Navbar';
import waves from '../../wickedbackground.svg';
import './CreateEvent.css';

interface Event {
  title: string;
  start: Date;
  end: Date;
}

const CreateEvent: React.FC = () => {
  const [title, setTitle] = useState('');
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);

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
          end: moment(endDate).format()
        })
      }).then((response) => {
        if (response.ok) {
          console.log("Form submitted successfully");
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
          <div className="flex justify-center mt-4">
            <button type="submit" className="py-2 px-11 bg-blue-500 text-white rounded-lg font-bold">Create Event</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateEvent;
