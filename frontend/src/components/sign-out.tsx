"use client";

import { signOut } from "next-auth/react";

export function SignOutButton() {
  return <button className="bg-blue-500 py-2 px-4 rounded text-white" onClick={() => signOut()}>Sign out</button>
}