import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import ParentPortal from './components/ParentPortal';
import Header from './components/Header';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <div className="container">
          <Routes>
            <Route path="/" element={<Register />} />
            <Route path="/dashboard/:id" element={<Dashboard />} />
            <Route path="/parent/:id" element={<ParentPortal />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
