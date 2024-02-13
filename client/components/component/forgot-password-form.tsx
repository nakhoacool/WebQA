'use client'
import { auth } from '@/lib/firebase/config'
import { sendPasswordResetEmail } from 'firebase/auth'
import { useRouter } from 'next/navigation'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Bounce, ToastContainer, toast } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'

const formSchema = z.object({
  email: z.string().min(1, 'Email is required').email('Invalid email'),
})

export default function ForgotPasswordForm() {
  const router = useRouter()

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: '',
    },
  })

  function onSubmit(values: z.infer<typeof formSchema>) {
    sendPasswordResetEmail(auth, values.email)
      .then(() => {
        toast.success('Password reset email sent', {
          position: 'top-right',
          autoClose: 3000,
          hideProgressBar: false,
          closeOnClick: false,
          pauseOnHover: true,
          draggable: false,
          progress: undefined,
          theme: 'light',
          transition: Bounce,
          onClose: () => router.replace('/auth/signin'),
        })
      })
      .catch((error) => {
        toast.error(error.message, {
          position: 'top-right',
          autoClose: 3000,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
          theme: 'light',
          transition: Bounce,
        })
      })
  }

  return (
    <div>
      <ToastContainer />
      <div className='flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8'>
        <div className='sm:mx-auto sm:w-full sm:max-w-sm'>
          <h2 className='mt-10 text-center text-2xl font-bold leading-9 tracking-tight text-white'>
            Forgot Password
          </h2>
        </div>

        <div className='mt-5 sm:mx-auto sm:w-full sm:max-w-sm'>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className='space-y-6'>
              <FormField
                control={form.control}
                name='email'
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <input
                        type='email'
                        autoComplete='email'
                        className='block w-full rounded-md border-0 bg-white/5 py-1.5 text-white shadow-sm ring-1 ring-inset ring-white/10 focus:ring-2 focus:ring-inset focus:ring-indigo-500 sm:text-sm sm:leading-6'
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <button
                type='submit'
                className='flex w-full justify-center rounded-md bg-indigo-500 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500'
              >
                Send Forgot Password Email
              </button>
            </form>
          </Form>
          <p className='mt-5 text-center text-sm text-gray-400'>
            Remember ?{' '}
            <button
              onClick={() => router.replace('/auth/signin')}
              className='font-semibold leading-6 text-indigo-400 hover:text-indigo-300'
            >
              Sign In
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}
