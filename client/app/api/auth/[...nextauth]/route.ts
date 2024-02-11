import NextAuth from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import { signInWithEmailAndPassword } from 'firebase/auth'
import { auth } from '@/lib/firebase/config'

const handler = NextAuth({
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
          .catch((error) => console.log(error))
          .catch((error) => {
            const errorCode = error.code
            const errorMessage = error.message
            console.log(error)
          })
      },
    }),
  ],
})
export { handler as GET, handler as POST }
