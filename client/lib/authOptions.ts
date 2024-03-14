import { AuthOptions, Session, User } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import { signInWithEmailAndPassword } from 'firebase/auth'
import { doc, getDoc } from 'firebase/firestore'
import { auth, db } from '@/lib/firebase/config'
import { JWT } from 'next-auth/jwt'
export const authOptions: AuthOptions = {
  pages: {
    signIn: '/auth/signin',
  },
  callbacks: {
    async jwt({ token, user }: { token: JWT; user: User }) {
      if (user) {
        token.id = user.id
        token.role = user.role
      }
      return token
    },
    async session({ session, token }: { session: Session; token: JWT }) {
      session.user.id = token.id
      session.user.role = token.role
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
        ).then(async (userCredential) => {
          if (userCredential) {
            const uid = userCredential.user.uid
            const email = userCredential.user.email
            const userRef = doc(db, 'thesis', uid)
            const userDoc = await getDoc(userRef)
            if (userDoc.exists()) {
              const role = userDoc.data().user_profile.role
              return {
                id: uid,
                email: email,
                role: role,
              }
            }
            return null
          }
          return null
        })
      },
    }),
  ],
}
