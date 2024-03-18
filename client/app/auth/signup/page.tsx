import { redirect } from 'next/navigation'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/authOptions'
import SignUpForm from '@/components/component/signup-form'

export default async function SignUp() {
  const session = await getServerSession(authOptions)
  if (session) {
    redirect('/')
  }

  return <SignUpForm />
}
