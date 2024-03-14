import { redirect } from 'next/navigation'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/authOptions'
import SignInForm from '@/components/component/signin-form'

export default async function SignIn() {
  const session = await getServerSession(authOptions)
  if (session) {
    redirect('/')
  }

  return <SignInForm />
}
