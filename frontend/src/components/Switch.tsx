import React from 'react';

interface SwitchProps {
  name: string;
  id: string;
  checked: boolean;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const Switch: React.FC<SwitchProps> = ({ name, id, checked, onChange }) => {
  return (
    <div className="relative flex items-center">
      <input
        type="hidden"
        name={name}
        value={checked ? 'on' : 'off'}
        className="sr-only"
      />
      <div className="flex items-center">
        <input
          id={id}
          name={name}
          type="checkbox"
          checked={checked}
          onChange={onChange}
          className="absolute w-full h-full cursor-pointer opacity-0 peer"
        />
        <div className="w-12 h-7 bg-gray-300 rounded-full peer peer-checked:after:translate-x-[80%] peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-500"></div>
      </div>
    </div>
  );
};

export default Switch;
