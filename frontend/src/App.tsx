import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Register from './pages/auth/Register';
import Login from './pages/auth/Login';
import OverviewDay from './pages/OverviewDay';
import MyCalendar from './pages/calendar/MyCalendar';
import AddData from './pages/AddData';
import User from './pages/User';
import NewInput from './pages/NewInput';
import CreateEvent from './pages/calendar/CreateEvent';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<h1>Home Page</h1>} />
        <Route path="/overview" element={<OverviewDay />} />
        <Route path="/calendar" element={<MyCalendar />} />
        <Route path="/createevent" element={<CreateEvent />} />
        <Route path="/newinput" element={<NewInput />} />
        <Route path="/user" element={<User />} />
        <Route path="/adddata" element={<AddData />} />
      </Routes>
    </Router>
  );
}

export default App;
