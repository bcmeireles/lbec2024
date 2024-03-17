import React, { useEffect, useState } from 'react'
import { Calendar, momentLocalizer } from 'react-big-calendar'
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import Navbar from '../../components/navbar/Navbar'
import waves from '../../wickedbackground.svg'
import CreateEvent from './CreateEvent';

const localizer = momentLocalizer(moment)

interface Event {
  _id: string;
  email: string;
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
        console.log("chegou aqui");

      //   {
      //     "data": [
      //         {
      //             "_id": "65f688737d328ab5ec350550",
      //             "email": "bcmeireles74@gmail.com",
      //             "end": "2024-03-17T16:15:00+00:00",
      //             "start": "2024-03-17T06:00:00+00:00",
      //             "title": "asdasdasd"
      //         }
      //     ],
      //     "status": "success",
      //     "success": true,
      //     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcxMDY1NTg3NCwianRpIjoiMzgzNTNmN2UtN2NiNC00NWFhLWE4YjQtYWQ1NzYwNGZlY2QwIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImJjbWVpcmVsZXM3NEBnbWFpbC5jb20iLCJuYmYiOjE3MTA2NTU4NzQsImNzcmYiOiIzNmMzMzE5ZC01YjMxLTQ3NGQtYjZmNy0yNjY2ZDY5NmM4YmQiLCJleHAiOjE3MTA2NTY3NzR9.VVC9RxLAka00FT_xaBBWs7KZu_1QkcuI97Vm9HlxIWA"
      // }

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
  
  })

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
        <Navbar selected={2}/>
      </div>
    </div>
  )
}

export default MyCalendar