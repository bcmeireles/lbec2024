import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Register from './pages/auth/Register';
import Login from './pages/auth/Login';
import Overview from './pages/Overview';
import Calendar from './pages/Calendar';
import AddData from './pages/AddData';
import User from './pages/User';
import NewInput from './pages/NewInput';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<h1>Home Page</h1>} />
        <Route path="/overview" element={<Overview />} />
        <Route path="/calendar" element={<Calendar />} />
        <Route path="/newinput" element={<NewInput name="Joaquim" />} />
        <Route path="/user" element={<User />} />
        <Route path="/adddata" element={<AddData />} />
      </Routes>
    </Router>
  );
}

export default App;
