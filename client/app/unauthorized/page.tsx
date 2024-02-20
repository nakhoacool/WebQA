import LockIcon from '@/components/icon/lock'
import Link from 'next/link'
export default function UnauthorizedPage() {
  return (
    <div className='flex flex-col items-center justify-center w-full min-h-[400px] gap-2 text-center'>
      <div className='flex items-center justify-center rounded-full border border-gray-200 bg-gray-50 w-16 h-16 p-3 shadow-md dark:border-gray-800 dark:bg-gray-950'>
        <LockIcon className='w-10 h-10 text-gray-400 dark:text-gray-400' />
      </div>
      <div className='space-y-2'>
        <h1 className='text-3xl font-bold'>Unauthorized Access</h1>
        <p className='text-gray-500/60 dark:text-gray-400/60'>
          You do not have permission to access this page.
        </p>
      </div>
      <Link
        className='inline-flex h-10 items-center rounded-md border border-gray-200 bg-white px-8 text-sm font-medium shadow-sm transition-colors hover:bg-gray-100 hover:text-gray-900 dark:border-gray-800 dark:bg-gray-950 dark:hover:bg-gray-800 dark:hover:text-gray-50 dark:focus-visible:ring-gray-300'
        href='/'
      >
        Go back
      </Link>
    </div>
  )
}
