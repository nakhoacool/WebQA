import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { useSession } from 'next-auth/react'
import { useContext } from 'react'
import { ChatContext } from '@/contexts/ChatContext'
import * as z from 'zod'
import axios from 'axios'
import { Button } from '@/components/ui/button'
import { Form, FormControl, FormField, FormItem } from '@/components/ui/form'
import { Textarea } from '@/components/ui/textarea'
import IconSend from '@/components/icon/send'

const formSchema = z.object({
  chatMessage: z.string(),
})

export default function ChatForm() {
  const { data: session } = useSession()
  const context = useContext(ChatContext)

  if (!context) {
    throw new Error('useContext must be used within a ChatProvider')
  }

  const { isBotTyping, setIsBotTyping, handleFormSubmit, setAbortController } =
    context

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
    const url = 'http://158.178.243.160:5000/qa'
    const data = {
      question: values.chatMessage,
      userid: session?.user.id,
    }
    handleFormSubmit({
      role: 'user',
      content: values.chatMessage,
    })
    setIsBotTyping(true)
    const controller = new AbortController()
    setAbortController(controller)
    axios
      .post(url, data, {
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        },
        signal: controller.signal,
      })
      .then(({ data }) => {
        handleFormSubmit({
          role: 'bot',
          content: data.answer,
        })
        setIsBotTyping(false)
      })
      .catch(function (thrown) {
        if (axios.isCancel(thrown)) {
          console.log('Request canceled', thrown.message)
        } else {
          console.log(thrown)
        }
      })
    window.addEventListener('beforeunload', (e) => {
      controller.abort()
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
                      disabled={isBotTyping}
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
