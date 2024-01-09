import { Sidebar } from "@/components/component/sidebar"
export default function Home() {
  return (
    <div className="h-screen flex">
      <Sidebar />
      <div>
        Main
      </div>
    </div>
  )
}
