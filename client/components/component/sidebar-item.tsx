import { useState } from 'react'
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
    <button
      key={item.id}
      className={`btn mb-2 flex justify-between items-center hover:bg-[#35255c] w-full ${
        isActive || isHovered ? 'bg-[#35255c]' : 'bg-[#1c1528]'
      } flex-nowrap`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => handleSidebarItemClick(item.id)}
    >
      <p className='text-sm truncate text-clip'>{item.title}</p>
      {(isHovered || isActive) && (
        <TrashIcon
          className='h-5 w-5 hover:text-red-500 transition-colors duration-200 ease-in-out flex-shrink-0'
          onClick={(event) => {
            event.stopPropagation()
            handleRemoveChatHistory(item.id)
          }}
        />
      )}
    </button>
  )
}
