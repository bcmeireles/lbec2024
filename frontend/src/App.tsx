import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Register from './pages/auth/Register';
import Login from './pages/auth/Login';
import Overview from './pages/Overview';
import Calendar from './pages/Calendar';
import AddData from './pages/AddData';
import User from './pages/User';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<h1>Home Page</h1>} />
        <Route path="/overview" element={<Overview />} />
        <Route path="/calendar" element={<Calendar />} />
        <Route path="/adddata" element={<AddData />} />
        <Route path="/user" element={<User />} />
      </Routes>
    </Router>
  );
}

export default App;
