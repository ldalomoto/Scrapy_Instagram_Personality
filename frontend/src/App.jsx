import { useState } from 'react'
import './App.css'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/home'
import Infor from './components/information';

function App() {
  const [username, setUsername] = useState("")

  return (
    <>
      <Router>
        <Routes>
          <Route path="/" element={<Home username={username} setUsername={setUsername}/>} />
          <Route path="/infor/:username" element={<Infor />} />
        </Routes>
      </Router>
    </>
  )
}

export default App
