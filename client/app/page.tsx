import { Sidebar } from '@/components/component/sidebar'
export default function Home() {
  return (
    <div className='h-screen flex flex-row'>
      <Sidebar />
      <div>Main</div>
    </div>
  )
}
