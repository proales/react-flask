import { useState } from 'react'
import Loader from './Loader'
import './App.css'

function App() {
  const [query, setQuery] = useState('Fix camera in Subway store #102')
  const [message, setMessage] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isVisible, setIsVisible] = useState(true)

  const getMessage = async (e) => {
    e.preventDefault()
    if (isLoading) return
    setIsVisible(false);
    try {
      setIsLoading(true)
      const { message } = await fetch('/api/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query })
      }).then(r => r.json())
      setMessage(message)
    } catch(error) {
      console.log(error)
    } finally {
      // setQuery('')
      setIsLoading(false)
    }
  }
  
  return (
    <>
      <img src="logo.png"></img>
      <form className="card" onSubmit={getMessage}>
        <textarea 
          type="text" 
          cols="40" rows="20"
          value={query} 
          placeholder="Enter your ticket" 
          onChange={(e) => setQuery(e.target.value)} 
        />
        {isLoading && (
          <Loader />
        )}
       {message && (
         <textarea name="Text1" cols="40" rows="20">{message?.content}</textarea>
        )}
       {isVisible && (
         <button type="submit" disabled={isLoading}>
          Flow~
        </button>
        )}
      </form>
      {/* <pre className="read-the-docs">
        {isLoading ? (
          <Loader />
        ) : (
          <div>{message?.content}</div>
        )}
      </pre> */}
    </>
  )
}

export default App
