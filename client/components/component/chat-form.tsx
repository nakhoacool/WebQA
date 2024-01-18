'use client'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import * as z from 'zod'
import axios from 'axios'
import { Button } from '@/components/ui/button'
import { Form, FormControl, FormField, FormItem } from '@/components/ui/form'
import { Textarea } from '@/components/ui/textarea'
import { JSX, SVGProps } from 'react'

type ChildProps = {
  onSubmit: (message: string) => void
}

const formSchema = z.object({
  chatMessage: z.string(),
})

export function ChatForm(props: ChildProps) {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      chatMessage: '',
    },
  })

  function onSubmit(values: z.infer<typeof formSchema>) {
    const url = 'http://127.0.0.1:5000/qa'
    const data = {
      question: values.chatMessage,
    }
    // axios
    //   .post(url, data, {
    //     headers: {
    //       Accept: 'application/json',
    //       'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    //     },
    //   })
    //   .then(({ data }) => {
    //     //props.onSubmit(data.answer);
    //     // props.onSubmit(values.chatMessage)
    //   })
    props.onSubmit(values.chatMessage)
    form.reset()
  }

  return (
    <Form {...form}>
      <div className='inp'>
        <form onSubmit={form.handleSubmit(onSubmit)}>
          <FormField
            control={form.control}
            name='chatMessage'
            render={({ field }) => (
              <FormItem>
                <div className='relative'>
                  <FormControl>
                    <Textarea
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          if (
                            field.value.length < 1 ||
                            (field.value.length < 2 && !e.shiftKey)
                          ) {
                            e.preventDefault()
                          } else {
                            form.handleSubmit(onSubmit)()
                            form.reset()
                          }
                        }
                      }}
                      placeholder='Enter your message...'
                      className='resize-none focus-visible:ring-offset-0 focus-visible:ring-0 pr-20'
                      {...field}
                    />
                  </FormControl>
                  <Button
                    type='submit'
                    className='absolute bottom-[10px] right-[10px]'
                    disabled={field.value.length < 2}
                  >
                    <IconSend className='text-white dark:text-black' />
                  </Button>
                </div>
              </FormItem>
            )}
          />
        </form>
      </div>
    </Form>
  )
}

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
