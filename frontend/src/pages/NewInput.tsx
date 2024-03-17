import React from 'react'
import Navbar from '../components/navbar/Navbar'
import waves from '../wickedbackground.svg'

interface Props {
  name: string;
}

function NewInput({ name }: Props) {
  return (
    <div className="h-screen bg-white flex flex-col items-center justify-center px-6 relative">
      <img src={waves} alt="Waves" className="absolute bottom-0 left-0 w-full h-full" />
      <div className="z-10 relative w-full">
        <Navbar selected={3}/>
        <div className="-mt-36">
          <h1 className="text-4xl font-bold text-center">Welcome, {name}</h1>
          <h2 className="text-3xl font-bold text-center mt-16">New Input</h2>
        </div>
        <div className="flex flex-col items-center mt-32 space-y-16">
          <button onClick={() => {window.location.href = "/adddata"}} className="w-64 py-7 px-11 bg-blue-500 text-white font-bold rounded-lg text-2xl">
            Manual Input
          </button>
          <button className="w-64 py-7 px-11 bg-blue-500 text-white font-bold rounded-lg text-2xl">
            Import
          </button>
        </div>
      </div>
    </div>
  )
}

export default NewInput
