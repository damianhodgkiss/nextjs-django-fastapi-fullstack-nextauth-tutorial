import { SignInButton } from "@/components/sign-in";
import { SignOutButton } from "@/components/sign-out";
import { auth } from "@/auth";
import { Sign } from "crypto";

export default async function Home() {
  const session = await auth();
  const { user } = session || {};
  const isSignedIn = !!user;

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      {
        isSignedIn ?
          <div>
            <pre>{JSON.stringify(session, null, 2)}</pre>
            <SignOutButton />
          </div>
          : <SignInButton />
      }
    </main>
  );
}
