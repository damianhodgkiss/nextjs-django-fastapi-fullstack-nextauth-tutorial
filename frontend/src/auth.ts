import NextAuth, { type User } from "next-auth";
import { CredentialsSignin } from '@auth/core/errors';
import CredentialsProvider from 'next-auth/providers/credentials';


export const { handlers, signIn, signOut, auth } = NextAuth({
  secret: process.env.NEXTAUTH_SECRET || "secret",
  providers: [
    CredentialsProvider({
      id: 'django',
      name: 'Django',
      credentials: {
        username: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        // Login to get token
        const response = await fetch(`${process.env.INTERNAL_API_URL}/users/login/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(credentials),
        });
        const json = await response.json();

        if (!response.ok) throw new CredentialsSignin(json.detail);

        return json;
      }
    })
  ],
  callbacks: {
    async jwt({ token, user, account }) {
      switch (account?.provider) {
        case 'django':
          // store the user's access token in the next-auth JWT
          const credentialUser = user as any;

          token.access_token = credentialUser?.access_token;
          token.token_type = credentialUser?.token_type;
          token.user = credentialUser?.user;
          break;
      }

      return token;
    },
    async session({ session, token }) {
      const accessToken = token?.access_token;
      const expireSession = {
        expires: new Date().toISOString(),
      };

      if (!accessToken) {
        return expireSession;
      }

      // check the API to see if the token is still valid
      const response = await fetch(`${process.env.INTERNAL_API_URL}/users/session/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
      });

      if (response.status !== 200) {
        return expireSession;
      }

      // if the token is still valid, return the new token
      const json = await response.json();

      return {
        ...session,
        access_token: json.access_token,
        token_type: json.token_type,
        user: json.user,
      };
    }
  }
})
