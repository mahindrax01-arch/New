import { useState } from 'react'

const API = 'http://localhost:8000'

export default function App() {
  const [email, setEmail] = useState('demo@local.dev')
  const [token, setToken] = useState('')
  const [posts, setPosts] = useState([])
  const [text, setText] = useState('')

  const login = async () => {
    const res = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    })
    const data = await res.json()
    setToken(data.access_token)
  }

  const loadFeed = async () => {
    const res = await fetch(`${API}/feed`)
    setPosts(await res.json())
  }

  const createPost = async () => {
    await fetch(`${API}/feed`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ text })
    })
    setText('')
    loadFeed()
  }

  return (
    <main style={{ maxWidth: 640, margin: '2rem auto', fontFamily: 'sans-serif' }}>
      <h1>Social Media Starter</h1>
      <p>FastAPI + React feed, reactions, friends, websocket, token rotation, RBAC.</p>
      <div style={{ display: 'flex', gap: 8 }}>
        <input value={email} onChange={(e) => setEmail(e.target.value)} />
        <button onClick={login}>Login</button>
        <button onClick={loadFeed}>Load Feed</button>
      </div>
      <div style={{ marginTop: 16, display: 'flex', gap: 8 }}>
        <input value={text} onChange={(e) => setText(e.target.value)} placeholder="What's happening?" />
        <button onClick={createPost} disabled={!token || !text.trim()}>Post</button>
      </div>
      <ul>
        {posts.map((post) => (
          <li key={post.id}>
            {post.text} — ❤️ {post.reactions?.['❤️'] || 0}
          </li>
        ))}
      </ul>
    </main>
  )
}
