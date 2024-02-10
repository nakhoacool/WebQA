export interface Message {
  role: string
  content: string
}

export interface ChatHistory {
  id: string
  messages: Message[]
}
