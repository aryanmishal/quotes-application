"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"
import { type ThemeProviderProps } from "next-themes"
import { useAuthStore } from "@/lib/store/auth"
import { usePathname } from "next/navigation"

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  const [mounted, setMounted] = React.useState(false)
  const [storageKey, setStorageKey] = React.useState('theme-guest')
  const [isAuthPage, setIsAuthPage] = React.useState(false)
  const { user } = useAuthStore()
  const pathname = usePathname()

  // Handle mounting and initial setup
  React.useEffect(() => {
    setMounted(true)
    // Check if current page is login or register
    setIsAuthPage(pathname === "/login" || pathname === "/register")
    // Set storage key based on user
    setStorageKey(user ? `theme-${user.id}` : 'theme-guest')
  }, [pathname, user])

  // Don't render anything until mounted to prevent hydration mismatch
  if (!mounted) {
    return (
      <div style={{ visibility: 'hidden' }}>
        {children}
      </div>
    )
  }

  return (
    <NextThemesProvider 
      {...props} 
      attribute="class"
      defaultTheme="light"
      enableSystem={false}
      storageKey={storageKey}
      value={{
        light: "light",
        dark: "dark"
      }}
      forcedTheme={isAuthPage ? "light" : undefined}
    >
      {children}
    </NextThemesProvider>
  )
} 