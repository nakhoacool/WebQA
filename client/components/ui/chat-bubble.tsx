import React from 'react'
import { JSX, SVGProps } from 'react'

interface ChatBubbleProps {
  data: {
    id: string
    role: string
    content: string
  }
}

const ChatBubble: React.FC<ChatBubbleProps> = ({ data }) => (
  <div
    className={`p-4 flex ${
      data.role === 'bot' ? '' : 'text-right justify-end'
    }`}
  >
    {data.role === 'bot' && (
      <div className='rounded-full h-8 w-8 flex items-center justify-center mr-2'>
        <RobotIcon />
      </div>
    )}
    <div
      className={`rounded-lg ${
        data.role === 'bot' ? 'bg-gray-700' : 'bg-blue-600'
      } px-4 py-2 inline-block max-w-xs text-sm`}
    >
      {data.content}
    </div>
    {data.role === 'user' && (
      <div className='rounded-full h-8 w-8 flex items-center justify-center ml-2'>
        <UserIcon />
      </div>
    )}
  </div>
)

function RobotIcon(props: JSX.IntrinsicAttributes & SVGProps<SVGSVGElement>) {
  return (
    <svg
      xmlns='http://www.w3.org/2000/svg'
      viewBox='0 0 640 512'
      fill='white'
      {...props}
    >
      <path d='M320 0c13.3 0 24 10.7 24 24V96H448c53 0 96 43 96 96V416c0 53-43 96-96 96H192c-53 0-96-43-96-96V192c0-53 43-96 96-96H296V24c0-13.3 10.7-24 24-24zM192 144c-26.5 0-48 21.5-48 48V416c0 26.5 21.5 48 48 48H448c26.5 0 48-21.5 48-48V192c0-26.5-21.5-48-48-48H320 192zM48 224H64V416H48c-26.5 0-48-21.5-48-48V272c0-26.5 21.5-48 48-48zm544 0c26.5 0 48 21.5 48 48v96c0 26.5-21.5 48-48 48H576V224h16zM208 384h32c8.8 0 16 7.2 16 16s-7.2 16-16 16H208c-8.8 0-16-7.2-16-16s7.2-16 16-16zm96 0h32c8.8 0 16 7.2 16 16s-7.2 16-16 16H304c-8.8 0-16-7.2-16-16s7.2-16 16-16zm96 0h32c8.8 0 16 7.2 16 16s-7.2 16-16 16H400c-8.8 0-16-7.2-16-16s7.2-16 16-16zM200 256a40 40 0 1 1 80 0 40 40 0 1 1 -80 0zm200-40a40 40 0 1 1 0 80 40 40 0 1 1 0-80z' />
    </svg>
  )
}

function UserIcon(props: JSX.IntrinsicAttributes & SVGProps<SVGSVGElement>) {
  return (
    <svg
      xmlns='http://www.w3.org/2000/svg'
      viewBox='0 0 448 512'
      fill='white'
      {...props}
    >
      <path d='M320 128a96 96 0 1 0 -192 0 96 96 0 1 0 192 0zM96 128a128 128 0 1 1 256 0A128 128 0 1 1 96 128zM32 480H416c-1.2-79.7-66.2-144-146.3-144H178.3c-80 0-145 64.3-146.3 144zM0 482.3C0 383.8 79.8 304 178.3 304h91.4C368.2 304 448 383.8 448 482.3c0 16.4-13.3 29.7-29.7 29.7H29.7C13.3 512 0 498.7 0 482.3z' />
    </svg>
  )
}
export default ChatBubble
