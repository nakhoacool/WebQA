import { JSX, SVGProps } from 'react'
function RobotIcon(props: JSX.IntrinsicAttributes & SVGProps<SVGSVGElement>) {
  return (
    <svg
      xmlns='http://www.w3.org/2000/svg'
      viewBox='0 0 640 512'
      fill='black'
      {...props}
    >
      <path d='M320 0c13.3 0 24 10.7 24 24V96H448c53 0 96 43 96 96V416c0 53-43 96-96 96H192c-53 0-96-43-96-96V192c0-53 43-96 96-96H296V24c0-13.3 10.7-24 24-24zM192 144c-26.5 0-48 21.5-48 48V416c0 26.5 21.5 48 48 48H448c26.5 0 48-21.5 48-48V192c0-26.5-21.5-48-48-48H320 192zM48 224H64V416H48c-26.5 0-48-21.5-48-48V272c0-26.5 21.5-48 48-48zm544 0c26.5 0 48 21.5 48 48v96c0 26.5-21.5 48-48 48H576V224h16zM208 384h32c8.8 0 16 7.2 16 16s-7.2 16-16 16H208c-8.8 0-16-7.2-16-16s7.2-16 16-16zm96 0h32c8.8 0 16 7.2 16 16s-7.2 16-16 16H304c-8.8 0-16-7.2-16-16s7.2-16 16-16zm96 0h32c8.8 0 16 7.2 16 16s-7.2 16-16 16H400c-8.8 0-16-7.2-16-16s7.2-16 16-16zM200 256a40 40 0 1 1 80 0 40 40 0 1 1 -80 0zm200-40a40 40 0 1 1 0 80 40 40 0 1 1 0-80z' />
    </svg>
  )
}

export default RobotIcon
