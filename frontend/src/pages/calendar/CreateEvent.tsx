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
  const [events, setEvents] = useState<Event[]>([]);

  const handleCreateEvent = () => {
    if (title && startDate && endDate) {
      setEvents([...events, { title, start: startDate, end: endDate }]);
      setTitle('');
      setStartDate(null);
      setEndDate(null);
    }
  };

  return (
    <div className="h-screen bg-white flex flex-col items-center justify-center px-6 relative">
      <img src={waves} alt="Waves" className="absolute bottom-0 left-0 w-full h-full" />
      <div className="z-10 relative w-full space-y-4">
        <Navbar selected={2} />
        <h1 className="text-3xl font-bold text-center mb-8">Create New Event</h1>
        <div className="bg-white border rounded-lg p-2 space-y-4">
          <input
            type="text"
            placeholder="Event title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <div className="datepicker-container space-y-4">
            <DatePicker
              selected={startDate}
              onChange={(date: Date) => setStartDate(date)}
              showTimeSelect
              timeFormat="HH:mm"
              timeIntervals={15}
              dateFormat="MMMM d, yyyy h:mm aa"
              placeholderText="Start date and time"
            />
            <DatePicker
              selected={endDate}
              onChange={(date: Date) => setEndDate(date)}
              showTimeSelect
              timeFormat="HH:mm"
              timeIntervals={15}
              dateFormat="MMMM d, yyyy h:mm aa"
              placeholderText="End date and time"
            />
          </div>
        </div>
        <div className="flex justify-center mt-8">
          <button onClick={handleCreateEvent} className="py-2 px-11 bg-blue-500 text-white rounded-lg font-bold">Create Event</button>
        </div>
      </div>
    </div>
  );
};

export default CreateEvent;