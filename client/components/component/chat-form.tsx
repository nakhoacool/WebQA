import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import * as z from 'zod'
import axios from 'axios'
import { Button } from '@/components/ui/button'
import { Form, FormControl, FormField, FormItem } from '@/components/ui/form'
import { Textarea } from '@/components/ui/textarea'
import IconSend from '@/components/icon/send'
import { ChatFormProps } from '@/lib/types'

const formSchema = z.object({
  chatMessage: z.string(),
})

export default function ChatForm(props: ChatFormProps) {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      chatMessage: '',
    },
  })

  function handleKeyDown(
    e: React.KeyboardEvent,
    field: any,
    form: any,
    onSubmit: Function
  ) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (field.value.trim().length > 0) {
        form.handleSubmit(onSubmit)()
      }
    }
  }

  function onSubmit(values: z.infer<typeof formSchema>) {
    const url = 'http://127.0.0.1:5000/qa'
    const data = {
      question: values.chatMessage,
      context: props.chatHistory,
    }
    props.onSubmit({
      role: 'user',
      content: values.chatMessage,
    })
    props.setIsTyping(true)
    axios
      .post(url, data, {
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        },
      })
      .then(({ data }) => {
        props.onSubmit({
          role: 'bot',
          content: data.answer,
        })
        props.setIsTyping(false)
      })
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
                      onKeyDown={(e) => handleKeyDown(e, field, form, onSubmit)}
                      placeholder='Enter your message...'
                      className='resize-none focus-visible:ring-offset-0 focus-visible:ring-0 pr-20'
                      disabled={props.isTyping}
                      {...field}
                    />
                  </FormControl>
                  <Button
                    type='submit'
                    className='absolute bottom-[10px] right-[10px]'
                    disabled={field.value.trim().length < 1}
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
