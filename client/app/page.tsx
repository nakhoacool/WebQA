import { Sidebar } from '@/components/component/sidebar'
import { ChatForm } from '@/components/component/chat-form'
export default function Home() {
  return (
    <div className='h-screen flex flex-row'>
      <Sidebar />
      <div className='main'>
        <div className='chats'>
          <div className='chat'>
            dawdawdawdwad
          </div>
        </div>
        <div className='chat-footer'>
          <ChatForm />
        </div>
      </div>
    </div>
  )
}
