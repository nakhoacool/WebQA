import React, { useState } from 'react'
import TrashIcon from '@/components/icon/trash'
import { SidebarItemProps } from '@/lib/types'

export default function SidebarItem({
  item,
  handleSidebarItemClick,
  handleRemoveChatHistory,
  activeChatHistoryId,
}: SidebarItemProps) {
  const [isHovered, setIsHovered] = useState(false)
  const isActive = item.id === activeChatHistoryId

  return (
    <div
      key={item.id}
      className={`px-4 py-2 cursor-pointer flex justify-between items-center ${
        isActive || isHovered ? 'bg-gray-700' : ''
      }`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => handleSidebarItemClick(item.id)}
    >
      <p className='w-50 text-sm truncate'>{item.title}</p>
      {(isHovered || isActive) && (
        <TrashIcon
          className='h-5 w-5'
          onClick={(event) => {
            event.stopPropagation()
            handleRemoveChatHistory(item.id)
          }}
        />
      )}
    </div>
  )
}
