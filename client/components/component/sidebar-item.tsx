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
      }`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => handleSidebarItemClick(item.id)}
    >
      <p className='w-36 text-sm truncate grow'>{item.title}</p>
      {(isHovered || isActive) && (
        <TrashIcon
          className='h-5 w-5'
          onClick={(event) => {
            event.stopPropagation()
            handleRemoveChatHistory(item.id)
          }}
        />
      )}
    </button>
  )
}
