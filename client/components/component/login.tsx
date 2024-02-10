import {
  CardTitle,
  CardDescription,
  CardHeader,
  CardContent,
  Card,
} from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import EyeIcon from '../icon/eye'
import LockIcon from '../icon/lock'

export function login() {
  return (
    <Card className='mx-auto max-w-sm overflow-hidden shadow-xl'>
      <CardHeader className='p-6'>
        <CardTitle className='text-3xl font-bold'>Login</CardTitle>
        <CardDescription>
          Enter your email below to login to your account
        </CardDescription>
      </CardHeader>
      <CardContent className='p-6'>
        <div className='space-y-4'>
          <div className='space-y-2'>
            <Label htmlFor='email'>Email</Label>
            <Input
              id='email'
              placeholder='m@example.com'
              required
              type='email'
            />
          </div>
          <div className='relative space-y-2'>
            <div className='flex items-center'>
              <Label htmlFor='password'>Password</Label>
              <Link className='ml-auto inline-block text-sm underline' href='#'>
                Forgot your password?
              </Link>
            </div>
            <Input id='password' required type='password' />
            <Button
              className='absolute bottom-1 right-1 h-7 w-7'
              size='icon'
              variant='ghost'
            >
              <EyeIcon className='h-4 w-4' />
              <span className='sr-only'>Toggle password visibility</span>
            </Button>
          </div>
          <Button className='w-full' type='submit'>
            <LockIcon className='mr-2 h-4 w-4' />
            Login
          </Button>
          <Button className='w-full' variant='outline'>
            Login with Google
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
