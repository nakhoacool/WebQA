import { JSX, SVGProps } from 'react'

function IconSend(props: JSX.IntrinsicAttributes & SVGProps<SVGSVGElement>) {
  return (
    <svg width='24' height='24' viewBox='0 0 24 24' fill='none' {...props}>
      <path
        d='M7 11L12 6L17 11M12 18V7'
        stroke='currentColor'
        strokeWidth='2'
        strokeLinecap='round'
        strokeLinejoin='round'
      ></path>
    </svg>
  )
}

export default IconSend