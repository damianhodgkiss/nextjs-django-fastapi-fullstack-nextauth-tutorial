import NextAuth from "next-auth";
import { JWT } from "next-auth/jwt"


declare module 'next-auth' {
  interface User {
    first_name: string;
    last_name?: string;
    is_staff: boolean;
    is_active: boolean;
    is_superuser: boolean;
    last_login: string;
    date_joined: string;
  }

  interface Session {
    user: User;
    access_token: string;
    token_type: 'Bearer';
  }

}

declare module 'next-auth/jwt' {
  interface JWT {
    user: User;
    access_token: string;
    token_type: 'Bearer';
  }
}