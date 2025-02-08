import { useState } from 'react'
import './App.css'
import { Button } from '@/components/ui/button'

function App() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [token, setToken] = useState('')

  const handleLogin = async (e) => {
    e.preventDefault()
    const response = await fetch('http://127.0.0.1:8000/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        username,
        password,
      }),
    })
    const data = await response.json()
    if (response.ok) {
      setToken(data.access_token)
      localStorage.setItem('token', data.access_token)
    } else {
      alert(data.detail)
    }
  }

  return (
    <div>
      <h1>Login</h1>
      <form onSubmit={handleLogin}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <Button className="mt-4" type="submit">
          Login
        </Button>
      </form>
      {token && <p>Logged in! Token: {token}</p>}
    </div>
  )
}

export default App
