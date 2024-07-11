"use client";

import { signIn } from "next-auth/react";

export function SignInButton() {
  return <button className="bg-blue-500 py-2 px-4 rounded text-white" onClick={() => signIn()}>Sign in</button>
}