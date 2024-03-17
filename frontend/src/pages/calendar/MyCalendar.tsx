import React, { useState } from 'react'
import { Calendar, momentLocalizer } from 'react-big-calendar'
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import Navbar from '../../components/navbar/Navbar'
import waves from '../../wickedbackground.svg'
import CreateEvent from './CreateEvent';

const localizer = momentLocalizer(moment)

const events = [
  {
    title: 'Event 1',
    start: moment().toDate(),
    end: moment().add(4, 'hours').toDate()
  },
  // more events...
];
interface Event {
  title: string;
  start: Date;
  end: Date;
}

function MyCalendar() {
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