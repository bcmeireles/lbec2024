import React from 'react'
import Navbar from '../components/navbar/Navbar'
import waves from '../wickedbackground.svg'

function User() {
  return (
    <div className="h-screen bg-white flex items-center justify-center px-6 relative">
      <img src={waves} alt="Waves" className="absolute bottom-0 left-0 w-full h-full" />
      <div className="z-10 relative">
        <Navbar selected={4}/>
      </div>
    </div>
  )
}

export default User