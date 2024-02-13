import NextAuth from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import { signInWithEmailAndPassword } from 'firebase/auth'
import { auth } from '@/lib/firebase/config'

export const authOptions = {
  pages: {
    signIn: '/auth/signin',
  },
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {},
      async authorize(credentials): Promise<any> {
        return await signInWithEmailAndPassword(
          auth,
          (credentials as any).email || '',
          (credentials as any).password || ''
        )
          .then((userCredential) => {
            if (userCredential.user) {
              // *TODO: Add role based access control here
              return userCredential.user
            }
            return null
          })
      },
    }),
  ],
}
export const handler = NextAuth(authOptions)
export { handler as GET, handler as POST }
