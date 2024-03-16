import React from 'react'

import OverviewIcon from './assets/Icon1.svg'
import OverviewIconSelected from './assets/Icon1Selected.svg'
import CalendarIcon from './assets/Icon2.svg'
import CalendarIconSelected from './assets/Icon2Selected.svg'
import AddDataIcon from './assets/Icon3.svg'
import AddDataIconSelected from './assets/Icon3Selected.svg'
import UserIcon from './assets/Icon4.svg'
import UserIconSelected from './assets/Icon4Selected.svg'

function Navbar(props: { selected: number }) {
  const icons = [
    {
      name: 'Overview',
      icon: OverviewIcon,
      iconSelected: OverviewIconSelected,
      href: '/overview',
    },
    {
      name: 'Calendar',
      icon: CalendarIcon,
      iconSelected: CalendarIconSelected,
      href: '/calendar',
    },
    {
      name: 'Add Data',
      icon: AddDataIcon,
      iconSelected: AddDataIconSelected,
      href: '/adddata',
    },
    {
      name: 'User',
      icon: UserIcon,
      iconSelected: UserIconSelected,
      href: '/user',
    },
  ]

  const iconSize = 32

  return (
    <div className="fixed bottom-0 inset-x-0 bg-gray-200 bg-opacity-80 flex justify-around py-2">
      {icons.map(({ name, icon, iconSelected, href }, index) => (
        <div key={index} className="flex-1 flex flex-col items-center">
          <a href={href}>
            <div className="flex flex-col items-center" style={{ height: `${iconSize + 16}px` }}>
              <img
                src={props.selected === index + 1 ? iconSelected : icon}
                alt={name}
                className={`w-8 h-8 mb-1 ${props.selected === index + 1 ? 'text-blue-500' : 'text-gray-600'}`}
              />
              <p className={`text-xs font-bold ${props.selected === index + 1 ? 'text-[#1E40AF]' : 'text-gray-600'}`}>{name}</p>
            </div>
          </a>
        </div>
      ))}
    </div>
  )
}

export default Navbar
