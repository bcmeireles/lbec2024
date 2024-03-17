import React, { useEffect, useState } from 'react'
import { Calendar, momentLocalizer } from 'react-big-calendar'
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import Navbar from '../../components/navbar/Navbar'
import waves from '../../wickedbackground.svg'
import CreateEvent from './CreateEvent';

const localizer = momentLocalizer(moment)

interface Event {
  title: string;
  start: Date;
  end: Date;
}

function MyCalendar() {

  const [events, setEvents] = useState<Event[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/events', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();

        const events = data.data.map((event: Event) => {
          return {
            ...event,
            start: new Date(event.start),
            end: new Date(event.end)
          }
        });
        setEvents(events);
      }
    };

    fetchData();
  
  }, []);

  return (
    <div className="h-screen bg-white flex items-center justify-center px-6 relative">
      <img src={waves} alt="Waves" className="absolute bottom-0 left-0 w-full h-full" />
      <div className="z-10 relative">
        <Calendar
          localizer={localizer}
          events={events}
          startAccessor="start"
          endAccessor="end"
          style={{ height: 500 }}
          defaultView='day'
        />
        <div className="flex justify-center mb-10 mt-10">
          <button onClick={() => {window.location.href = "/createevent"}} className="py-2 px-11 bg-blue-500 text-white rounded-lg font-bold mb-10">Create Event</button>
        </div>
        <Navbar selected={2}/>
      </div>
    </div>
  )
}

export default MyCalendar