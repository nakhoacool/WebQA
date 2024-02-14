import React, { useState } from 'react'
import TrashIcon from '@/components/icon/trash'
import { ChatHistory } from '@/lib/types'

interface SidebarItemProps {
  item: ChatHistory
  handleSidebarItemClick: (id: string) => void
  handleRemoveChatHistory: (id: string) => void
}

const SidebarItem: React.FC<SidebarItemProps> = ({
  item,
  handleSidebarItemClick,
  handleRemoveChatHistory,
}) => {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <div
      key={item.id}
      className='px-4 py-2 hover:bg-gray-700 cursor-pointer flex justify-between items-center'
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => handleSidebarItemClick(item.id)}
    >
      <p className='w-50 text-sm truncate'>{item.title}</p>
      {isHovered && (
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

export default SidebarItem
