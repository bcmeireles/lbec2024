import React, { useState } from 'react';
import Navbar from '../components/navbar/Navbar';
import waves from '../wickedbackground.svg';
import ConsumptionForm from '../components/ConsumptionForm';
import { State } from '../components/ConsumptionForm';

function AddData() {
  const [selectedForm, setSelectedForm] = useState<'Morning' | 'Afternoon' | 'Night'>('Morning');
  const [date, setDate] = useState<Date | null>(null);
  const [forms, setForms] = useState<Record<string, State>>({
    Morning: {
      gas: 0,
      electricity: 0,
      water: 0,
      temperature: 0,
      atHome: false,
      date: '',
      timeslot: 'Morning',
    },
    Afternoon: {
      gas: 0,
      electricity: 0,
      water: 0,
      temperature: 0,
      atHome: false,
      date: '',
      timeslot: 'Afternoon',
    },
    Night: {
      gas: 0,
      electricity: 0,
      water: 0,
      temperature: 0,
      atHome: false,
      date: '',
      timeslot: 'Night',
    },
  });

  const handleSubmitAll = () => {
    // Send 3 requests, one for each form
    console.log('Submitting all forms');
  };

  return (
    <div className="h-screen bg-white flex flex-col items-center justify-center px-6 relative">
      <img src={waves} alt="Waves" className="absolute bottom-0 left-0 w-full h-full" />
      <div className="z-10 relative w-full">
        <div className="flex justify-center my-4">
          {(['Morning', 'Afternoon', 'Night'] as ('Morning' | 'Afternoon' | 'Night')[]).map((formName) => (
            <button
              key={formName}
              className={`px-4 py-2 mr-2 text-gray-800 font-bold border-b-2 ${formName === selectedForm ? 'border-blue-500' : 'border-transparent'
                } focus:outline-none0`}
              onClick={() => setSelectedForm(formName)}
            >
              {formName.toUpperCase()}
            </button>
          ))}
        </div>
        <div className="flex flex-col items-center">
          {/* <ConsumptionForm onSubmit={(data) => handleFormSubmit(data, selectedForm)} /> */}
          <ConsumptionForm
          date={date}
          setDate={setDate}
          form={forms[selectedForm]}
          setForm={setForms}
          selectedForm={selectedForm}
        />
          <button onClick={handleSubmitAll} className="py-2 px-11 bg-blue-500 text-white rounded-lg mt-4 font-bold">Submit All</button>
        </div>
        <Navbar selected={3} />
      </div>
    </div>
  );
}

export default AddData;
