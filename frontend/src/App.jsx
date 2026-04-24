import { useState } from 'react'
import './App.css'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/home'
import Infor from './components/information';

function App() {
  const [username, setUsername] = useState("")
  const [numPosts, setNumPosts] = useState(5)
  const [numComments, setNumComments] = useState(5)

  return (
    <>
      <Router>
        <Routes>
          <Route path="/" element={<Home username={username} setUsername={setUsername} numPosts2={numPosts} setNumePosts={setNumPosts} numComments2={numComments} setNumeComments={setNumComments}/>} />
          <Route path="/infor/:username/:numPosts/:numComments" element={<Infor />} />
        </Routes>
      </Router>
    </>
  )
}

export default App
