export interface Message {
  role: string
  content: string
}

export interface ChatHistory {
  id: string
  title: string
  messages: Message[]
}

export interface ChatBubbleProps {
  data: {
    role: string
    content: string
  }
}

export interface ChatFormProps {
  onSubmit: (message: Message) => void
  setIsTyping: (isBotTyping: boolean) => void
  isTyping: boolean
  chatHistory: Message[]
}

export interface SidebarProps {
  session: any
  chatHistory: ChatHistory[]
  handleClearChat: () => void
  handleSidebarItemClick: (id: string) => void
  handleRemoveChatHistory: (id: string) => void
  activeChatHistoryId: string | null
}

export interface SidebarItemProps {
  item: ChatHistory
  handleSidebarItemClick: (id: string) => void
  handleRemoveChatHistory: (id: string) => void
  activeChatHistoryId: string | null
}
