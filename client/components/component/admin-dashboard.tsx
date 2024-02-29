'use client'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
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
  value: z.string().min(1, 'Cannot be empty'),
})

export default function AdminDashboardPage() {
  const router = useRouter()

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      value: '',
    },
  })
  function onSubmit(values: z.infer<typeof formSchema>) {
    // Do something with the form values
  }
  return (
    <div>
      <ToastContainer />
      <div className='flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8'>
        <div className='sm:mx-auto sm:w-full sm:max-w-sm'>
          <h2 className='mt-10 text-center text-2xl font-bold leading-9 tracking-tight text-white'>
            Dashboard
          </h2>
        </div>
        <div className='mt-5 sm:mx-auto sm:w-full sm:max-w-sm'>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className='space-y-6'>
              <FormField
                control={form.control}
                name='value'
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Content</FormLabel>
                    <FormControl>
                      <textarea
                        placeholder='Enter your content'
                        className='textarea h-12 block w-full rounded-md border-0 bg-white/5 py-1.5 text-white shadow-sm ring-1 ring-inset ring-white/10 focus:ring-2 focus:ring-inset focus:ring-indigo-500 sm:text-sm sm:leading-6'
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <button
                type='submit'
                className='btn w-full bg-indigo-500 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500'
              >
                Submit
              </button>
            </form>
          </Form>
          <p className='mt-5 text-center text-sm text-gray-400'>
            <button
              onClick={() => router.push('/')}
              className='font-semibold leading-6 text-indigo-400 hover:text-indigo-300'
            >
              Go back
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}
