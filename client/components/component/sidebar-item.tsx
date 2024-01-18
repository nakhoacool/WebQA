import React, { useState, JSX, SVGProps } from 'react'
const SidebarItem = ({
  text,
  onRemove,
}: {
  text: string
  onRemove: () => void
}) => {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <div
      className='px-4 py-2 hover:bg-gray-700 cursor-pointer flex justify-between items-center'
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <p className='w-40 text-sm truncate'>{text}</p>
      {isHovered && <TrashIcon className='h-5 w-5' onClick={onRemove} />}
    </div>
  )
}

function TrashIcon(props: JSX.IntrinsicAttributes & SVGProps<SVGSVGElement>) {
  return (
    <svg
      xmlns='http://www.w3.org/2000/svg'
      viewBox='0 0 448 512'
      fill='white'
      {...props}
    >
      <path d='M164.2 39.5L148.9 64H299.1L283.8 39.5c-2.9-4.7-8.1-7.5-13.6-7.5H177.7c-5.5 0-10.6 2.8-13.6 7.5zM311 22.6L336.9 64H384h32 16c8.8 0 16 7.2 16 16s-7.2 16-16 16H416V432c0 44.2-35.8 80-80 80H112c-44.2 0-80-35.8-80-80V96H16C7.2 96 0 88.8 0 80s7.2-16 16-16H32 64h47.1L137 22.6C145.8 8.5 161.2 0 177.7 0h92.5c16.6 0 31.9 8.5 40.7 22.6zM64 96V432c0 26.5 21.5 48 48 48H336c26.5 0 48-21.5 48-48V96H64zm80 80V400c0 8.8-7.2 16-16 16s-16-7.2-16-16V176c0-8.8 7.2-16 16-16s16 7.2 16 16zm96 0V400c0 8.8-7.2 16-16 16s-16-7.2-16-16V176c0-8.8 7.2-16 16-16s16 7.2 16 16zm96 0V400c0 8.8-7.2 16-16 16s-16-7.2-16-16V176c0-8.8 7.2-16 16-16s16 7.2 16 16z' />
    </svg>
  )
}
export default SidebarItem
