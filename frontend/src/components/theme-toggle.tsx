"use client"

import * as React from "react"
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { useEffect, useState } from "react"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useAuthStore } from "@/lib/store/auth"
import { toast } from "sonner"
import { authAPI } from "@/lib/api"

export function ThemeToggle() {
  const [mounted, setMounted] = useState(false)
  const { theme, setTheme } = useTheme()
  const { user, isAuthenticated, updateTheme } = useAuthStore()

  // Set initial theme based on authentication status
  useEffect(() => {
    setMounted(true)
    if (isAuthenticated && user?.theme_preference) {
      // For logged-in users, use their saved preference
      setTheme(user.theme_preference)
    } else if (!isAuthenticated && !localStorage.getItem('theme-guest')) {
      // Only set light theme for non-logged-in users if they haven't set a preference yet
      setTheme('light')
      localStorage.setItem('theme-guest', 'light')
    }
  }, [isAuthenticated, user?.theme_preference, setTheme])

  const handleThemeChange = async (newTheme: string) => {
    try {
      if (isAuthenticated) {
        // For logged-in users, update theme in database
        console.log('Updating theme preference:', { newTheme, isAuthenticated })
        const updatedUser = await authAPI.updateTheme(newTheme)
        console.log('Theme update response:', updatedUser)
        
        if (updatedUser) {
          setTheme(newTheme)
          updateTheme(newTheme)
          toast.success('Theme preference saved')
        }
      } else {
        // For non-logged-in users, just update the theme locally
        setTheme(newTheme)
        localStorage.setItem('theme-guest', newTheme)
      }
    } catch (error: any) {
      console.error('Theme update error:', {
        error,
        response: error.response?.data,
        status: error.response?.status,
        headers: error.response?.headers
      })
      
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to save theme preference'
      toast.error(errorMessage)
      
      // Revert the theme if the API call failed (only for logged-in users)
      if (isAuthenticated && user?.theme_preference) {
        setTheme(user.theme_preference)
      }
    }
  }

  if (!mounted) {
    return null
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon" aria-label="Toggle theme">
          {theme === 'dark' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => handleThemeChange('light')}>
          <Sun className="mr-2 h-4 w-4" /> Light
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleThemeChange('dark')}>
          <Moon className="mr-2 h-4 w-4" /> Dark
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
} 