import NextAuth from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import { signInWithEmailAndPassword } from 'firebase/auth'
import { auth } from '@/lib/firebase/config'

export const authOptions = {
  pages: {
    signIn: '/auth/signin',
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
      }
      return token
    },
    async session({ session, token }) {
      session.user.id = token.id
      return session
    },
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
        ).then((userCredential) => {
          if (userCredential) {
            // *TODO: Add role based access control here
            return {
              id: userCredential.user.uid,
              email: userCredential.user.email,
            }
          }
          return null
        })
      },
    }),
  ],
}
export const handler = NextAuth(authOptions)
export { handler as GET, handler as POST }
