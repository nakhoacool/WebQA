'use client'
import { AvatarImage, AvatarFallback, Avatar } from '@/components/ui/avatar'
import React, { useState, JSX, SVGProps } from 'react'
import SidebarItem from './sidebar-item'

type ChildProps = {
  onClearChat: () => void
}

export function Sidebar(props: ChildProps) {
  const [items, setItems] = useState([
    'Hello',
    'How are you',
    `Let's meet up later. Let's meet up later. Let's meet up later.
              Let's meet up later. Let's meet up later.`,
  ])
  const handleRemove = (indexToRemove: number) => {
    setItems(items.filter((_, index) => index !== indexToRemove))
  }

  return (
    <div className='flex flex-col w-64 border-r border-gray-700'>
      <div className='px-4 py-2 flex items-center justify-between border-b border-gray-700'>
        <h2 className='text-lg font-semibold'>New chat</h2>
        <button
          className='p-2 rounded-full hover:bg-gray-600 focus:outline-none focus:ring hover:scale-105 transition-transform duration-200 ease-in-out'
          onClick={props.onClearChat}
        >
          <PlusIcon className='text-white h-6 w-6' />
        </button>
      </div>
      <div className='overflow-y-auto'>
        {items.map((item, index) => (
          <SidebarItem
            key={index}
            text={item}
            onRemove={() => handleRemove(index)}
          />
        ))}
      </div>
      <div className='px-4 py-2 flex items-center space-x-2 border-t border-gray-700 mt-auto'>
        <Avatar>
          <AvatarImage alt='Guest' src='/placeholder.svg?height=32&width=32' />
          <AvatarFallback>G</AvatarFallback>
        </Avatar>
        <span className='text-sm'>Guest</span>
      </div>
    </div>
  )
}

function PlusIcon(props: JSX.IntrinsicAttributes & SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns='http://www.w3.org/2000/svg'
      width='24'
      height='24'
      viewBox='0 24'
      fill='none'
      stroke='currentColor'
      strokeWidth='2'
      strokeLinecap='round'
      strokeLinejoin='round'
    >
      <path d='M5 12h14' />
      <path d='M12 5v14' />
    </svg>
  )
}
